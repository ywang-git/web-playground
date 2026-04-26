from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, Event, EventParticipant


class EntitySlugTests(TestCase):
    def test_slug_auto_populates(self):
        e = Entity.objects.create(name="Mick Jagger", kind=Entity.PERSON)
        self.assertEqual(e.slug, "mick-jagger")

    def test_slug_collision_resolved(self):
        Entity.objects.create(name="London", kind=Entity.PLACE)
        e2 = Entity.objects.create(name="London ", kind=Entity.PLACE)
        self.assertEqual(e2.slug, "london-2")


class EventModelTests(TestCase):
    def setUp(self):
        self.place = Entity.objects.create(name="Marquee Club", kind=Entity.PLACE)
        self.person = Entity.objects.create(name="Mick Jagger", kind=Entity.PERSON)

    def test_when_sort_key(self):
        e1 = Event.objects.create(
            title="Year only", description="d", when_year=1962,
            when_text="1962", source_kind=Event.WIKIPEDIA,
            source_url="https://example.com/a", source_snippet="x",
        )
        e2 = Event.objects.create(
            title="Full date", description="d",
            when_year=1962, when_month=7, when_day=12,
            when_text="12 July 1962", source_kind=Event.WIKIPEDIA,
            source_url="https://example.com/b", source_snippet="x",
        )
        self.assertLess(e1.when_sort_key, e2.when_sort_key)

    def test_place_must_be_kind_place(self):
        ev = Event(
            title="Bad place", description="d", when_year=1962, when_text="1962",
            place=self.person, source_kind=Event.WIKIPEDIA,
            source_url="https://example.com/c", source_snippet="x",
        )
        with self.assertRaises(ValidationError):
            ev.full_clean()

    def test_wikipedia_requires_url(self):
        ev = Event(
            title="No URL", description="d", when_year=1962, when_text="1962",
            source_kind=Event.WIKIPEDIA, source_snippet="x",
        )
        with self.assertRaises(ValidationError):
            ev.full_clean()

    def test_book_requires_citation(self):
        ev = Event(
            title="No citation", description="d", when_year=1962, when_text="1962",
            source_kind=Event.BOOK, source_snippet="x",
        )
        with self.assertRaises(ValidationError):
            ev.full_clean()


class APITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_rolling_stones", verbosity=0)

    def test_seed_idempotent(self):
        e1, ev1, p1 = (
            Entity.objects.count(),
            Event.objects.count(),
            EventParticipant.objects.count(),
        )
        call_command("seed_rolling_stones", verbosity=0)
        self.assertEqual(Entity.objects.count(), e1)
        self.assertEqual(Event.objects.count(), ev1)
        self.assertEqual(EventParticipant.objects.count(), p1)

    def test_graph_no_orphan_edges(self):
        resp = self.client.get(reverse("api_graph"))
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        node_ids = {n["id"] for n in payload["nodes"]}
        for edge in payload["edges"]:
            self.assertIn(edge["source"], node_ids)
            self.assertIn(edge["target"], node_ids)

    def test_events_endpoint_includes_solo_event(self):
        # Create an event with no participants — must still appear in the timeline
        Event.objects.create(
            title="Solo event", description="d", when_year=1980,
            when_text="1980", source_kind=Event.WIKIPEDIA,
            source_url="https://example.com/solo", source_snippet="x",
        )
        resp = self.client.get(reverse("api_events"))
        titles = {e["title"] for e in resp.json()["events"]}
        self.assertIn("Solo event", titles)

    def test_event_detail(self):
        ev = Event.objects.get(title="First Rolling Stones gig at the Marquee Club")
        resp = self.client.get(reverse("api_event_detail", args=[ev.pk]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["title"], ev.title)
        self.assertGreater(len(data["participants"]), 0)
        self.assertEqual(data["place"]["name"], "Marquee Club")
        self.assertEqual(data["source"]["kind"], Event.WIKIPEDIA)

    def test_entity_detail_page(self):
        resp = self.client.get(reverse("entity_detail", args=["mick-jagger"]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Mick Jagger")

    def test_entity_detail_page_404(self):
        resp = self.client.get(reverse("entity_detail", args=["does-not-exist"]))
        self.assertEqual(resp.status_code, 404)

    def test_api_entity_detail_lists_participation_and_place(self):
        # London is the place for many events; Mick Jagger participates in many
        resp = self.client.get(reverse("api_entity_detail", args=["mick-jagger"]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["entity"]["name"], "Mick Jagger")
        kinds = {ev["source"]["kind"] for ev in data["events"]}
        self.assertIn(Event.WIKIPEDIA, kinds)
        self.assertIn(Event.BOOK, kinds)

        # Place inclusion: London should list events held there even if it isn't a participant
        london_resp = self.client.get(reverse("api_entity_detail", args=["london"]))
        london_data = london_resp.json()
        london_titles = {ev["title"] for ev in london_data["events"]}
        self.assertIn("Charlie Watts joins The Rolling Stones", london_titles)

    def test_jagger_bowie_bridge(self):
        # The Jagger/Bowie collaboration must connect the two subgraphs
        ev = Event.objects.get(title__startswith="Jagger and Bowie record")
        names = set(ev.participants.values_list("name", flat=True))
        self.assertIn("Mick Jagger", names)
        self.assertIn("David Bowie", names)

    def test_home_renders(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="network-svg"')
        self.assertContains(resp, 'id="timeline-svg"')

"""Integration tests for the JSON API endpoints.

Exercise the full request → view → JSON payload path via Django's test client,
including URL routing and serialization.
"""

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import Event


class ApiSeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_rolling_stones", verbosity=0)


class GraphEndpointTests(ApiSeededTestCase):
    def test_status_and_shape(self):
        resp = self.client.get(reverse("api_graph"))
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn("nodes", payload)
        self.assertIn("edges", payload)
        self.assertGreater(len(payload["nodes"]), 0)
        self.assertGreater(len(payload["edges"]), 0)

    def test_edges_reference_only_declared_nodes(self):
        payload = self.client.get(reverse("api_graph")).json()
        node_ids = {n["id"] for n in payload["nodes"]}
        for edge in payload["edges"]:
            self.assertIn(edge["source"], node_ids, edge)
            self.assertIn(edge["target"], node_ids, edge)

    def test_nodes_have_expected_fields(self):
        payload = self.client.get(reverse("api_graph")).json()
        entities = [n for n in payload["nodes"] if n["type"] == "entity"]
        events = [n for n in payload["nodes"] if n["type"] == "event"]
        self.assertTrue(entities and events)
        for n in entities:
            self.assertIn("slug", n)
            self.assertIn("kind", n)
        for n in events:
            self.assertIn("event_id", n)
            self.assertIn("significance", n)


class EventsListEndpointTests(ApiSeededTestCase):
    def test_returns_all_events(self):
        resp = self.client.get(reverse("api_events"))
        self.assertEqual(resp.status_code, 200)
        events = resp.json()["events"]
        self.assertEqual(len(events), Event.objects.count())

    def test_includes_solo_events(self):
        Event.objects.create(
            title="Solo event", description="d", when_year=1980,
            when_text="1980", source_kind=Event.WIKIPEDIA,
            source_url="https://example.com/solo", source_snippet="x",
        )
        events = self.client.get(reverse("api_events")).json()["events"]
        self.assertIn("Solo event", {e["title"] for e in events})

    def test_each_event_has_source_block(self):
        events = self.client.get(reverse("api_events")).json()["events"]
        for e in events:
            self.assertIn("source", e)
            self.assertIn("kind", e["source"])
            self.assertIn("snippet", e["source"])


class EventDetailEndpointTests(ApiSeededTestCase):
    def test_returns_full_detail(self):
        ev = Event.objects.get(title="First Rolling Stones gig at the Marquee Club")
        resp = self.client.get(reverse("api_event_detail", args=[ev.pk]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["title"], ev.title)
        self.assertGreater(len(data["participants"]), 0)
        self.assertEqual(data["place"]["name"], "Marquee Club")
        self.assertEqual(data["source"]["kind"], Event.WIKIPEDIA)

    def test_404_for_unknown_pk(self):
        resp = self.client.get(reverse("api_event_detail", args=[999999]))
        self.assertEqual(resp.status_code, 404)

    def test_participants_carry_slug(self):
        ev = Event.objects.get(title="First Rolling Stones gig at the Marquee Club")
        data = self.client.get(reverse("api_event_detail", args=[ev.pk])).json()
        for p in data["participants"]:
            self.assertIn("slug", p)
            self.assertIn("name", p)


class EntityDetailEndpointTests(ApiSeededTestCase):
    def test_returns_events_participant_and_place(self):
        # London appears as PLACE for several events but as participant for none
        resp = self.client.get(reverse("api_entity_detail", args=["london"]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        titles = {e["title"] for e in data["events"]}
        self.assertIn("Charlie Watts joins The Rolling Stones", titles)

    def test_returns_multiple_source_kinds(self):
        data = self.client.get(reverse("api_entity_detail", args=["mick-jagger"])).json()
        kinds = {e["source"]["kind"] for e in data["events"]}
        self.assertIn(Event.WIKIPEDIA, kinds)
        self.assertIn(Event.BOOK, kinds)

    def test_focused_graph_includes_entity(self):
        data = self.client.get(reverse("api_entity_detail", args=["mick-jagger"])).json()
        self.assertIn("graph", data)
        slugs = {n.get("slug") for n in data["graph"]["nodes"] if n["type"] == "entity"}
        self.assertIn("mick-jagger", slugs)

    def test_404_for_unknown_slug(self):
        resp = self.client.get(reverse("api_entity_detail", args=["nobody"]))
        self.assertEqual(resp.status_code, 404)

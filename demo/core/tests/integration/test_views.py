"""Integration tests for the server-rendered HTML views."""

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class ViewSeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_rolling_stones", verbosity=0)


class HomeViewTests(ViewSeededTestCase):
    def test_home_renders_200(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)

    def test_home_contains_both_svg_containers(self):
        resp = self.client.get(reverse("home"))
        self.assertContains(resp, 'id="network-svg"')
        self.assertContains(resp, 'id="timeline-svg"')

    def test_home_wires_up_tabs(self):
        resp = self.client.get(reverse("home"))
        self.assertContains(resp, 'id="tab-network"')
        self.assertContains(resp, 'id="tab-timeline"')


class EntityDetailViewTests(ViewSeededTestCase):
    def test_renders_for_seeded_slug(self):
        resp = self.client.get(reverse("entity_detail", args=["mick-jagger"]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Mick Jagger")

    def test_404_for_unknown_slug(self):
        resp = self.client.get(reverse("entity_detail", args=["nobody-here"]))
        self.assertEqual(resp.status_code, 404)

    def test_kind_badge_shown(self):
        resp = self.client.get(reverse("entity_detail", args=["mick-jagger"]))
        self.assertContains(resp, "Person")

    def test_wikipedia_link_shown_when_present(self):
        resp = self.client.get(reverse("entity_detail", args=["mick-jagger"]))
        self.assertContains(resp, "wikipedia.org/wiki/Mick_Jagger")

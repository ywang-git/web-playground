"""Unit tests for the seed_rolling_stones management command."""

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity, Event, EventParticipant


class SeedCommandTests(TestCase):
    def test_seed_populates_expected_shape(self):
        call_command("seed_rolling_stones", verbosity=0)
        self.assertGreaterEqual(Entity.objects.count(), 15)
        self.assertGreaterEqual(Event.objects.count(), 15)
        self.assertGreater(EventParticipant.objects.count(), Event.objects.count())

    def test_seed_is_idempotent(self):
        call_command("seed_rolling_stones", verbosity=0)
        counts = (
            Entity.objects.count(),
            Event.objects.count(),
            EventParticipant.objects.count(),
        )
        call_command("seed_rolling_stones", verbosity=0)
        after = (
            Entity.objects.count(),
            Event.objects.count(),
            EventParticipant.objects.count(),
        )
        self.assertEqual(counts, after)

    def test_seed_all_source_kinds_represented(self):
        call_command("seed_rolling_stones", verbosity=0)
        kinds = set(Event.objects.values_list("source_kind", flat=True))
        self.assertIn(Event.WIKIPEDIA, kinds)
        self.assertIn(Event.BOOK, kinds)
        self.assertIn(Event.NOTE, kinds)

    def test_seed_all_significance_levels_represented(self):
        call_command("seed_rolling_stones", verbosity=0)
        levels = set(Event.objects.values_list("significance", flat=True))
        self.assertIn(Event.MAJOR, levels)
        self.assertIn(Event.NORMAL, levels)
        self.assertIn(Event.MINOR, levels)

    def test_jagger_bowie_bridge_event_present(self):
        """The seed must wire an event connecting the Stones and Bowie subgraphs."""
        call_command("seed_rolling_stones", verbosity=0)
        bridge = Event.objects.filter(title__startswith="Jagger and Bowie record").first()
        self.assertIsNotNone(bridge)
        names = set(bridge.participants.values_list("name", flat=True))
        self.assertIn("Mick Jagger", names)
        self.assertIn("David Bowie", names)

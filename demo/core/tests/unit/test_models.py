"""Unit tests for the core domain model.

Exercise model methods, validators and derived properties in isolation
(no HTTP client, no template rendering).
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import Entity, Event


class EntitySlugTests(TestCase):
    def test_slug_auto_populates(self):
        e = Entity.objects.create(name="Mick Jagger", kind=Entity.PERSON)
        self.assertEqual(e.slug, "mick-jagger")

    def test_slug_collision_resolved(self):
        Entity.objects.create(name="London", kind=Entity.PLACE)
        e2 = Entity.objects.create(name="London ", kind=Entity.PLACE)
        self.assertEqual(e2.slug, "london-2")

    def test_get_absolute_url_uses_slug(self):
        e = Entity.objects.create(name="David Bowie", kind=Entity.PERSON)
        self.assertEqual(e.get_absolute_url(), "/entity/david-bowie/")

    def test_explicit_slug_is_preserved(self):
        e = Entity.objects.create(name="Foo", slug="custom-slug", kind=Entity.OTHER)
        self.assertEqual(e.slug, "custom-slug")


class EventSortKeyTests(TestCase):
    def _mk(self, **overrides):
        defaults = dict(
            title="t", description="d", when_year=1962, when_text="1962",
            source_kind=Event.WIKIPEDIA, source_url="https://example.com/x",
            source_snippet="x",
        )
        defaults.update(overrides)
        return Event.objects.create(**defaults)

    def test_year_only_sorts_before_full_date_same_year(self):
        year_only = self._mk(title="year", when_year=1962)
        full_date = self._mk(title="full", when_year=1962, when_month=7, when_day=12)
        self.assertLess(year_only.when_sort_key, full_date.when_sort_key)

    def test_month_only_sorts_between(self):
        year_only = self._mk(title="a", when_year=1962)
        month_only = self._mk(title="b", when_year=1962, when_month=6)
        full_date = self._mk(title="c", when_year=1962, when_month=6, when_day=1)
        self.assertLess(year_only.when_sort_key, month_only.when_sort_key)
        self.assertLess(month_only.when_sort_key, full_date.when_sort_key)

    def test_earlier_year_sorts_first(self):
        earlier = self._mk(title="a", when_year=1962, when_month=12, when_day=31)
        later = self._mk(title="b", when_year=1963, when_month=1, when_day=1)
        self.assertLess(earlier.when_sort_key, later.when_sort_key)


class EventValidationTests(TestCase):
    def setUp(self):
        self.place = Entity.objects.create(name="Marquee Club", kind=Entity.PLACE)
        self.person = Entity.objects.create(name="Mick Jagger", kind=Entity.PERSON)

    def _event_kwargs(self, **overrides):
        base = dict(
            title="t", description="d", when_year=1962, when_text="1962",
            source_kind=Event.WIKIPEDIA, source_url="https://example.com/x",
            source_snippet="x",
        )
        base.update(overrides)
        return base

    def test_valid_event_passes_full_clean(self):
        ev = Event(**self._event_kwargs(place=self.place))
        ev.full_clean()  # no exception

    def test_place_must_be_kind_place(self):
        ev = Event(**self._event_kwargs(place=self.person))
        with self.assertRaises(ValidationError) as cm:
            ev.full_clean()
        self.assertIn("place", cm.exception.error_dict)

    def test_wikipedia_requires_source_url(self):
        ev = Event(**self._event_kwargs(source_kind=Event.WIKIPEDIA, source_url=""))
        with self.assertRaises(ValidationError) as cm:
            ev.full_clean()
        self.assertIn("source_url", cm.exception.error_dict)

    def test_web_requires_source_url(self):
        ev = Event(**self._event_kwargs(source_kind=Event.WEB, source_url=""))
        with self.assertRaises(ValidationError) as cm:
            ev.full_clean()
        self.assertIn("source_url", cm.exception.error_dict)

    def test_book_requires_citation(self):
        ev = Event(**self._event_kwargs(
            source_kind=Event.BOOK, source_url="", source_citation=""))
        with self.assertRaises(ValidationError) as cm:
            ev.full_clean()
        self.assertIn("source_citation", cm.exception.error_dict)

    def test_note_requires_citation(self):
        ev = Event(**self._event_kwargs(
            source_kind=Event.NOTE, source_url="", source_citation=""))
        with self.assertRaises(ValidationError) as cm:
            ev.full_clean()
        self.assertIn("source_citation", cm.exception.error_dict)

    def test_other_requires_neither(self):
        ev = Event(**self._event_kwargs(
            source_kind=Event.OTHER, source_url="", source_citation=""))
        ev.full_clean()  # no exception


class EntityStrTests(TestCase):
    def test_entity_str(self):
        self.assertEqual(str(Entity(name="X")), "X")

    def test_event_str_contains_when_text(self):
        ev = Event(title="Founding", when_year=1962, when_text="July 1962",
                   description="d", source_snippet="x")
        self.assertIn("July 1962", str(ev))

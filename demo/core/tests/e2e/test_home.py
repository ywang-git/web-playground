"""End-to-end browser tests for the home (network + timeline) page."""

from .base import PlaywrightTestCase


class HomePageE2ETests(PlaywrightTestCase):
    def _open_home(self):
        self.page.goto(self.url("/"))
        self.page.wait_for_selector("#network-svg circle.node-entity")

    def test_network_renders_entity_and_event_nodes(self):
        self._open_home()
        self.assertGreater(self.page.locator("#network-svg circle.node-entity").count(), 5)
        self.assertGreater(self.page.locator("#network-svg rect.node-event").count(), 5)

    def test_timeline_tab_reveals_markers(self):
        self._open_home()
        self.page.click("#tab-timeline")
        self.page.wait_for_selector("#timeline-svg .marker")
        self.assertGreater(self.page.locator("#timeline-svg .marker circle").count(), 5)
        # network SVG must actually be hidden (the specificity-fix regression case)
        self.assertTrue(self.page.locator("#network-svg").evaluate(
            "el => getComputedStyle(el).display === 'none'"
        ))

    def test_clicking_event_populates_side_panel(self):
        self._open_home()
        # Wait for simulation to settle enough that at least one event node is stable.
        first_event = self.page.locator("#network-svg rect.node-event").first
        first_event.click()
        # Panel should switch out of the placeholder and render a source badge.
        self.page.wait_for_selector("#panel .source-badge")
        self.assertGreater(self.page.locator("#panel h2").count(), 0)
        self.assertGreater(self.page.locator("#panel .chip").count(), 0)

    def test_clicking_entity_navigates_to_detail_page(self):
        self._open_home()
        first_entity = self.page.locator("#network-svg circle.node-entity").first
        with self.page.expect_navigation():
            first_entity.click()
        self.assertRegex(self.page.url, r"/entity/[^/]+/$")

    def test_deep_link_event_param_opens_panel(self):
        # Load home with ?event=<id>; panel should populate before any click
        from core.models import Event
        ev = Event.objects.first()
        self.page.goto(self.url(f"/?event={ev.pk}"))
        self.page.wait_for_selector("#panel .source-badge")
        self.assertIn(ev.title, self.page.locator("#panel").inner_text())

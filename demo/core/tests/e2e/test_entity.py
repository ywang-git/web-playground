"""End-to-end browser tests for the per-entity detail page."""

from .base import PlaywrightTestCase


class EntityDetailE2ETests(PlaywrightTestCase):
    def test_entity_page_renders_header_and_event_cards(self):
        self.page.goto(self.url("/entity/mick-jagger/"))
        self.page.wait_for_selector(".event-card")
        self.assertIn("Mick Jagger", self.page.locator("header").inner_text())
        self.assertGreater(self.page.locator(".event-card").count(), 3)

    def test_focused_graph_renders_center_entity(self):
        self.page.goto(self.url("/entity/mick-jagger/"))
        self.page.wait_for_selector("#entity-graph-svg circle.center")
        self.assertEqual(self.page.locator("#entity-graph-svg circle.center").count(), 1)

    def test_source_badge_visible_for_book_source(self):
        # Jagger has BOOK-sourced events in the seed
        self.page.goto(self.url("/entity/mick-jagger/"))
        self.page.wait_for_selector(".event-card .source-badge")
        # Assert the BOOK-classed badge exists (class is source-of-truth; visible
        # text is uppercased by CSS text-transform).
        self.assertGreater(
            self.page.locator(".event-card .source-badge.BOOK").count(), 0
        )

    def test_clicking_related_entity_chip_navigates(self):
        self.page.goto(self.url("/entity/mick-jagger/"))
        self.page.wait_for_selector(".event-card .chip")
        # Click a chip that is NOT the self chip (self chips carry class 'self')
        other_chip = self.page.locator(".event-card a.chip:not(.self)").first
        with self.page.expect_navigation():
            other_chip.click()
        self.assertRegex(self.page.url, r"/entity/[^/]+/$")
        self.assertNotIn("/entity/mick-jagger/", self.page.url)

    def test_back_link_returns_home(self):
        self.page.goto(self.url("/entity/mick-jagger/"))
        with self.page.expect_navigation():
            self.page.click("header a.back")
        self.assertTrue(self.page.url.rstrip("/").endswith(self.live_server_url.rstrip("/")))

"""Shared Playwright + LiveServerTestCase harness for browser tests."""

import os
# Playwright's sync API runs on a greenlet that Django detects as an async
# context. The ORM refuses sync operations there unless this flag is set.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

import unittest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:  # pragma: no cover - dev-only dependency
    PLAYWRIGHT_AVAILABLE = False


def _resolve_chromium_executable():
    """Return the pre-installed chromium path if present, else None.

    The remote execution environment ships a Chromium build at
    /opt/pw-browsers/chromium that must be passed explicitly to launch(),
    because the installed playwright version's default expected build id
    won't match. On dev machines with `playwright install` chromium, leave
    executable_path unset so Playwright picks its default.
    """
    explicit = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if explicit and os.path.exists(explicit):
        return explicit
    fallback = "/opt/pw-browsers/chromium"
    if os.path.exists(fallback):
        return fallback
    return None


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "playwright not installed")
class PlaywrightTestCase(StaticLiveServerTestCase):
    """Base class: one Chromium instance per test class, one page per test.

    Reseeds the database in setUp() because LiveServerTestCase extends
    TransactionTestCase, which flushes tables between tests.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._pw = sync_playwright().start()
        launch_kwargs = {"headless": True}
        exe = _resolve_chromium_executable()
        if exe:
            launch_kwargs["executable_path"] = exe
        cls.browser = cls._pw.chromium.launch(**launch_kwargs)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.browser.close()
        finally:
            cls._pw.stop()
            super().tearDownClass()

    def setUp(self):
        super().setUp()
        call_command("seed_rolling_stones", verbosity=0)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        try:
            self.context.close()
        finally:
            super().tearDown()

    def url(self, path=""):
        if path.startswith("/"):
            path = path[1:]
        return f"{self.live_server_url}/{path}"

from contextlib import suppress
from playwright.sync_api import sync_playwright

"""
Opens Playwright, launches a chromium browser, creates a browser context and page, and provides cleanup.
It exposes the page object as 's.page' inside a 'with' block.
"""
class BrowserSession:

    def __init__(self, headless: bool = True, timeout_ms: int = 15000):
        # Run chromium without a visible window if True
        self.headless = headless
        # Timeout for waits and actions
        self.timeout_ms = timeout_ms
        # Playwright driver
        self._p = None
        # Browser instance
        self.browser = None
        # Browser context
        self.context = None
        # Page used by callers
        self.page = None

    def __enter__(self):
        # Start Playwright driver
        self._p = sync_playwright().start()
        # Open chromium with the requested mode
        self.browser = self._p.chromium.launch(headless=self.headless)
        # Create a fresh context (no cached cookies/storage)
        self.context = self.browser.new_context()
        # Open one page for this session
        self.page = self.context.new_page()
        # Timeout to page related operations
        self.page.set_default_timeout(self.timeout_ms)
        return self

    def __exit__(self, exc_type, exc, tb):
        with suppress(Exception):
            if self.context: self.context.close()
        with suppress(Exception):
            if self.browser: self.browser.close()
        with suppress(Exception):
            if self._p: self._p.stop()
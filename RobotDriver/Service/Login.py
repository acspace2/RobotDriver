import re
from playwright.sync_api import Page
from RobotDriver.Site.Base import SiteAdapter

"""
Encapsulates the authentication flow for a shopping site.
"""
class AuthService:
    def __init__(self, adapter: SiteAdapter, page: Page):
        self.adapter = adapter
        self.page = page

    def login(self, email: str, password: str, auto_signup: bool = False) -> bool:
        # First login attempt
        ok = self.adapter.login(self.page, email, password)
        if ok:
            return True
        # If not successful, try auto signing-up and logging in
        if not auto_signup:
            err = self.page.locator(".login-form p, .alert-danger, [data-qa*='error']").first
            if err.count():
                print("[DEBUG] login error banner:", err.inner_text().strip())
            return False
        print("[INFO] Login failed; trying sign-up…")
        if not self.adapter.signup(self.page, email, password, name="Test User"):
            return False

        # Login in again as some sites are not auto logged-in after sign-up
        self.adapter.ensure_login_page(self.page)
        return self.adapter.login(self.page, email, password)
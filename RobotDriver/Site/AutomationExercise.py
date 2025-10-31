import re
from urllib.parse import urljoin
from contextlib import suppress
from playwright.sync_api import Page, TimeoutError as PWTimeout
from .Base import SiteAdapter
from RobotDriver.Util.Parsing import extract_price_from_scope

BASE_URL   = "https://automationexercise.com"
LOGIN_PATH = "/login"

# Use selectors that are shown by the site, preferably data-qa to reduce risk of class/text being changed
SELECTOR = {
    "email":  'input[data-qa="login-email"]',
    "pass":   'input[data-qa="login-password"]',
    "submit": 'button[data-qa="login-button"]',
    "search_input": "#search_product",
    "search_btn":   "#submit_search",
    "cards":        ".productinfo.text-center",
}

"""
Encapsulates all selectors from the site and navigation sites.
"""
class AutomationExerciseAdapter(SiteAdapter):
    def goto_home(self, page: Page) -> None:
        page.goto(BASE_URL, wait_until="domcontentloaded")

    def ensure_login_page(self, page: Page) -> None:
        # Check if the page has a login form
        if page.locator(SELECTOR["email"]).count():
            return
        # Try going to login page using general links
        for sel in ('a[href="/login"]', 'a:has-text("Signup / Login")'):
            loc = page.locator(sel).first
            if loc.count():
                loc.click()
                try:
                    page.wait_for_selector(SELECTOR["email"], timeout=5000)
                    return
                except PWTimeout:
                    # Try next one
                    pass
        # Go to login path
        page.goto(urljoin(BASE_URL, LOGIN_PATH), wait_until="domcontentloaded")
        page.wait_for_selector(SELECTOR["email"])

    """
    Try to authenticate with given credentials.
    """
    def login(self, page: Page, email: str, password: str) -> bool:
        self.ensure_login_page(page)
        page.fill(SELECTOR["email"], email)
        page.fill(SELECTOR["pass"], password)
        page.click(SELECTOR["submit"])
        page.wait_for_load_state("domcontentloaded")
        return page.get_by_role("link", name=re.compile(r"logout", re.I)).first.count() > 0

    """
    Create a new account.
    """
    def signup(self, page: Page, email: str, password: str, name: str) -> bool:
        self.ensure_login_page(page)
        # Sign-up form
        try:
            page.fill('input[data-qa="signup-name"]', name)
            page.fill('input[data-qa="signup-email"]', email)
            page.click('button[data-qa="signup-button"]')
            page.wait_for_load_state("domcontentloaded")
        except Exception:
            return False
        # Registration form
        try:
            with suppress(Exception):
                page.check('input#id_gender1', force=True)
            page.fill('input[data-qa="password"]', password)
            page.select_option('select[data-qa="days"]', "1")
            page.select_option('select[data-qa="months"]', "1")
            page.select_option('select[data-qa="years"]', "1990")
            page.fill('input[data-qa="first_name"]', "Test")
            page.fill('input[data-qa="last_name"]', "User")
            page.fill('input[data-qa="address"]', "123 Test Street")
            page.select_option('select[data-qa="country"]', label="United States")
            page.fill('input[data-qa="state"]', "CA")
            page.fill('input[data-qa="city"]', "LA")
            page.fill('input[data-qa="zipcode"]', "90001")
            page.fill('input[data-qa="mobile_number"]', "+15555555555")
            page.click('button[data-qa="create-account"]')
            page.wait_for_load_state("domcontentloaded")
        except Exception:
            return False
        # To click 'Continue' if one pops up after creating an account
        cont = page.get_by_role("link", name=re.compile("continue", re.I)).first
        if cont.count():
            with suppress(Exception):
                cont.click()
            page.wait_for_load_state("domcontentloaded")
            return True
        return False

    """
    Search for a product and its price
    """
    def search_and_price(self, page: Page, product_name: str) -> tuple[bool, str|None]:
        page.goto(f"{BASE_URL}/products", wait_until="domcontentloaded")
        page.fill(SELECTOR["search_input"], product_name)
        page.click(SELECTOR["search_btn"])
        page.wait_for_selector(".features_items", state="visible")

        # Finding one that contains the product name
        card = page.locator(SELECTOR["cards"]).filter(
            has_text=re.compile(re.escape(product_name), re.I)
        ).first

        if card.count():
            # Try to parse the price from the card
            price = extract_price_from_scope(card)
            # Open detailed page if price can't be found initially
            if not price:
                with suppress(Exception):
                    card.get_by_role("link", name=re.compile("view product", re.I)).first.click()
                    page.wait_for_load_state("domcontentloaded")
                    price = extract_price_from_scope(page)
            return True, price

        # Try link to go to detailed page if above doesn't work
        link = page.get_by_role("link", name=re.compile(re.escape(product_name), re.I)).first
        if link.count():
            link.click()
            page.wait_for_load_state("domcontentloaded")
            return True, extract_price_from_scope(page)

        return False, None
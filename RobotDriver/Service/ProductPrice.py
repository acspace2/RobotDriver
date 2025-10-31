from playwright.sync_api import Page
from RobotDriver.Site.Base import SiteAdapter

"""
Encapsulates product search and price extraction.
"""
class CatalogService:
    def __init__(self, adapter: SiteAdapter, page: Page):
        self.adapter = adapter
        self.page = page

    """
    Search for a product and extract price.
    True for found if a product and its page is found.
    Price text e.g., "Rs. 500" if visible, otherwise, None.
    """
    def price_for(self, product_name: str) -> tuple[bool, str|None]:
        return self.adapter.search_and_price(self.page, product_name)
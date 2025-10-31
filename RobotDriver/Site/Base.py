from abc import ABC, abstractmethod
from playwright.sync_api import Page

"""
Strategy interface that encapsulates site-specific actions.
"""
class SiteAdapter(ABC):
    """
    Navigate to the site home and wait for DOM readiness.
    """
    @abstractmethod
    def goto_home(self, page: Page) -> None:...
    """
    Ensure the login form is visible (navigate/redirect if needed).
    """
    @abstractmethod
    def ensure_login_page(self, page: Page) -> None:...
    """
    Attempt login. Return True if the session is authenticated.
    """
    @abstractmethod
    def login(self, page: Page, email: str, password: str) -> bool:...
    """
    Optionally create a new account.
    """
    def signup(self, page: Page, email: str, password: str, name: str) -> bool:
        return False
    """
    Find a product by name and extract its price.
    """
    @abstractmethod
    def search_and_price(self, page: Page, product_name: str) -> tuple[bool, str|None]: ...
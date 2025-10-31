from abc import ABC, abstractmethod
from playwright.sync_api import Page

class SiteAdapter(ABC):
    """사이트별 동작(셀렉터/흐름)을 캡슐화하는 인터페이스"""

    @abstractmethod
    def goto_home(self, page: Page) -> None: ...
    @abstractmethod
    def ensure_login_page(self, page: Page) -> None: ...
    @abstractmethod
    def login(self, page: Page, email: str, password: str) -> bool: ...
    def signup(self, page: Page, email: str, password: str, name: str) -> bool:
        """필요 시 구현(기본: 미지원)"""
        return False
    @abstractmethod
    def search_and_price(self, page: Page, product_name: str) -> tuple[bool, str|None]:
        """(found, price) 반환"""
        ...
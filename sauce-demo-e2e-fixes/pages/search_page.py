from __future__ import annotations

from playwright.sync_api import Locator, Response

from pages.base_page import BasePage
from utils.helpers import goto_with_retry


class SearchPage(BasePage):
    path = "/search"

    @property
    def search_input(self) -> Locator:
        return self.page.locator("input[name='q']:visible").first

    def open_with_query(self, term: str) -> Response | None:
        return goto_with_retry(self.page, f"/search?q={term}", wait_until="domcontentloaded")

    def search(self, term: str) -> None:
        self.search_input.fill(term)
        self.search_input.press("Enter")
        self.page.wait_for_url("**/search?**q=**")

    def wait_for_results(self) -> None:
        """Wait until at least one product link is rendered on the results page."""
        self.page.locator("a[href*='/products/']").first.wait_for(state="attached")

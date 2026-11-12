from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, Response

import time

from pages.base_page import BasePage
from utils.helpers import recover_from_checkpoint


class ProductPage(BasePage):
    def __init__(self, page: Page, handle: str) -> None:
        super().__init__(page)
        self.handle = handle
        self.path = f"/products/{handle}"

    # The logo is also an <h1>, so exclude headings that wrap an image.
    @property
    def heading(self) -> Locator:
        return self.page.locator("h1:not(:has(img))").first

    @property
    def price(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*£\d+\.\d{2}\s*$")).first

    @property
    def description(self) -> Locator:
        return self.page.get_by_text(re.compile("This area is populated by the product description"))

    @property
    def main_image(self) -> Locator:
        return self.page.locator("img[src*='/cdn/shop/products/']").first

    @property
    def add_button(self) -> Locator:
        return self.page.locator("form[action*='/cart/add'] [type='submit'], [name='add']").first

    @property
    def quantity_input(self) -> Locator:
        return self.page.locator("form[action*='/cart/add'] input[name='quantity']")

    @property
    def related_section(self) -> Locator:
        return self.page.get_by_text("You Might Also Like")

    def related_handles(self) -> list[str]:
        return [h for h in self.product_handles() if h != self.handle]

    def add_to_cart(self, quantity: int = 1) -> None:
        """Click 'Add to cart' and wait for the cart request (works for AJAX and native form posts).
        Retries when Shopify rate-limits the request (HTTP 429)."""
        recover_from_checkpoint(self.page)
        for attempt in range(4):
            if quantity != 1 and self.quantity_input.count():
                self.quantity_input.first.fill(str(quantity))
            with self.page.expect_response(
                lambda r: "/cart/add" in r.url and r.request.method == "POST"
            ) as response_info:
                self.add_button.click()
            self.page.wait_for_load_state("domcontentloaded")
            if response_info.value.status != 429:
                return
            time.sleep(min(5 * 2**attempt, 30))
            self.open()  # reload a clean product page, then try again
        recover_from_checkpoint(self.page)

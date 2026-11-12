from __future__ import annotations

import re

from playwright.sync_api import Locator

from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart"

    # NOTE: the header contains a hidden mini-cart with duplicate links/buttons,
    # so every locator below is restricted to visible elements.
    @property
    def quantity_inputs(self) -> Locator:
        return self.page.locator("input[name^='updates']:visible")

    @property
    def update_button(self) -> Locator:
        return self.page.locator("[name='update']:visible")

    @property
    def checkout_button(self) -> Locator:
        return self.page.locator(
            "[name='checkout']:visible, input[value='Check Out']:visible, "
            "button:has-text('Check Out'):visible"
        ).first

    def line_count(self) -> int:
        return self.quantity_inputs.count()

    def is_empty(self) -> bool:
        return self.line_count() == 0

    def item_link(self, title: str) -> Locator:
        return self.page.locator("a[href*='/products/']:visible").filter(has_text=title).first

    def quantity(self, index: int = 0) -> int:
        return int(self.quantity_inputs.nth(index).input_value())

    def set_quantity(self, index: int, quantity: int) -> None:
        field = self.quantity_inputs.nth(index)
        field.fill(str(quantity))
        if self.update_button.count():
            with self.page.expect_navigation(wait_until="domcontentloaded"):
                self.update_button.first.click()
        else:  # theme auto-updates on change
            field.blur()
            self.page.wait_for_load_state("networkidle")

    def remove_item(self, index: int = 0) -> None:
        self.set_quantity(index, 0)

    def shows_amount(self, amount: str) -> Locator:
        """Visible text like '£105.00' (line price or subtotal)."""
        pattern = re.escape(f"£{amount}")
        return self.page.locator(f"text=/{pattern}/ >> visible=true").first

    def checkout(self) -> None:
        self.checkout_button.click()

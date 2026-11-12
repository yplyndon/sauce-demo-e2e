from __future__ import annotations

import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.product_page import ProductPage
from utils.helpers import recover_from_checkpoint


class HomePage(BasePage):
    path = "/"

    def open_product(self, handle: str, title: str | None = None) -> ProductPage:
        self.product_card(handle, title).click()
        expect(self.page).to_have_url(re.compile(rf"/products/{re.escape(handle)}"))
        recover_from_checkpoint(self.page)
        return ProductPage(self.page, handle)

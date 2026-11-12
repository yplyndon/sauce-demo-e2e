from __future__ import annotations

import re

from playwright.sync_api import Locator

from pages.base_page import BasePage
from utils.helpers import recover_from_checkpoint


class RegisterPage(BasePage):
    path = "/account/register"

    @property
    def form(self) -> Locator:
        return self.page.locator("form[action$='/account']").first

    def field(self, name: str) -> Locator:
        return self.form.locator(f"input[name='customer[{name}]']")

    @property
    def submit(self) -> Locator:
        return self.form.locator("[type='submit']").first

    @property
    def heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Create Account")

    @property
    def validation_errors(self) -> Locator:
        return self.page.get_by_text(re.compile(r"blank|invalid|too short|already", re.I)).first

    def fill_and_submit(
        self, first_name: str = "", last_name: str = "", email: str = "", password: str = ""
    ) -> None:
        for name, value in (
            ("first_name", first_name),
            ("last_name", last_name),
            ("email", email),
            ("password", password),
        ):
            if self.field(name).count():
                self.field(name).fill(value)
        self.submit.click()
        self.page.wait_for_load_state("domcontentloaded")
        recover_from_checkpoint(self.page)

    def hit_bot_challenge(self) -> bool:
        return "/challenge" in self.page.url

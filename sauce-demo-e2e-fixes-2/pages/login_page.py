from __future__ import annotations

import re

from playwright.sync_api import Locator

from pages.base_page import BasePage
from utils.helpers import recover_from_checkpoint


class LoginPage(BasePage):
    path = "/account/login"

    @property
    def form(self) -> Locator:
        return self.page.locator("form[action$='/account/login']").first

    @property
    def email(self) -> Locator:
        return self.form.locator("input[name='customer[email]']")

    @property
    def password(self) -> Locator:
        return self.form.locator("input[name='customer[password]']")

    @property
    def submit(self) -> Locator:
        return self.form.locator("[type='submit']").first

    @property
    def heading(self) -> Locator:
        return self.page.get_by_role("heading", name="Customer Login")

    @property
    def error_message(self) -> Locator:
        return self.page.get_by_text(re.compile(r"incorrect|invalid", re.I)).first

    @property
    def forgot_password_link(self) -> Locator:
        return self.page.get_by_text(re.compile("forgot", re.I)).first

    @property
    def recover_email(self) -> Locator:
        return self.page.locator("form[action$='/account/recover'] input[name='email']")

    def login(self, email: str, password: str) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.submit.click()
        self.page.wait_for_load_state("domcontentloaded")
        recover_from_checkpoint(self.page)

    def hit_bot_challenge(self) -> bool:
        """Shopify may show a captcha after repeated attempts; tests skip rather than fail."""
        return "/challenge" in self.page.url

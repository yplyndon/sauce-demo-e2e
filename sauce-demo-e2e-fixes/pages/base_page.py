"""BasePage: behaviour and locators shared by every page (header, footer, product grid)."""
from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, Response

from utils.helpers import goto_with_retry, handle_from_href, unique

# label -> href, as rendered in the header / menu of the Sauce Demo theme
HEADER_LINKS: dict[str, str] = {
    "Search": "/search",
    "About Us": "/pages/about-us",
    "Log In": "/account/login",
    "Sign up": "/account/register",
    "My Cart": "/cart",
}
MENU_LINKS: dict[str, str] = {
    "Home": "/",
    "Catalog": "/collections/all",
    "Blog": "/blogs/news",
    "About Us": "/pages/about-us",
    "Login": "/account/login",
    "Create account": "/account/register",
}


class BasePage:
    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    # ------------------------------------------------------------------ navigation
    def open(self) -> Response | None:
        return goto_with_retry(self.page, self.path, wait_until="domcontentloaded")

    def link_by_href(self, href: str) -> Locator:
        selector = "a[href='/']" if href == "/" else f"a[href$='{href}']"
        return self.page.locator(selector).first

    # ------------------------------------------------------------------ header
    @property
    def logo(self) -> Locator:
        return self.page.get_by_role("img", name="Sauce Demo").first

    @property
    def tagline(self) -> Locator:
        return self.page.get_by_text("Just a demo site showing off what Sauce can do")

    @property
    def cart_link(self) -> Locator:
        return self.page.locator("a[href$='/cart']", has_text=re.compile("My Cart")).first

    def cart_count(self) -> int:
        match = re.search(r"\((\d+)\)", self.cart_link.text_content() or "")
        return int(match.group(1)) if match else 0

    def click_header_link(self, label: str) -> None:
        self.page.get_by_role("link", name=label, exact=True).first.click()

    # ------------------------------------------------------------------ footer
    @property
    def footer_about_text(self) -> Locator:
        return self.page.get_by_text("This is a demo site created for")

    @property
    def payment_icons(self) -> Locator:
        return self.page.get_by_role("img", name=re.compile("We accept"))

    @property
    def copyright_notice(self) -> Locator:
        return self.page.get_by_text(re.compile(r"Copyright ©"))

    # ------------------------------------------------------------------ product grid (home, catalog, search, related)
    def product_handles(self) -> list[str]:
        """Unique product handles linked from the page, in DOM order (markup-agnostic)."""
        hrefs = self.page.locator("a[href*='/products/']").evaluate_all(
            "els => els.map(e => e.getAttribute('href'))"
        )
        return unique(h for h in (handle_from_href(href) for href in hrefs) if h)

    def product_card(self, handle: str, title: str | None = None) -> Locator:
        card = self.page.locator(f"a[href*='/products/{handle}']")
        if title:
            card = card.filter(has_text=title)
        return card.first

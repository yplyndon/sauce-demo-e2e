"""Root conftest: global fixtures, Playwright overrides and reporting hooks.

Layers
------
* Session config      -> ``settings``, ``base_url``, ``browser_context_args``, ``browser_type_launch_args``
* UI fixtures         -> ``page`` (timeouts applied), one fixture per page object
* API fixtures        -> ``api`` (isolated cart), ``cart_api`` (shares the browser's cookies), ``product_catalog``
* Hooks               -> auto layer markers, failure screenshots embedded in the HTML report
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Callable, Iterator

import pytest
from playwright.sync_api import Page, Playwright, expect

from clients import ShopifyApi
from config.settings import settings as _settings
from pages import (
    AboutPage,
    BlogPage,
    CartPage,
    CatalogPage,
    HomePage,
    LoginPage,
    ProductPage,
    RegisterPage,
    SearchPage,
)
from testdata import PRODUCTS
from utils.logger import get_logger

log = get_logger("conftest")
TESTS_DIR = Path(__file__).parent / "tests"


# ============================================================================ hooks
def pytest_configure(config: pytest.Config) -> None:
    """Show the target environment in the HTML report header."""
    try:
        from pytest_metadata.plugin import metadata_key

        config.stash[metadata_key]["Target"] = _settings.base_url
        config.stash[metadata_key]["Project"] = "Sauce Demo - Playwright/Python E2E"
    except Exception:  # metadata plugin missing -> not critical
        pass


def pytest_html_report_title(report) -> None:  # pytest-html hook
    report.title = "Sauce Demo - E2E Test Report"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Auto-apply the layer marker (ui / api / e2e) from the folder a test lives in."""
    for item in items:
        try:
            layer = item.path.relative_to(TESTS_DIR).parts[0]
        except (ValueError, IndexError):
            continue
        if layer in {"ui", "api", "e2e"}:
            item.add_marker(getattr(pytest.mark, layer))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Embed a full-page screenshot + URL into the HTML report when a browser test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page: Page | None = item.funcargs.get("page")
    if page is None or page.is_closed():
        return
    if getattr(page, "rate_limited", None):
        report.sections.append(
            (
                "Environment note",
                "Shopify rate-limited this test (HTTP 429) - likely an environment issue, "
                "not a product defect. Re-run with fewer workers (-n 2).\n" + "\n".join(page.rate_limited),
            )
        )
    try:
        from pytest_html import extras

        png = page.screenshot(full_page=True)
        report.extras = getattr(report, "extras", []) + [
            extras.image(base64.b64encode(png).decode("utf-8"), name="Failure screenshot"),
            extras.url(page.url, name="Page URL"),
        ]
    except Exception as exc:  # never let reporting break the run
        log.warning("Could not attach failure screenshot: %s", exc)


# ============================================================================ session config
@pytest.fixture(scope="session")
def settings():
    return _settings


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """--base-url on the CLI wins, otherwise BASE_URL / .env / default from settings."""
    return request.config.getoption("base_url") or _settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "viewport": {"width": _settings.viewport_width, "height": _settings.viewport_height},
        "locale": _settings.locale,
        "timezone_id": _settings.timezone_id,
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    return {**browser_type_launch_args, "slow_mo": _settings.slow_mo_ms}


# ============================================================================ UI fixtures
@pytest.fixture
def page(page: Page) -> Page:
    """pytest-playwright's page, with project-wide timeouts applied."""
    page.set_default_timeout(_settings.default_timeout_ms)
    page.set_default_navigation_timeout(_settings.navigation_timeout_ms)
    expect.set_options(timeout=_settings.expect_timeout_ms)

    # Remember pages Shopify rate-limited (HTTP 429) so failures can be triaged correctly.
    rate_limited: list[str] = []
    page.on(
        "response",
        lambda r: rate_limited.append(r.url)
        if r.status == 429 and r.request.resource_type == "document"
        else None,
    )
    page.rate_limited = rate_limited  # type: ignore[attr-defined]
    return page


@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def catalog_page(page: Page) -> CatalogPage:
    return CatalogPage(page)


@pytest.fixture
def search_page(page: Page) -> SearchPage:
    return SearchPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def register_page(page: Page) -> RegisterPage:
    return RegisterPage(page)


@pytest.fixture
def about_page(page: Page) -> AboutPage:
    return AboutPage(page)


@pytest.fixture
def blog_page(page: Page) -> BlogPage:
    return BlogPage(page)


@pytest.fixture
def open_product(page: Page) -> Callable[[str], ProductPage]:
    """Factory: ``open_product('grey-jacket')`` -> opened ProductPage."""

    def _open(handle: str) -> ProductPage:
        product_page = ProductPage(page, handle)
        product_page.open()
        return product_page

    return _open


# ============================================================================ API fixtures
@pytest.fixture
def api(playwright: Playwright) -> Iterator[ShopifyApi]:
    """Standalone API client - every test gets its own cookie jar, hence its own cart."""
    context = playwright.request.new_context(extra_http_headers={"Accept": "application/json"})
    yield ShopifyApi(context, _settings.base_url)
    context.dispose()


@pytest.fixture
def cart_api(page: Page) -> ShopifyApi:
    """API client bound to the *browser context*: shares cookies (and therefore the cart) with the UI."""
    return ShopifyApi(page.request, _settings.base_url)


@pytest.fixture(scope="session")
def product_catalog(playwright: Playwright) -> dict[str, dict]:
    """Resolve live variant ids/prices once per session so no ids are hard-coded.

    {handle: {"variant_id": int, "price_minor": int, "title": str, "available": bool}}
    """
    context = playwright.request.new_context()
    client = ShopifyApi(context, _settings.base_url)
    catalog: dict[str, dict] = {}
    try:
        for product in PRODUCTS:
            response = client.product_js(product.handle)
            assert response.ok, f"Cannot load /products/{product.handle}.js -> HTTP {response.status}"
            data = response.json()
            variant = data["variants"][0]
            catalog[product.handle] = {
                "variant_id": variant["id"],
                "price_minor": variant["price"],
                "title": data["title"],
                "available": variant["available"],
            }
    finally:
        context.dispose()
    return catalog

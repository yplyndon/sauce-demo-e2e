import re

import pytest
from playwright.sync_api import expect

from pages import HEADER_LINKS, MENU_LINKS
from utils.helpers import goto_with_retry

pytestmark = [pytest.mark.regression, pytest.mark.functional]

SITE_PAGES = [
    "/",
    "/collections/all",
    "/blogs/news",
    "/pages/about-us",
    "/search",
    "/account/login",
    "/account/register",
    "/cart",
]


@pytest.mark.smoke
@pytest.mark.parametrize("path", SITE_PAGES)
def test_every_main_page_loads_and_has_store_title(page, path):
    response = goto_with_retry(page, path)
    assert response is not None and response.ok, f"{path} returned {response and response.status}"
    expect(page).to_have_title(re.compile("Sauce Demo"))


@pytest.mark.parametrize("label,href", HEADER_LINKS.items())
def test_header_links_point_to_expected_urls(home_page, label, href):
    home_page.open()
    expect(home_page.link_by_href(href)).to_have_attribute("href", re.compile(f"{re.escape(href)}$"))


@pytest.mark.parametrize("label,href", MENU_LINKS.items())
def test_menu_links_point_to_expected_urls(home_page, label, href):
    home_page.open()
    expect(home_page.link_by_href(href)).to_have_attribute("href", re.compile(f"{re.escape(href)}$"))


@pytest.mark.parametrize(
    "label,url_part",
    [
        ("About Us", "/pages/about-us"),
        ("Log In", "/account/login"),
        ("Sign up", "/account/register"),
        ("Search", "/search"),
    ],
)
def test_clicking_header_link_navigates_to_page(home_page, label, url_part):
    home_page.open()
    home_page.click_header_link(label)
    expect(home_page.page).to_have_url(re.compile(re.escape(url_part)))


@pytest.mark.negative
def test_unknown_page_returns_404(page):
    response = page.goto("/pages/this-page-does-not-exist")
    assert response is not None and response.status == 404
    expect(page).to_have_title(re.compile("404"))


@pytest.mark.negative
def test_unknown_product_returns_404(page):
    response = page.goto("/products/this-product-does-not-exist")
    assert response is not None and response.status == 404

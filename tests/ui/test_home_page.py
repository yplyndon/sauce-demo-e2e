import re

import pytest
from playwright.sync_api import expect

from testdata import PRODUCTS

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
def test_home_page_loads_successfully(home_page):
    response = home_page.open()
    assert response is not None and response.ok
    expect(home_page.page).to_have_title(re.compile("Sauce Demo"))


@pytest.mark.smoke
def test_branding_is_displayed(home_page):
    home_page.open()
    expect(home_page.logo).to_be_visible()
    expect(home_page.tagline).to_be_visible()


@pytest.mark.smoke
@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_featured_product_is_listed_with_name_and_price(home_page, product):
    home_page.open()
    card = home_page.product_card(product.handle, product.title)
    expect(card).to_be_visible()
    expect(card).to_contain_text(product.display_price)


def test_home_page_lists_all_expected_featured_products(home_page):
    home_page.open()
    assert {p.handle for p in PRODUCTS} <= set(home_page.product_handles())


def test_cart_counter_starts_at_zero_for_new_visitor(home_page):
    home_page.open()
    assert home_page.cart_count() == 0


@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_clicking_a_featured_product_opens_its_detail_page(home_page, product):
    home_page.open()
    product_page = home_page.open_product(product.handle, product.title)
    expect(product_page.heading).to_have_text(product.title)

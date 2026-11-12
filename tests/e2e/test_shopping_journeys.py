"""End-to-end customer journeys: real clicks through the UI, with the Ajax API used as the
independent source of truth for cart state."""
import re

import pytest
from playwright.sync_api import expect

from testdata import PRODUCTS

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
def test_guest_browses_adds_to_cart_and_reaches_checkout(home_page, cart_page, cart_api):
    product = PRODUCTS[0]

    home_page.open()
    pdp = home_page.open_product(product.handle, product.title)
    expect(pdp.heading).to_have_text(product.title)
    expect(pdp.price).to_have_text(product.display_price)

    pdp.add_to_cart()

    cart_page.open()
    expect(cart_page.item_link(product.title)).to_be_visible()
    expect(cart_page.shows_amount(product.price)).to_be_visible()
    cart = cart_api.get_cart().json()
    assert cart["item_count"] == 1
    assert cart["total_price"] == product.price_minor

    cart_page.checkout()
    expect(cart_page.page).to_have_url(re.compile(r"checkout"))


def test_shopper_buys_multiple_products_and_total_is_correct(open_product, cart_page, cart_api):
    for product in PRODUCTS:
        open_product(product.handle).add_to_cart()

    cart_page.open()
    assert cart_page.line_count() == len(PRODUCTS)
    for product in PRODUCTS:
        expect(cart_page.item_link(product.title)).to_be_visible()

    expected_minor = sum(p.price_minor for p in PRODUCTS)
    assert cart_api.get_cart().json()["total_price"] == expected_minor
    expected_display = f"{expected_minor / 100:.2f}"
    expect(cart_page.shows_amount(expected_display)).to_be_visible()


def test_shopper_finds_product_via_search_and_buys_it(search_page, cart_page, cart_api):
    noir = next(p for p in PRODUCTS if p.handle == "noir-jacket")

    search_page.open_with_query("noir")
    search_page.product_card(noir.handle, noir.title).click()
    expect(search_page.page).to_have_url(re.compile(r"/products/noir-jacket"))

    from pages import ProductPage

    ProductPage(search_page.page, noir.handle).add_to_cart()
    cart_page.open()
    expect(cart_page.item_link(noir.title)).to_be_visible()
    assert cart_api.get_cart().json()["total_price"] == noir.price_minor


def test_shopper_changes_quantity_then_removes_item(open_product, cart_page, cart_api):
    product = PRODUCTS[2]
    open_product(product.handle).add_to_cart()

    cart_page.open()
    cart_page.set_quantity(0, 2)
    assert cart_api.get_cart().json()["total_price"] == product.price_minor * 2

    cart_page.remove_item(0)
    assert cart_page.is_empty()
    assert cart_api.get_cart().json()["item_count"] == 0


def test_cart_is_private_to_the_browser_session(open_product, browser, base_url):
    open_product(PRODUCTS[0].handle).add_to_cart()

    other_context = browser.new_context(base_url=base_url)
    try:
        other_page = other_context.new_page()
        other_page.goto("/cart")
        assert other_page.locator("input[name^='updates']").count() == 0
    finally:
        other_context.close()


@pytest.mark.negative
def test_checkout_with_empty_cart_does_not_start_a_checkout(cart_page):
    cart_page.open()
    assert cart_page.is_empty()
    expect(cart_page.page).not_to_have_url(re.compile(r"checkout"))

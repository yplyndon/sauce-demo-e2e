"""Cart UI behaviour. Cart state is seeded / verified through the Ajax API (hybrid approach)
so each test checks one UI behaviour without re-testing the whole purchase journey."""
import pytest
from playwright.sync_api import expect

from testdata import PRODUCTS

pytestmark = [pytest.mark.regression, pytest.mark.functional]

JACKET = PRODUCTS[0]


@pytest.mark.smoke
def test_empty_cart_has_no_line_items(cart_page, cart_api):
    cart_page.open()
    assert cart_page.is_empty()
    assert cart_api.get_cart().json()["item_count"] == 0


@pytest.mark.smoke
def test_adding_product_from_pdp_puts_it_in_cart(open_product, cart_page, cart_api):
    open_product(JACKET.handle).add_to_cart()
    cart_page.open()
    expect(cart_page.item_link(JACKET.title)).to_be_visible()
    expect(cart_page.shows_amount(JACKET.price)).to_be_visible()
    cart = cart_api.get_cart().json()
    assert cart["item_count"] == 1
    assert cart["total_price"] == JACKET.price_minor


def test_cart_page_lists_items_seeded_via_api(cart_page, cart_api, product_catalog):
    cart_api.add_to_cart(product_catalog[JACKET.handle]["variant_id"], 2)
    cart_page.open()
    assert cart_page.line_count() == 1
    assert cart_page.quantity(0) == 2
    expect(cart_page.item_link(JACKET.title)).to_be_visible()


def test_updating_quantity_recalculates_cart_total(cart_page, cart_api, product_catalog):
    cart_api.add_to_cart(product_catalog[JACKET.handle]["variant_id"], 1)
    cart_page.open()
    cart_page.set_quantity(0, 3)
    cart = cart_api.get_cart().json()
    assert cart["item_count"] == 3
    assert cart["total_price"] == JACKET.price_minor * 3


def test_removing_the_only_item_empties_the_cart(cart_page, cart_api, product_catalog):
    cart_api.add_to_cart(product_catalog[JACKET.handle]["variant_id"], 1)
    cart_page.open()
    cart_page.remove_item(0)
    assert cart_page.is_empty()
    assert cart_api.get_cart().json()["item_count"] == 0


def test_cart_contents_survive_a_page_reload(cart_page, cart_api, product_catalog):
    cart_api.add_to_cart(product_catalog[JACKET.handle]["variant_id"], 1)
    cart_page.open()
    cart_page.reload()
    expect(cart_page.item_link(JACKET.title)).to_be_visible()


def test_header_cart_counter_reflects_items(cart_page, cart_api, product_catalog):
    cart_api.add_to_cart(product_catalog[JACKET.handle]["variant_id"], 2)
    cart_page.open()
    assert cart_page.cart_count() == 2


@pytest.mark.smoke
def test_checkout_button_is_available_when_cart_has_items(cart_page, cart_api, product_catalog):
    cart_api.add_to_cart(product_catalog[JACKET.handle]["variant_id"], 1)
    cart_page.open()
    expect(cart_page.checkout_button).to_be_visible()

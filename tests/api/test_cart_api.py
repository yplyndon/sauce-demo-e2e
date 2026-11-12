"""Cart contract + business rules through Shopify's Ajax API.
Each test gets a fresh cookie jar (``api`` fixture) => an isolated cart."""
import pytest
from jsonschema import validate

from testdata import PRODUCTS
from testdata.schemas import CART_SCHEMA

pytestmark = [pytest.mark.regression, pytest.mark.functional]


def _variant(product_catalog, product):
    return product_catalog[product.handle]["variant_id"]


@pytest.mark.smoke
def test_new_session_starts_with_empty_cart(api):
    response = api.get_cart()
    assert response.status == 200
    cart = response.json()
    validate(instance=cart, schema=CART_SCHEMA)
    assert cart["item_count"] == 0
    assert cart["items"] == []
    assert cart["total_price"] == 0


@pytest.mark.smoke
@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_add_single_product(api, product_catalog, product):
    response = api.add_to_cart(_variant(product_catalog, product), 1)
    assert response.status == 200
    line = response.json()
    assert line["variant_id"] == _variant(product_catalog, product)
    assert line["quantity"] == 1

    cart = api.get_cart().json()
    validate(instance=cart, schema=CART_SCHEMA)
    assert cart["item_count"] == 1
    assert cart["total_price"] == product.price_minor


def test_adding_same_variant_twice_merges_into_one_line(api, product_catalog):
    variant = _variant(product_catalog, PRODUCTS[0])
    api.add_to_cart(variant, 1)
    api.add_to_cart(variant, 1)
    cart = api.get_cart().json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 2
    assert cart["total_price"] == PRODUCTS[0].price_minor * 2


def test_adding_different_products_sums_the_total(api, product_catalog):
    for product in PRODUCTS:
        api.add_to_cart(_variant(product_catalog, product), 1)
    cart = api.get_cart().json()
    assert len(cart["items"]) == len(PRODUCTS)
    assert cart["item_count"] == len(PRODUCTS)
    assert cart["total_price"] == sum(p.price_minor for p in PRODUCTS)


def test_change_quantity_of_existing_line(api, product_catalog):
    api.add_to_cart(_variant(product_catalog, PRODUCTS[0]), 1)
    response = api.change_cart(quantity=4, line=1)
    assert response.status == 200
    cart = api.get_cart().json()
    assert cart["item_count"] == 4
    assert cart["total_price"] == PRODUCTS[0].price_minor * 4


def test_setting_quantity_to_zero_removes_the_line(api, product_catalog):
    api.add_to_cart(_variant(product_catalog, PRODUCTS[0]), 2)
    api.change_cart(quantity=0, line=1)
    assert api.get_cart().json()["item_count"] == 0


def test_update_endpoint_sets_absolute_quantities(api, product_catalog):
    variant = _variant(product_catalog, PRODUCTS[1])
    api.add_to_cart(variant, 1)
    response = api.update_cart({variant: 3})
    assert response.status == 200
    assert api.get_cart().json()["item_count"] == 3


def test_clear_endpoint_empties_the_cart(api, product_catalog):
    for product in PRODUCTS:
        api.add_to_cart(_variant(product_catalog, product), 1)
    assert api.clear_cart().status == 200
    assert api.get_cart().json()["item_count"] == 0


def test_carts_are_isolated_between_sessions(api, playwright, settings, product_catalog):
    from clients import ShopifyApi

    api.add_to_cart(_variant(product_catalog, PRODUCTS[0]), 1)
    other_context = playwright.request.new_context()
    try:
        other = ShopifyApi(other_context, settings.base_url)
        assert other.get_cart().json()["item_count"] == 0
    finally:
        other_context.dispose()


@pytest.mark.negative
def test_adding_unknown_variant_is_rejected(api):
    response = api.add_to_cart(variant_id=1, quantity=1)
    assert response.status in (404, 422)
    body = response.json()
    assert body.get("message") or body.get("description")
    assert api.get_cart().json()["item_count"] == 0

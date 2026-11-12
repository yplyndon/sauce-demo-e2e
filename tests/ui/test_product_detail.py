import re

import pytest
from playwright.sync_api import expect

from testdata import PRODUCTS

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_product_page_shows_core_information(open_product, product):
    pdp = open_product(product.handle)
    expect(pdp.page).to_have_title(re.compile(rf"{re.escape(product.title)}.*Sauce Demo"))
    expect(pdp.heading).to_have_text(product.title)
    expect(pdp.price).to_have_text(product.display_price)
    expect(pdp.description).to_be_visible()
    expect(pdp.main_image).to_be_visible()


@pytest.mark.smoke
@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_add_to_cart_button_is_available(open_product, product):
    pdp = open_product(product.handle)
    expect(pdp.add_button).to_be_visible()
    expect(pdp.add_button).to_be_enabled()


@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_related_products_exclude_current_product(page, product):
    # The "You Might Also Like" block is only rendered when the product is opened
    # within a collection context (as when a shopper clicks it from the home page).
    from pages import ProductPage

    page.goto(f"/collections/frontpage/products/{product.handle}")
    pdp = ProductPage(page, product.handle)
    expect(pdp.related_section).to_be_visible()
    related = pdp.related_handles()
    assert related, "expected at least one related product"
    assert product.handle not in related


def test_product_page_is_reachable_via_collection_url(page):
    response = page.goto("/collections/frontpage/products/grey-jacket")
    assert response is not None and response.ok
    expect(page.locator("link[rel='canonical']")).to_have_attribute(
        "href", re.compile(r"/products/grey-jacket$")
    )

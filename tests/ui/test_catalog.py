import re
import time

import pytest
from playwright.sync_api import expect

from testdata import PRODUCTS

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
def test_catalog_lists_products(catalog_page):
    response = catalog_page.open()
    assert response is not None and response.ok
    assert len(catalog_page.product_handles()) >= len(PRODUCTS)


@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_catalog_shows_each_featured_product_with_price(catalog_page, product):
    catalog_page.open()
    card = catalog_page.product_card(product.handle, product.title)
    expect(card).to_be_visible()
    expect(card).to_contain_text(re.compile(r"£\d+\.\d{2}"))
    expect(card).to_contain_text(product.display_price)


def test_every_product_link_in_catalog_resolves(catalog_page, cart_api):
    catalog_page.open()
    broken = []
    for handle in catalog_page.product_handles():
        response = cart_api.get(f"/products/{handle}")  # retries on 429
        if not response.ok:
            broken.append((handle, response.status))
        time.sleep(0.3)  # be polite to the shared demo store
    assert not broken, f"Broken product links: {broken}"


def test_catalog_has_no_duplicate_products(catalog_page):
    catalog_page.open()
    handles = catalog_page.product_handles()
    assert len(handles) == len(set(handles))

import time

import pytest
from jsonschema import validate

from testdata import CURRENCY_CODE, PRODUCTS, PRODUCTS_BY_HANDLE
from testdata.schemas import PRODUCTS_RESPONSE_SCHEMA, PRODUCT_SCHEMA

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
def test_products_endpoint_returns_json_200(api):
    response = api.products()
    assert response.status == 200
    assert "application/json" in response.headers["content-type"]


def test_products_response_matches_schema(api):
    validate(instance=api.products().json(), schema=PRODUCTS_RESPONSE_SCHEMA)


def test_products_contain_expected_featured_items(api):
    products = {p["handle"]: p for p in api.products().json()["products"]}
    assert set(PRODUCTS_BY_HANDLE) <= set(products)


def test_product_ids_and_handles_are_unique(api):
    products = api.products().json()["products"]
    assert len({p["id"] for p in products}) == len(products)
    assert len({p["handle"] for p in products}) == len(products)


@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_product_prices_match_expected(api, product):
    products = {p["handle"]: p for p in api.products().json()["products"]}
    assert products[product.handle]["title"] == product.title
    assert products[product.handle]["variants"][0]["price"] == product.price


def test_limit_parameter_restricts_result_size(api):
    assert len(api.products(limit=1).json()["products"]) == 1


def test_pagination_returns_different_products_per_page(api):
    page1 = {p["id"] for p in api.products(limit=2, page=1).json()["products"]}
    page2 = {p["id"] for p in api.products(limit=2, page=2).json()["products"]}
    assert page1 and page2
    assert page1.isdisjoint(page2)


@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_product_json_endpoint(api, product):
    response = api.product_json(product.handle)
    assert response.status == 200
    body = response.json()["product"]
    validate(instance=body, schema=PRODUCT_SCHEMA)
    assert body["handle"] == product.handle


@pytest.mark.parametrize("product", PRODUCTS, ids=lambda p: p.handle)
def test_product_ajax_endpoint_reports_prices_in_minor_units(api, product):
    response = api.product_js(product.handle)
    assert response.status == 200
    body = response.json()
    assert body["title"] == product.title
    assert body["price"] == product.price_minor
    assert body["variants"][0]["price"] == product.price_minor
    assert isinstance(body["available"], bool)


@pytest.mark.negative
@pytest.mark.parametrize("endpoint", ["json", "js"])
def test_unknown_product_returns_404(api, endpoint):
    response = api.get(f"/products/does-not-exist-123.{endpoint}")
    assert response.status == 404


def test_products_endpoint_responds_within_budget(api):
    start = time.perf_counter()
    response = api.products()
    elapsed = time.perf_counter() - start
    assert response.ok
    assert elapsed < 5, f"/products.json took {elapsed:.2f}s"


def test_store_currency_is_gbp(api):
    assert api.get_cart().json()["currency"] == CURRENCY_CODE

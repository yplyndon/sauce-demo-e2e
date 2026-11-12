import pytest
from jsonschema import validate

from testdata import PRODUCTS
from testdata.schemas import COLLECTIONS_RESPONSE_SCHEMA, PRODUCTS_RESPONSE_SCHEMA

pytestmark = [pytest.mark.regression, pytest.mark.functional]


def test_collections_endpoint_matches_schema(api):
    response = api.collections()
    assert response.status == 200
    validate(instance=response.json(), schema=COLLECTIONS_RESPONSE_SCHEMA)


def test_frontpage_collection_contains_featured_products(api):
    response = api.collection_products("frontpage")
    assert response.status == 200
    body = response.json()
    validate(instance=body, schema=PRODUCTS_RESPONSE_SCHEMA)
    assert {p.handle for p in PRODUCTS} <= {p["handle"] for p in body["products"]}


def test_all_collection_is_a_superset_of_frontpage(api):
    all_handles = {p["handle"] for p in api.collection_products("all").json()["products"]}
    front_handles = {p["handle"] for p in api.collection_products("frontpage").json()["products"]}
    assert front_handles <= all_handles


@pytest.mark.negative
def test_unknown_collection_returns_no_products(api):
    response = api.collection_products("no-such-collection-xyz")
    # Shopify answers 404 or an empty list depending on the theme/store settings
    assert response.status == 404 or response.json()["products"] == []

import pytest

pytestmark = [pytest.mark.regression, pytest.mark.functional]

SEARCH_CASES = [
    ("jacket", {"grey-jacket", "noir-jacket"}),
    ("JACKET", {"grey-jacket", "noir-jacket"}),  # case-insensitive
    ("striped", {"striped-top"}),
    ("noir", {"noir-jacket"}),
]


@pytest.mark.smoke
@pytest.mark.parametrize("term,expected", SEARCH_CASES, ids=[c[0] for c in SEARCH_CASES])
def test_search_by_url_returns_matching_products(search_page, term, expected):
    response = search_page.open_with_query(term)
    assert response is not None and response.ok
    assert expected <= set(search_page.product_handles())


def test_search_through_the_ui_form(search_page):
    search_page.open()
    search_page.search("jacket")
    search_page.wait_for_results()
    assert {"grey-jacket", "noir-jacket"} <= set(search_page.product_handles())


@pytest.mark.negative
def test_search_with_no_match_returns_no_products(search_page):
    search_page.open_with_query("zzzxqwvnomatch")
    assert search_page.product_handles() == []


@pytest.mark.negative
def test_empty_search_does_not_error(search_page):
    response = search_page.open_with_query("")
    assert response is not None and response.ok

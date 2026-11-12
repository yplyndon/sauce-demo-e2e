"""Storefront-level checks: transport security, SEO/meta files and HTML endpoints."""
import pytest

pytestmark = [pytest.mark.regression]


@pytest.mark.smoke
def test_cart_endpoint_is_reachable_and_json(api):
    response = api.get_cart()
    assert response.ok
    content_type = response.headers["content-type"]
    assert "json" in content_type or "javascript" in content_type  # Shopify serves /cart.js as text/javascript
    assert "item_count" in response.json()


def test_http_redirects_to_https(api, settings):
    insecure = settings.base_url.replace("https://", "http://")
    response = api.request.get(insecure, max_redirects=0)
    assert response.status in (301, 302, 308)
    assert response.headers["location"].startswith("https://")


def test_robots_txt_is_served(api):
    response = api.get("/robots.txt")
    assert response.status == 200
    assert "User-agent" in response.text()


def test_sitemap_is_valid_xml(api):
    response = api.get("/sitemap.xml")
    assert response.status == 200
    body = response.text()
    assert "<urlset" in body or "<sitemapindex" in body


def test_search_endpoint_returns_html_with_matches(api):
    response = api.search_html("jacket")
    assert response.status == 200
    assert "text/html" in response.headers["content-type"]
    assert "jacket" in response.text().lower()


@pytest.mark.negative
def test_unknown_url_returns_404_html(api):
    response = api.get("/definitely/not/a/real/page")
    assert response.status == 404

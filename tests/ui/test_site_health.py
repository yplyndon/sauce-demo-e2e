"""Cheap, broad regression nets: broken internal links and failing page-level requests.
Requests are throttled and retried on HTTP 429 because the demo store rate-limits bursts."""
import time

import pytest

pytestmark = [pytest.mark.regression]


@pytest.mark.parametrize("path", ["/", "/collections/all"])
def test_internal_links_are_not_broken(page, cart_api, settings, path):
    page.goto(path)
    hrefs = page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
    internal = sorted(
        {h.split("#")[0] for h in hrefs if h.startswith(settings.base_url) and h.split("#")[0]}
    )
    assert internal, "no internal links found"
    broken = []
    for url in internal:
        status = cart_api.get(url).status  # retries on 429
        if status >= 400:
            broken.append((url, status))
        time.sleep(0.3)
    assert not broken, f"Broken internal links on {path}: {broken}"


def test_home_page_makes_no_failing_document_or_xhr_requests(page, settings):
    failures: list[tuple[str, int]] = []

    def on_response(response):
        if (
            response.url.startswith(settings.base_url)
            and response.request.resource_type in {"document", "xhr", "fetch"}
            and response.status >= 400
            and response.status != 429  # rate limiting is environmental, not a defect
        ):
            failures.append((response.url, response.status))

    page.on("response", on_response)
    # 'networkidle' never settles here (third-party pixels keep connections open)
    page.goto("/", wait_until="load")
    page.wait_for_timeout(2000)
    assert not failures, f"Failing same-origin requests: {failures}"

"""Thin API client for Shopify's public storefront endpoints.

It wraps Playwright's ``APIRequestContext`` so it can be used in two ways:

* standalone (``playwright.request.new_context()``)  -> pure API tests, isolated cart per test
* bound to a browser (``page.request``)               -> shares cookies with the UI, which lets
  UI tests seed/inspect the cart through the API (fast, deterministic "hybrid" tests).
"""
from __future__ import annotations

import time
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse


class ShopifyApi:
    JSON_HEADERS = {"Accept": "application/json"}

    def __init__(self, request: APIRequestContext, base_url: str) -> None:
        self.request = request
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------ plumbing
    def url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self.base_url}{path}"

    MAX_RETRIES = 4

    def _send(self, send) -> APIResponse:
        """Run a request and back off / retry while Shopify answers 429 (rate limit)."""
        for attempt in range(self.MAX_RETRIES + 1):
            response = send()
            if response.status != 429 or attempt == self.MAX_RETRIES:
                return response
            try:
                delay = float(response.headers.get("retry-after", 0))
            except ValueError:
                delay = 0
            time.sleep(min(max(delay, 2 * 2**attempt), 20))
        return response

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send(lambda: self.request.get(self.url(path), **kwargs))

    def post(self, path: str, payload: dict | None = None) -> APIResponse:
        return self._send(
            lambda: self.request.post(self.url(path), data=payload or {}, headers=self.JSON_HEADERS)
        )

    # ------------------------------------------------------------------ catalogue
    def products(self, limit: int | None = None, page: int | None = None) -> APIResponse:
        params = {k: v for k, v in {"limit": limit, "page": page}.items() if v is not None}
        return self.get("/products.json", params=params)

    def product_json(self, handle: str) -> APIResponse:
        """Admin-style JSON: prices are strings such as '55.00'."""
        return self.get(f"/products/{handle}.json")

    def product_js(self, handle: str) -> APIResponse:
        """Ajax API JSON: prices are integers in minor units (5500)."""
        return self.get(f"/products/{handle}.js")

    def collections(self) -> APIResponse:
        return self.get("/collections.json")

    def collection_products(self, handle: str) -> APIResponse:
        return self.get(f"/collections/{handle}/products.json")

    # ------------------------------------------------------------------ cart (Ajax API)
    def get_cart(self) -> APIResponse:
        return self.get("/cart.js")

    def add_to_cart(self, variant_id: int, quantity: int = 1) -> APIResponse:
        return self.post("/cart/add.js", {"id": variant_id, "quantity": quantity})

    def change_cart(self, quantity: int, line: int = 1) -> APIResponse:
        return self.post("/cart/change.js", {"line": line, "quantity": quantity})

    def update_cart(self, updates: dict[int, int]) -> APIResponse:
        return self.post("/cart/update.js", {"updates": {str(k): v for k, v in updates.items()}})

    def clear_cart(self) -> APIResponse:
        return self.post("/cart/clear.js")

    # ------------------------------------------------------------------ misc
    def search_html(self, term: str) -> APIResponse:
        return self.get("/search", params={"q": term}, headers={"Accept": "text/html"})

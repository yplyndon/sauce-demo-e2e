"""Small, dependency-free helpers shared by pages, clients and tests."""
from __future__ import annotations

import re
import uuid
from decimal import Decimal
from typing import Iterable, TypeVar

T = TypeVar("T")

_PRODUCT_HREF = re.compile(r"/products/([^/?#]+)")


def handle_from_href(href: str | None) -> str | None:
    """'/collections/frontpage/products/grey-jacket?x=1' -> 'grey-jacket'."""
    match = _PRODUCT_HREF.search(href or "")
    return match.group(1) if match else None


def unique(items: Iterable[T]) -> list[T]:
    """De-duplicate while preserving order."""
    return list(dict.fromkeys(items))


def to_minor_units(amount: str) -> int:
    """'55.00' -> 5500 (Shopify's Ajax API reports prices in minor units)."""
    return int(Decimal(amount) * 100)


def format_money(minor_units: int, symbol: str = "£") -> str:
    return f"{symbol}{Decimal(minor_units) / 100:.2f}"


def unique_email(prefix: str = "qa") -> str:
    return f"{prefix}+{uuid.uuid4().hex[:10]}@example.com"


def goto_with_retry(page, url: str, retries: int = 3, **kwargs):
    """page.goto that backs off and retries when Shopify rate-limits us (HTTP 429)."""
    import time

    response = None
    for attempt in range(retries + 1):
        response = page.goto(url, **kwargs)
        if response is None or response.status != 429 or attempt == retries:
            return response
        time.sleep(min(2 * 2**attempt, 15))
    return response

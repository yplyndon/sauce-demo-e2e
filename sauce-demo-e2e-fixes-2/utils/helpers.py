"""Small, dependency-free helpers shared by pages, clients and tests."""
from __future__ import annotations

import re
import time
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



CHECKPOINT_HEADING = re.compile(r"connection needs to be verified", re.I)


def _skip_blocked() -> None:
    import pytest

    pytest.skip(
        "Shopify served its bot checkpoint / rate limit (HTTP 429) - environment issue, "
        "not a product defect. Re-run later or with a larger PACING_SECONDS."
    )


def goto_with_retry(page, url: str, retries: int = 4, **kwargs):
    """page.goto that backs off and retries on HTTP 429; skips the test if still blocked."""
    response = None
    for attempt in range(retries + 1):
        response = page.goto(url, **kwargs)
        if response is None or response.status != 429:
            return response
        if attempt < retries:
            time.sleep(min(5 * 2**attempt, 30))
    _skip_blocked()


def recover_from_checkpoint(page, retries: int = 3) -> None:
    """If the 'connection needs to be verified' page is showing, wait and reload;
    skip the test when it does not clear (call after clicks / reloads / form posts)."""
    for attempt in range(retries + 1):
        page.wait_for_load_state("domcontentloaded")
        if page.get_by_role("heading", name=CHECKPOINT_HEADING).count() == 0:
            return
        if attempt < retries:
            time.sleep(min(5 * 2**attempt, 30))
            page.reload(wait_until="domcontentloaded")
    _skip_blocked()

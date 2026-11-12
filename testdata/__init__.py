"""Static test data, loaded from JSON so QA can edit it without touching code."""
from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

_DATA = json.loads((Path(__file__).parent / "products.json").read_text(encoding="utf-8"))

CURRENCY_CODE: str = _DATA["currency_code"]
CURRENCY_SYMBOL: str = _DATA["currency_symbol"]


@dataclass(frozen=True)
class Product:
    handle: str
    title: str
    price: str  # as displayed, e.g. "55.00"

    @property
    def price_minor(self) -> int:
        return int(Decimal(self.price) * 100)

    @property
    def display_price(self) -> str:
        return f"{CURRENCY_SYMBOL}{self.price}"


PRODUCTS: list[Product] = [Product(**p) for p in _DATA["featured_products"]]
PRODUCTS_BY_HANDLE: dict[str, Product] = {p.handle: p for p in PRODUCTS}

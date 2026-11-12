"""JSON Schemas used for API contract checks (jsonschema, Draft 2020-12)."""

_VARIANT = {
    "type": "object",
    "required": ["id", "price"],
    "properties": {
        "id": {"type": "integer"},
        "price": {"type": "string", "pattern": r"^\d+\.\d{2}$"},
    },
}

PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "handle", "variants", "images"],
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string", "minLength": 1},
        "handle": {"type": "string", "minLength": 1},
        "variants": {"type": "array", "minItems": 1, "items": _VARIANT},
        "images": {"type": "array"},
    },
}

PRODUCTS_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["products"],
    "properties": {"products": {"type": "array", "items": PRODUCT_SCHEMA}},
}

CART_SCHEMA = {
    "type": "object",
    "required": ["item_count", "items", "total_price", "currency"],
    "properties": {
        "item_count": {"type": "integer", "minimum": 0},
        "total_price": {"type": "integer", "minimum": 0},
        "currency": {"type": "string", "minLength": 3, "maxLength": 3},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["variant_id", "quantity", "title"],
                "properties": {
                    "variant_id": {"type": "integer"},
                    "quantity": {"type": "integer", "minimum": 1},
                },
            },
        },
    },
}

COLLECTIONS_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["collections"],
    "properties": {
        "collections": {
            "type": "array",
            "items": {"type": "object", "required": ["id", "handle", "title"]},
        }
    },
}

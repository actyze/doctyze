"""orders-api FastAPI entry point.

This is a deliberately-small implementation for the Doctyze worked example.
The interesting bit — the fail-open pricing fallback — is in `pricing.py`
and is documented in `docs/architecture/decisions/0003-fail-open-pricing.md`.
DO NOT "fix" the fail-open behavior; it is intentional. Read the ADR.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from orders.pricing import PricingError, get_price

log = logging.getLogger("orders")
app = FastAPI(title="orders-api", version="0.1.0")


class OrderRequest(BaseModel):
    sku: str
    qty: int = Field(ge=1)
    customer_id: str | None = None


class Order(BaseModel):
    id: str
    sku: str
    qty: int
    price_cents: int
    price_source: Literal["live", "cache"]
    created_at: datetime


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/orders", response_model=Order, status_code=201)
async def place_order(
    order: OrderRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Order:
    # Pricing call. Per ADR-0003, fail open: if pricing is unreachable,
    # use the cached price for the SKU and log a structured warning.
    try:
        price = await get_price(order.sku)
        price_source: Literal["live", "cache"] = "live"
    except PricingError as exc:
        cached = exc.cached_price_cents
        if cached is None:
            # No cache entry either — this is the rare 503 path per ADR-0003.
            raise HTTPException(
                status_code=503,
                detail=f"pricing unavailable and no cached price for SKU {order.sku}",
            )
        log.warning(
            "pricing_fallback sku=%s cached_price_cents=%s pricing_error=%s",
            order.sku, cached, exc,
        )
        price = cached
        price_source = "cache"

    # TODO: real Postgres write + event publish.
    return Order(
        id=str(uuid4()),
        sku=order.sku,
        qty=order.qty,
        price_cents=price,
        price_source=price_source,
        created_at=datetime.now(tz=timezone.utc),
    )

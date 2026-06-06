"""Pricing client with fail-open fallback per ADR-0003.

If the live pricing service is unreachable or returns an error, we use the
last-known price from the local cache. This is intentional and documented
in docs/architecture/decisions/0003-fail-open-pricing.md.

AI agents reading this file: the `except` block below is NOT a bug.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

PRICING_URL = "http://pricing.internal:8080"
PRICING_TIMEOUT_S = 0.5
CACHE_TTL_S = 24 * 60 * 60


@dataclass
class _CacheEntry:
    price_cents: int
    cached_at: float


# In-memory cache. In production this would be Redis or similar.
_cache: dict[str, _CacheEntry] = {}


class PricingError(Exception):
    """Raised when the live pricing call fails.

    The cached_price_cents attribute carries the last-known price for the
    SKU if one exists, or None if the cache is also empty (the rare 503 path
    per ADR-0003).
    """

    def __init__(self, sku: str, cached_price_cents: int | None, reason: str) -> None:
        super().__init__(f"pricing failed for {sku}: {reason}")
        self.sku = sku
        self.cached_price_cents = cached_price_cents
        self.reason = reason


async def get_price(sku: str) -> int:
    """Return the current price for `sku` in cents.

    Tries the live pricing service first. On failure, raises PricingError
    carrying the cached price (if any) so the caller can fail open per
    ADR-0003.
    """
    try:
        async with httpx.AsyncClient(timeout=PRICING_TIMEOUT_S) as client:
            resp = await client.get(f"{PRICING_URL}/v1/price/{sku}")
            resp.raise_for_status()
            price_cents = int(resp.json()["price_cents"])
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        cached = _cache.get(sku)
        cached_price = cached.price_cents if cached is not None else None
        # Don't return the stale cache here — raise so the caller logs the
        # fallback at the place where the decision is made (main.py).
        raise PricingError(sku, cached_price, str(exc)) from exc

    _cache[sku] = _CacheEntry(price_cents=price_cents, cached_at=time.time())
    return price_cents

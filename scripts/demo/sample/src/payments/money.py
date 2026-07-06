"""Money helpers for the sample payments module (Doctyze demo fixture)."""
from __future__ import annotations

from decimal import Decimal


def to_minor_units(amount: Decimal, *, currency: str = "USD") -> int:
    """Convert a decimal amount to integer minor units (e.g. cents)."""
    exponent = 2 if currency in {"USD", "EUR", "GBP"} else 0
    return int(amount.scaleb(exponent))


def format_amount(minor_units: int, *, currency: str = "USD") -> str:
    major = Decimal(minor_units).scaleb(-2)
    return f"{major:.2f} {currency}"

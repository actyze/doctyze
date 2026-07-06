"""Refund policy for the sample payments module (Doctyze demo fixture)."""
from __future__ import annotations

from decimal import Decimal

from .money import to_minor_units

# Largest refund allowed without manual approval.
MAX_AUTO_REFUND = Decimal("100.00")


def can_auto_refund(amount: Decimal) -> bool:
    """Return True if `amount` may be refunded without manual review."""
    return amount <= MAX_AUTO_REFUND


def refund(amount: Decimal, *, currency: str = "USD") -> int:
    """Issue a refund, returning the amount in minor units."""
    if not can_auto_refund(amount):
        raise ValueError("refund exceeds the auto-approval limit")
    return to_minor_units(amount, currency=currency)

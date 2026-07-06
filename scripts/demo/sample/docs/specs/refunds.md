---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/payments/refund.py]
  last_verified: 2026-07-05
---
# Spec — Refund policy

A refund may be issued automatically when the amount is at or below the
auto-approval limit `MAX_AUTO_REFUND` (currently **100.00**). Larger amounts
raise `ValueError` and require manual review.

- `can_auto_refund(amount)` — the policy predicate.
- `refund(amount, currency=...)` — issues the refund, returning minor units.

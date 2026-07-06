---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/payments/money.py]
  last_verified: 2026-07-05
---
# Spec — Money representation

Amounts are handled as `Decimal` and converted to integer **minor units**
(e.g. cents) for storage via `to_minor_units(amount, currency=...)`.
`format_amount(minor_units, currency=...)` renders them back for display.

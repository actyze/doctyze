---
doctyze:
  artifact: adr
  generated_by: write-adr
  affects: [src/payments/money.py]
  last_verified: 2026-07-05
---
# ADR-0001 — Represent money as Decimal minor units

Amounts use `Decimal` and are stored as integer **minor units** (via
`to_minor_units()`) to avoid floating-point rounding errors in payment math.

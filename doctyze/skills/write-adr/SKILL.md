---
name: write-adr
description: Capture a significant architecture/design decision in MADR format under docs/architecture/decisions/.
---
# write-adr
Write `docs/architecture/decisions/NNNN-<slug>.md` (next free 4-digit number).

## How
1. MADR format: Context, Decision, Status, Consequences, Alternatives considered.
2. Infer decisions already embodied in the code (datastore choice, sync vs async, auth model) when bootstrapping; capture new ones as they happen.
3. Never reuse an existing ADR number. Add the freshness anchor.

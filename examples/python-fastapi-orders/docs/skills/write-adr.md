---
name: write-adr
description: Use when adding a new external dependency, swapping a major architectural component, or making a non-obvious design choice. Captures the decision in MADR format under docs/architecture/decisions/.
---

# How to write an ADR for orders-api

## When to apply

- Adding a new external dependency (library, service, database, queue)
- Swapping a major architectural component
- Making a non-obvious design choice (especially one a future engineer
  might second-guess)
- Superseding an existing decision

If the change is a pure refactor or trivial fix, skip — ADRs are for
decisions, not commits.

## Required artifact

A new file at `docs/architecture/decisions/NNNN-<kebab-case-slug>.md`
where NNNN is the next zero-padded sequence number.

## Template (MADR)

```markdown
# ADR-NNNN — <title>

- Status: proposed | accepted | deprecated | superseded by ADR-MMMM
- Date: YYYY-MM-DD
- Confidence: 🟢 CONFIRMED

## Context
What situation forced this decision?

## Decision
What did we choose? Be specific — name the library, the pattern, the algorithm.

## Alternatives rejected
At least 2–4 alternatives, with the reason each was rejected.
**This is the load-bearing section.**

## Consequences
Both positive and negative consequences.
```

## Anti-patterns

- **No alternatives section** — without rejected alternatives, an ADR is
  just commit-message context. Always include 2+ alternatives.
- **Mutating accepted ADRs** — ADRs are append-only. Supersede; don't edit.
- **One ADR per commit** — overuse dilutes the signal. Use ADRs for real
  decisions only.

## Important for AI agents

Read ADR-0003 (fail-open pricing) carefully before proposing any change to
pricing-fallback behavior. That ADR exists specifically to prevent AI tools
from "fixing" deliberate fail-open intent.

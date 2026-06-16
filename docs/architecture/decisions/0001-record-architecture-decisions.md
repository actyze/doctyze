# ADR-0001: Record Architecture Decisions

**Status:** 🟢 ACCEPTED
**Date:** 2026-06-15
**Deciders:** Rohit Mangal

## Context

Doctyze makes non-obvious architectural and design choices (delivery model, data formats, adopted dependencies, the pivot from v2). We need a durable, reviewable record of *why* decisions were made, the alternatives rejected, and the consequences — so future contributors don't re-litigate settled choices or undo them without understanding the trade-offs.

## Decision

We will record significant architectural decisions as **Architecture Decision Records (ADRs)** in [MADR](https://adr.github.io/madr/) format, stored under `docs/architecture/decisions/` and numbered sequentially (`NNNN-title.md`).

- One decision per file; ADRs are append-only (supersede, don't rewrite).
- A new dependency, significant component, or non-obvious design choice warrants an ADR.
- ADR numbers are never reused; superseded ADRs are marked, not deleted.

## Consequences

- **Positive:** decisions are discoverable and self-documenting; new contributors can read the reasoning; the `write-adr` skill has a clear home and format.
- **Tradeoff:** a small amount of ceremony per significant decision.

## Alternatives Considered

- **No formal record** (rely on commit messages / memory) — rejected: reasoning gets lost; decisions get silently reverted.
- **A single design doc** — rejected: doesn't capture per-decision context/alternatives or supersession over time.

## Related ADRs

- [ADR-0002: Workspace Mode](./0002-workspace-mode-for-monorepo.md) (a v2 decision, superseded)
- [ADR-0003: Pivot to a Repo Context-Layer Generator](./0003-pivot-to-context-layer-generator.md)

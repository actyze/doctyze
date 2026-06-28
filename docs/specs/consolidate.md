---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [doctyze/consolidate/**]
  last_verified: '2026-06-15'
---

# Spec: Consolidate

**Purpose.** Bring scattered documentation in a repo into one canonical `docs/` structure, non-destructively.

**CLI.** `doctyze consolidate [--apply] [PATH]` — without `--apply`, writes a reviewable plan and changes nothing.

## Behavior

1. **Audit** ([`audit.py`](../../doctyze/consolidate/audit.py)) — walk the repo (skipping `.git`, `node_modules`, `.archive`, `.doctyze`, …), find `.md/.mdx/.rst/.adoc` files, and classify each by path + filename heuristics into: `spec`, `adr`, `runbook`, `architecture`, `observability`, `skill`, `agent_context`, `keep_in_place`, or `stale`.
2. **Plan** ([`plan.py`](../../doctyze/consolidate/plan.py)) — map each classified doc to its canonical slot and emit an ordered `MigrationPlan` to `.doctyze/consolidation-plan.md`. ADR number collisions are resolved by renumbering duplicates (existing numbers are reserved first, so a real ADR is never renumbered).
3. **Apply** ([`apply.py`](../../doctyze/consolidate/apply.py)) — execute via `git mv` (plain-move fallback), rewrite markdown links that pointed at moved files, and skip anything already in place. Idempotent.

## Inputs / outputs
- **Input:** a repo path (default `.`).
- **Output:** `.doctyze/consolidation-plan.md` (always); with `--apply`, files relocated under `docs/` and links updated.

## Edge cases
- `README` and standard root files (`CONTRIBUTING`, `LICENSE`, …) are left in place.
- Agent-context files (`.cursor/`, `.claude/`, `AGENTS.md`) are left to `distribute`, not consolidated.
- Nothing is ever deleted — stale docs are moved to `docs/archive/`.
- Files prefixed `_` and the `.doctyze/` dir are ignored.

## Known limitation
On a **docs-only repo** (no code, deep curated doc tree) the heuristics over-reach and propose moving most files. Treat consolidation as intended for code repos with scattered docs; a docs-repo detector is a future improvement.

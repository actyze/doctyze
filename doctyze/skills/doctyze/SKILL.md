---
name: doctyze
description: Generate and maintain a complete documentation context layer for this repo. Orchestrates consolidate, bootstrap, generation, distribute, and freshness.
---
# Doctyze

Build and maintain the documentation context layer for this repository, for humans and AI agents. You (the agent) do the writing with your own model; the `doctyze` CLI handles deterministic mechanics (file moves, scaffolding, drift detection, fan-out).

## Steps
1. **Consolidate** existing scattered docs: `doctyze consolidate`, review `.doctyze/consolidation-plan.md`, then `doctyze consolidate --apply`. Non-destructive.
2. **Scaffold + plan**: `doctyze bootstrap`. Read `.doctyze/bootstrap-manifest.md`.
3. **Survey existing docs FIRST** (critical): before generating anything, read what already lives in `docs/`. If a topic is already documented — especially a large existing doc — **refresh or split it** into the canonical structure. Never write a doc that duplicates one that exists; link to or supersede it.
4. **Generate** each artifact in the manifest by running the matching skill, grounded in the actual code. Add a freshness anchor to every file you create.
5. **Distribute**: `doctyze distribute`.
6. **Keep fresh**: `doctyze watch --install`.

## Generation skills
`write-architecture` · `write-spec` · `write-adr` · `write-runbook` · `write-observability` · `write-skills`

## The freshness anchor (add to every generated doc)
```yaml
---
doctyze:
  artifact: spec            # spec|adr|runbook|architecture|observability|guide|skill
  generated_by: write-spec
  affects: [<the specific module(s) this doc describes>]
  last_verified: <YYYY-MM-DD>
---
```
**Keep `affects` narrow** — the exact files/dirs the doc is about, never `app/**` or `src/**`. Broad anchors make every doc perpetually "stale" and train readers to ignore the signal.

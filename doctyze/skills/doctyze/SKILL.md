---
name: doctyze
description: Generate and maintain a complete documentation context layer for this repo. Orchestrates consolidate, bootstrap, generation, index, distribute, and freshness.
---
# Doctyze

Build and maintain the documentation context layer for this repository, for humans and AI agents. **You (this agent) do the writing** — read the code and produce the docs with your own model.

Doctyze's deterministic operations (audit & move scattered docs, scaffold, detect stale docs, fan-out, build the index) run as the **`doctyze` CLI** — the default, zero-setup path. Invoke it with `uvx` (nothing to install, no MCP approval needed), e.g. `uvx doctyze bootstrap`. The **same** operations are *also* exposed as **MCP tools** (`consolidate_plan`, `bootstrap`, `rebuild_index`, `distribute`, `check_freshness`) when the Doctyze MCP server is connected **and enabled** in your IDE — use those only if you can't run the CLI. Both transports run identical code, so the steps below don't change. **The docs themselves are always written by you (the model) reading the code — no CLI command and no MCP tool generates prose.**

## Steps
1. **Consolidate** scattered docs — `uvx doctyze consolidate` writes a reviewable plan to `.doctyze/consolidation-plan.md` and changes nothing; review it, then `uvx doctyze consolidate --apply`. *(MCP: `consolidate_plan` → `consolidate_apply`.)* Non-destructive: moves preserve git history, nothing is deleted.
2. **Scaffold + plan** — `uvx doctyze bootstrap` *(MCP: `bootstrap`)*. It scaffolds the canonical `docs/` tree and returns a manifest of what to generate (and lists existing docs to refresh, not duplicate).
3. **Survey existing docs FIRST** — read what already lives in `docs/`. If a topic is already documented (especially a large existing doc), **refresh or split it**; never write a parallel duplicate — link to or supersede it.
4. **Generate** each artifact in the manifest by **reading the actual code** and writing the doc: feature specs, architecture + Mermaid diagrams, runbooks, observability, dev/testing skills, and ADRs for decisions already embodied in the code. Add a freshness anchor to every file (see below).
5. **Index** — `uvx doctyze index` *(MCP: `rebuild_index`)* to build the `docs/` table of contents (humans + agents navigate from `docs/index.md`).
6. **Distribute** — `uvx doctyze distribute` *(MCP: `distribute`)* to fan the skills out to agent files.
7. **Keep fresh** — run `uvx doctyze watch --install` *(MCP: `install_freshness_hook`)* once to add a warn-first pre-commit hook. Thereafter `uvx doctyze watch` *(MCP: `check_freshness`)* — which the hook runs on each commit — flags docs whose anchored code changed; regenerate those.

## Generation guidance (per artifact)
See `write-architecture` · `write-spec` · `write-adr` · `write-runbook` · `write-observability` · `write-skills`. Ground every claim in real code (cite entry points as `path:line`), be honest about stubs/bugs, and keep anchors narrow.

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

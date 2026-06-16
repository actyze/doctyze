---
name: doctyze
description: Generate and maintain a complete documentation context layer for this repo. Orchestrates consolidate, bootstrap, generation, distribute, and freshness.
---
# Doctyze

Build and maintain the documentation context layer for this repository, for both humans and AI agents. You (the agent) do the writing using your own model; the `doctyze` CLI handles deterministic mechanics (file moves, scaffolding, drift detection, fan-out).

## Steps
1. **Consolidate** existing scattered docs: run `doctyze consolidate`, review `.doctyze/consolidation-plan.md`, then `doctyze consolidate --apply`. Non-destructive.
2. **Scaffold + plan**: run `doctyze bootstrap`. Read `.doctyze/bootstrap-manifest.md`.
3. **Generate** each artifact in the manifest by running the matching skill below, grounded in the actual code. Add a Doctyze freshness anchor to every file you create.
4. **Distribute**: run `doctyze distribute` to fan the skills/rules out to agent files.
5. **Keep fresh**: run `doctyze watch --install`.

## Generation skills
`write-architecture` · `write-spec` · `write-adr` · `write-runbook` · `write-observability` · `write-skills`

## The freshness anchor (add to every generated doc)
```yaml
---
doctyze:
  artifact: spec            # spec|adr|runbook|architecture|observability|skill
  generated_by: write-spec
  source: [src/<area>/]
  affects: [src/<area>/**]  # globs that make this doc stale when changed
  last_verified: <YYYY-MM-DD>
---
```

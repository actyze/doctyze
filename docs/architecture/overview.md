---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  source: [doctyze/]
  affects: [doctyze/**, pyproject.toml]
  last_verified: '2026-06-15'
---

# Architecture Overview

Doctyze is a **deterministic Python engine** that generates and maintains a documentation context layer for any repo. It never calls an LLM: the generation work is delegated to the developer's existing IDE/CI agent (BYO-agent). The engine does discovery, file moves, scaffolding, drift detection, and distribution — all without an API key.

## The four jobs

| Job | Package | What it does (deterministically) |
|---|---|---|
| **Consolidate** | [`doctyze/consolidate/`](../../doctyze/consolidate/) | Discover scattered docs, classify them, propose a non-destructive migration plan, apply it (git-mv + link rewrite). |
| **Bootstrap** | [`doctyze/generate/`](../../doctyze/generate/) | Detect the stack, scaffold the canonical `docs/` structure with freshness anchors, optionally run CodeBoarding for diagrams, emit a generation manifest for the agent. |
| **Distribute** | [`doctyze/distribute/`](../../doctyze/distribute/) | Fan the canonical skills out to `.claude/skills`, `.cursor/rules`, and an `AGENTS.md` block. |
| **Freshness** | [`doctyze/freshness/`](../../doctyze/freshness/) | Map changed code to the docs it invalidates (via anchors + git diff), write a refresh manifest, install a warn-first pre-commit hook. |

A single **service layer** ([`doctyze/api.py`](../../doctyze/api.py)) implements each job once. The CLI ([`doctyze/cli.py`](../../doctyze/cli.py), commands `init`, `consolidate`, `bootstrap`, `distribute`, `watch`) and the MCP server ([`doctyze/mcp_server.py`](../../doctyze/mcp_server.py)) are both thin presenters over `api.py`, so the two entry points can't drift.

## The freshness anchor (the core contract)

Every generated doc carries a `doctyze:` frontmatter block declaring which code makes it stale. `affects` globs are matched against `git diff` to decide which docs a change invalidates. This is the load-bearing idea — it's how a code change maps to the *specific* docs that need refreshing (see [`doctyze/freshness/detect.py`](../../doctyze/freshness/detect.py) and [ADR-0003](decisions/0003-pivot-to-context-layer-generator.md)).

## Boundaries

- **No LLM dependency.** `pyproject.toml` has no `anthropic`/`openai`; a test enforces the package imports without them. Generation is the agent's job.
- **Adopted OSS is optional.** CodeBoarding (diagrams), ruler (fan-out), fiberplane/drift (staleness) are enhancements; each has a built-in deterministic fallback.
- **Non-destructive.** Consolidation moves preserve git history; nothing is deleted (stale docs are archived).

See the pipeline diagram in [diagrams/pipeline.md](diagrams/pipeline.md).

# Doctyze — Agent Context

This file follows the [AGENTS.md standard](https://agents.md). Context for AI agents working on the **Doctyze tool itself** (not on a repo Doctyze documents).

## What this project is

Doctyze generates and maintains a documentation context layer for any repo, any stack: it **consolidates** scattered docs, **bootstraps** specs/architecture+Mermaid/runbooks/skills from code, and **keeps them fresh** via anchors + a warn-first hook. It serves humans and AI agents.

**Core principle — BYO-agent:** Doctyze never calls an LLM or needs an API key. It ships the deterministic mechanics + the skills (playbook); the LLM is the one already in the developer's IDE/CI agent. There is intentionally no `anthropic`/`openai` dependency (a test enforces this).

**Published by** [Actyze](https://github.com/actyze) under Apache 2.0. Free OSS.

## Layout

- `doctyze/` — the Python package (deterministic engine, no LLM)
  - `cli.py` — `init`, `consolidate`, `bootstrap`, `index`, `distribute`, `watch` (thin presenters over `api.py`)
  - `consolidate/` — audit → plan → apply (non-destructive)
  - `generate/` — stack detection, structure scaffold, CodeBoarding adapter, manifest
  - `distribute/` — fan-out skills to agent files
  - `freshness/` — anchors, the affected-docs detector, regenerate, hook
  - `skills/` — **canonical** agent-run generation skills (the product surface)
  - `mcp_server.py` — MCP server (exposes the deterministic tools + serves skills as prompts). Optional transport: the `doctyze` skill defaults to the CLI (`uvx doctyze …`, no approval); MCP is the faster opt-in. See ADR-0005.
  - `setup.py` — one-command `init` wiring: installs skills + scaffolds `docs/`, and registers the MCP server in IDE project configs (optional transport)
- `plugins/doctyze/` — the Claude Code plugin (skills copied from `doctyze/skills/`, `.mcp.json`)
- `.claude-plugin/marketplace.json` — this repo is also the plugin marketplace
- `docs/architecture/decisions/` — this repo's own ADRs (MADR); see ADR-0003 for the v3 pivot
- the superseded v2 skills-first design lives in git history (not this tree; do not revive)

## Conventions

- `doctyze/skills/` is the single source of truth for skills; `plugins/doctyze/skills/` is a generated copy (`scripts/sync-plugin-skills.sh`).
- Every generated doc carries a `doctyze:` frontmatter anchor (`affects:` globs drive staleness).
- Doctyze writes working files under `.doctyze/` in target repos.
- Tests are real and must stay green (`pytest`). No phantom-module tests.
- Decisions go in `docs/architecture/decisions/` (MADR). See ADR-0003 for the v3 pivot.

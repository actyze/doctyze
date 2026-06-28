# Contributing to Doctyze

Doctyze generates and maintains a documentation context layer for any repo, using the LLM already in the developer's IDE (BYO-agent — no API key). Free and open source under Apache 2.0.

> **Note:** Doctyze is mid–v3 rewrite. The previous v2 "skills-first" design is superseded (in git history) and is **not** being developed. See `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md` for the why, and `docs/planning/` for the full plan.

## Project shape

- `doctyze/` — the Python package (deterministic engine; **no LLM, no API key**)
  - `cli.py` — `init`, `consolidate`, `bootstrap`, `index`, `distribute`, `watch`
  - `consolidate/`, `generate/`, `distribute/`, `freshness/` — the four jobs
  - `skills/` — **canonical** agent-run generation skills (the product surface)
  - `mcp_server.py` — MCP server exposing the deterministic tools
- `plugins/doctyze/` — the Claude Code plugin (skills synced from `doctyze/skills/`)
- `.claude-plugin/marketplace.json` — this repo is also the plugin marketplace
- `tests/` — real tests (`pytest`)

## Dev setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest            # all tests must pass
```

## Ground rules

1. **Never add an LLM SDK dependency.** Generation is delegated to the user's existing agent. A test enforces that the package imports without `anthropic`/`openai`.
2. **`doctyze/skills/` is the single source of truth** for skills. After editing a skill, run `scripts/sync-plugin-skills.sh` to update the plugin copy.
3. **Consolidation is non-destructive.** Moves preserve git history; nothing is deleted (stale docs are archived).
4. **Every generated doc carries a `doctyze:` freshness anchor** (`affects:` globs drive staleness).
5. **Add real tests** for new behavior. No tests against modules that don't exist.
6. **Record significant decisions** as ADRs under `docs/architecture/decisions/` (MADR).

## Good places to help

Check the open issues. High-value areas now: the `doctyze init` flow, the reusable CI action, polishing the generation skills, and additional stack/diagram support. Issues labeled `good first issue` are a good start — but confirm the issue still applies to v3 first (some v2-era issues, e.g. the per-vendor "renderer" ones, are being closed as obsolete).

## Pull requests

Branch from the active development branch, keep PRs focused, ensure `pytest` is green, and run `scripts/sync-plugin-skills.sh` if you touched skills. Be kind in reviews.

## Questions

Open a GitHub Discussion or issue.

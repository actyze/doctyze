---
doctyze:
  artifact: runbook
  generated_by: write-runbook
  affects: [pyproject.toml, .github/workflows/**, scripts/**, action.yml]
  last_verified: '2026-06-15'
---

# Runbook: Development, Test & Release

## Local setup
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Run the tests
```bash
pytest -q          # all must pass; CI runs this on py3.10 + py3.12
```
CI is defined in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

## Run Doctyze on a repo
```bash
doctyze init <path>          # one-command setup: wire MCP + install skills + scaffold
doctyze consolidate <path>   # propose; add --apply to execute
doctyze bootstrap <path>     # scaffold + manifest
doctyze index <path>         # build docs/ table of contents
doctyze distribute <path>    # fan skills to agent files
doctyze watch <path>         # flag stale docs; --install for the hook
```
`init` is the front door: it registers the Doctyze MCP server in each IDE's
project config — `.mcp.json` (Claude Code), `.cursor/mcp.json` (Cursor),
`.vscode/mcp.json` (VS Code/Copilot), plus `.codex/config.toml` (Codex) and
`.gemini/settings.json` (Gemini) when those are detected — installs the skills,
and scaffolds `docs/`. All configs are project-scoped and merge-safe. Windsurf and
Cline are global-only, so `init` detects and reports them ([`setup.py`](../../doctyze/setup.py)).

## Editing skills
`doctyze/skills/` is the **single source of truth**. After changing a skill:
```bash
./scripts/sync-plugin-skills.sh   # regenerate plugins/doctyze/skills/
```

## Release

Doctyze is published on PyPI as [`doctyze`](https://pypi.org/project/doctyze/) and
releases via **GitHub Actions Trusted Publishing** (no tokens). To cut a release:

```bash
# 1. bump the version in pyproject.toml + doctyze/__init__.py, update CHANGELOG
# 2. commit, then tag and push:
git tag -a vX.Y.Z -m "Doctyze vX.Y.Z" && git push origin vX.Y.Z
```

The tag triggers [`.github/workflows/release.yml`](../../.github/workflows/release.yml),
which builds the sdist+wheel and publishes to PyPI via OIDC. The wheel ships the
`SKILL.md` files via `package-data`. The repo itself is the Claude Code plugin
marketplace (`.claude-plugin/marketplace.json`).

## Reusable CI action
[`action.yml`](../../action.yml) is a composite GitHub Action that installs Doctyze and runs the freshness check on PRs (use `actions/checkout` with `fetch-depth: 0` so `git diff` sees the base).

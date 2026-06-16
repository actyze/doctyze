---
doctyze:
  artifact: runbook
  generated_by: write-runbook
  source: [pyproject.toml]
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
doctyze init <path>          # scaffold + install skills
doctyze consolidate <path>   # propose; add --apply to execute
doctyze bootstrap <path>     # scaffold + manifest
doctyze distribute <path>    # fan skills to agent files
doctyze watch <path>         # flag stale docs; --install for the hook
```

## Editing skills
`doctyze/skills/` is the **single source of truth**. After changing a skill:
```bash
./scripts/sync-plugin-skills.sh   # regenerate plugins/doctyze/skills/
```

## Build & release (deployment)
```bash
pip wheel . -w dist --no-deps     # build the wheel (ships skills via package-data)
```
Release steps (see `docs/planning/DOCTYZE_V3_BUILD_PLAN.md`):
1. Build & verify the wheel (`SKILL.md` files must be present inside it).
2. Publish to PyPI (`doctyze`) — *pending account/token*.
3. Push the repo so the Claude Code marketplace (`.claude-plugin/marketplace.json`) resolves; submit to `claude-plugins-community`.

## Reusable CI action
[`action.yml`](../../action.yml) is a composite GitHub Action that installs Doctyze and runs the freshness check on PRs (use `actions/checkout` with `fetch-depth: 0` so `git diff` sees the base).

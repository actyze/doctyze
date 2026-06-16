# Doctyze

**Generate and maintain a complete documentation context layer for any repo — using the LLM already in your IDE.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-supported-green)](https://agents.md)
[![Status](https://img.shields.io/badge/status-v3%20in%20development-yellow)]()

---

## What it does

Point Doctyze at any existing repository, any tech stack. It:

1. **Consolidates** scattered docs (loose READMEs, wiki notes, stray design files) into one canonical `docs/` structure — non-destructively.
2. **Bootstraps** the full SDLC context layer from the code: specs, architecture docs + Mermaid diagrams, dev/testing skills, runbooks, deployment & observability docs.
3. **Maintains** it — when code changes, it flags the docs that are now stale and your agent refreshes them.

The result serves both humans and AI coding agents (`AGENTS.md`, `.cursor/rules`, Claude Code skills, MCP).

## Bring your own agent (no API key)

Doctyze does **not** call an LLM or need an API key. It brings the playbook (skills) and the deterministic mechanics (consolidation, drift detection, fan-out); the **LLM is the one already in your IDE** (Cursor / Claude Code / Copilot) or your CI agent. In your editor you just run the Doctyze skill and your existing agent does the generation.

## Commands

```bash
doctyze init                    # guided front door: scaffold + install skills + next steps
doctyze consolidate [--apply]   # scattered docs -> canonical docs/ (propose, then apply)
doctyze bootstrap               # scaffold structure + hand a generation manifest to your agent
doctyze distribute              # fan skills out to .claude/skills, .cursor/rules, AGENTS.md
doctyze watch [--install]       # flag docs whose anchored code changed (warn-first pre-commit hook)
```

Generated docs carry a freshness **anchor** declaring which code makes them stale:

```yaml
---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/payments/**]
  last_verified: 2026-06-15
---
```

## Status

v3 is a ground-up rewrite (the v2 skills-first design is superseded; in git history). The engine — consolidate, bootstrap, distribute, watch — is built and tested (`pytest`), and validated end-to-end on a real service repo. The distribution/release step (PyPI package, Claude Code plugin, CI action) is in progress; until then, run from source:

```bash
pip install -e .
doctyze --help
```

See `docs/planning/DOCTYZE_V3_PLAN.md`, `docs/planning/DOCTYZE_V3_BUILD_PLAN.md`, and `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md`.

## License

Apache 2.0. Free and open source for everyone.

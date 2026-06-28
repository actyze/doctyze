# Doctyze

**Generate and maintain a complete documentation context layer for any repo — using the LLM already in your IDE.**

[![PyPI](https://img.shields.io/pypi/v/doctyze.svg)](https://pypi.org/project/doctyze/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-supported-green)](https://agents.md)

---

## What it does

Point Doctyze at any existing repository, any tech stack. It:

1. **Consolidates** scattered docs (loose READMEs, wiki notes, stray design files) into one canonical `docs/` structure — non-destructively.
2. **Bootstraps** the full SDLC context layer from the code: specs, architecture docs + Mermaid diagrams, decisions (ADRs), runbooks, observability, dev/testing skills.
3. **Maintains** it — when code changes, it flags exactly which docs are now stale and your agent refreshes them.

The result serves both humans and AI coding agents (`AGENTS.md`, `.cursor/rules`, Claude Code skills, MCP).

## Bring your own agent — no API key

Doctyze does **not** call an LLM or need an API key. It brings the playbook (skills) and the deterministic mechanics (consolidation, drift detection, fan-out); the **LLM is the one already in your IDE** (Cursor / Claude Code / Copilot) or your CI agent. You run the Doctyze skill and your existing agent does the writing.

## Quick start

**Install** (Python ≥ 3.10):

```bash
pip install doctyze
```

> Claude Code users can instead install the plugin (bundles the skills + MCP server):
> ```
> /plugin marketplace add actyze/doctyze
> /plugin install doctyze@doctyze
> ```

**Run it on your repo:**

```bash
cd your-repo
doctyze init                  # detect stack, scaffold docs/, install the Doctyze skills
doctyze consolidate --apply   # organize existing scattered docs (review the plan first)
```

**Generate the docs** — in your IDE (Cursor / Claude Code), run the **`doctyze`** skill. Your agent reads the code and writes the specs, diagrams, runbooks, ADRs, and skills, grounded in the real code. Then:

```bash
doctyze index                 # build the docs/ table of contents (docs/index.md)
doctyze watch --install       # keep docs fresh on every commit (warn-first hook)
```

## Commands

```bash
doctyze init                    # guided front door: scaffold + install skills + next steps
doctyze consolidate [--apply]   # scattered docs -> canonical docs/ (propose, then apply)
doctyze bootstrap               # scaffold structure + hand a generation manifest to your agent
doctyze index                   # build docs/ navigation (table of contents) for humans + agents
doctyze distribute              # fan skills out to .claude/skills, .cursor/rules, AGENTS.md
doctyze watch [--install]       # flag docs whose anchored code changed (warn-first pre-commit hook)
```

Generated docs land in a canonical `docs/` tree — `specs/`, `architecture/{diagrams,decisions}/`, `runbooks/`, `observability/`, `guides/`, `skills/` — with a `docs/index.md` table of contents. Each generated doc carries a freshness **anchor** declaring which code makes it stale:

```yaml
---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/payments/**]
  last_verified: 2026-06-22
---
```

## How it's built

A deterministic Python engine (no LLM, no key) + agent-run generation skills. CLI and MCP server are thin presenters over one service layer. See `CONTRIBUTING.md`, and `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md` for the design rationale.

## License

Apache 2.0. Free and open source for everyone.

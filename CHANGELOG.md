# Changelog — Doctyze

Format based on [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

## [0.3.0] — 2026-06-16 (v3 rewrite, first PyPI release)

A ground-up rewrite. v3 replaces the v2 "skills-first, paste-by-hand + enforce"
design (now in git history) with a **context-layer generator** that
adopts existing OSS and delegates LLM work to the developer's existing agent
(BYO-agent — no API key). See `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md`.

### Added
- Installable `doctyze` package (no forced LLM dependency).
- `doctyze consolidate` — audit → plan → apply scattered docs into the canonical
  `docs/` structure; non-destructive (git-mv + link rewrite), ADR-collision
  renumbering, idempotent.
- `doctyze bootstrap` — stack detection, canonical-structure scaffold with
  freshness anchors, optional CodeBoarding diagrams (graceful), agent manifest.
- `doctyze distribute` — fan canonical skills out to `.claude/skills`,
  `.cursor/rules`, and an idempotent `AGENTS.md` block.
- `doctyze watch` — the affected-docs detector (maps changed code to stale docs
  via anchors + git diff), refresh manifest, warn-first pre-commit hook.
- 7 agent-run generation skills (`doctyze`, `write-spec`, `write-adr`,
  `write-architecture`, `write-runbook`, `write-observability`, `write-skills`).
- `doctyze index` — deterministic navigation: per-section `index.md` tables + a
  top-level `docs/index.md` table of contents (for humans and agents).
- A `docs/guides/` section; coding/testing standards route there, not `specs/`.
- Claude Code plugin + marketplace scaffolding; MCP server (incl. an index tool).

### Changed (post-validation refinements)
- Generation skills now **read existing docs first** (refresh/split, never
  duplicate) and require **narrow `affects:` anchors** (the specific module, not
  `app/**`) with a grounded depth bar (entry point `file:line`, honest about stubs).
- Bootstrap manifest lists existing docs so generation coordinates with consolidation.
- Dropped the decorative `source` anchor field (engine only uses `affects`).
- Consolidation fixes: `docs/architecture/diagrams/` treated as canonical;
  broader observability/runbook keyword routing.

### Validated
- End-to-end on a clean snapshot of a real Java/Spring service. All tests green.

### Removed
- All of v2 (renderer/vendor system, 23-skill catalog, broken CLI) removed (in git history).

## [2.0.0] — Superseded
The v2 skills-first design. Never shipped. (In git history.)

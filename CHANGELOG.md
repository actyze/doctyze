# Changelog — Doctyze

Format based on [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

## [0.3.0] — Unreleased (v3 rewrite)

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
- Claude Code plugin + marketplace scaffolding; MCP server.

### Validated
- End-to-end on a clean snapshot of a real Java/Spring service. All tests green.

### Removed
- All of v2 (renderer/vendor system, 23-skill catalog, broken CLI) removed (in git history).

## [2.0.0] — Superseded
The v2 skills-first design. Never shipped. (In git history.)

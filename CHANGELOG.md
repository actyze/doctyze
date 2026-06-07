# Changelog

All notable changes to Doctyze are documented here. The format is loosely
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Community-product files: `CODE_OF_CONDUCT.md` (adopts Contributor
  Covenant v2.1 by reference), `SECURITY.md` with vulnerability
  reporting policy.
- Canonical skill `docs/skills/check-and-update-adrs.md`: read every
  relevant existing ADR before research; write an ADR when research
  finishes. Propagated to both stack templates and the worked example.
- Issue templates: bug report, feature request, documentation issue,
  new vendor renderer.
- PR template with the Doctyze cleanup checklist.
- Discussion templates: Show & Tell, Ideas.
- `FUNDING.yml` and CHANGELOG.

### Changed
- **Renamed** `pr-review-action/` → `doc-guard-action/` and
  `doctyze-review.yml` → `doctyze-doc-guard.yml` across all templates
  and the worked example. The action's purpose is to be a
  **documentation-coupling guard** that runs alongside existing PR
  review agents (CodeRabbit, Greptile, Qodo, Bito, Copilot Code
  Review, internal copilots) — not to replace them. README and action
  README now describe this explicitly with side-by-side workflow
  examples.

## [0.1.0] — 2026-06-06

### Added
- LLM-driven placeholder extraction. `doctyze init` now fills
  `{{PLACEHOLDER}}` tokens (e.g., `{{SERVICE_NAME}}`,
  `{{ONE_PARAGRAPH_PURPOSE}}`) with content extracted from the repo.
- Pluggable LLM backends: Claude (`anthropic`), OpenAI, Ollama (local /
  air-gapped), and a no-op backend that leaves placeholders as 🔴 GAP
  markers when no credentials are configured.
- Auto-detection of LLM backend from environment variables.
- 7 new tests covering the extractor + placeholder substitution.

### Fixed
- `doctyze render --check` now catches stale content, not just missing
  files (uses a temp shadow tree to byte-compare expected vs on-disk
  output).

## [0.0.2] — 2026-06-06

### Added
- **Canonical source of truth model.** `docs/skills/*.md` and
  `docs/runbooks/*.md` are the single canonical source. Vendor files
  (`.claude/skills/`, `.cursor/rules/`, `.github/copilot-instructions.md`,
  `.windsurfrules`, `.holmes/runbooks/`) are now **generated** by
  pluggable renderers.
- `doctyze render` CLI command (with `--check`, `--target=<vendor>`,
  `--list`, `--dry-run`).
- Five vendor renderers: Claude, Cursor, Copilot, Windsurf, HolmesGPT.
- `.doctyze.yaml` gains `agent_targets:` config block.
- PR-render workflows: drift-check on PR + auto-render on push to main.
- First worked example: `examples/python-fastapi-orders/` — a small
  FastAPI service with 3 hand-authored ADRs (including the load-bearing
  fail-open pricing decision), 2 canonical skills, 1 runbook with
  frontmatter, all 5 vendor renderings, all 3 workflows.
- pytest suite: 20 tests covering the frontmatter parser + all 5
  renderers.
- CI workflow on push/PR (Python 3.11 + 3.12 matrix).

### Removed
- Vendor-specific subdirectories from templates (replaced by generation).
- Empty placeholder directories from the Day-1 scaffold
  (`extractors/`, `pr-review-action/src/`, several unused subdirs).
- `skills-library/` (was byte-identical to
  `templates/{modern,legacy}/docs/skills/` and not referenced by any
  code).
- Dead code in `scaffolder.py` (`llm` param, `_classify` branches for
  paths templates no longer contain).

## [0.0.1] — 2026-05-21

### Added
- Initial Doctyze scaffold.
- CLI: `init`, `verify`, `pr-bot install`, `interview-prep`, `ingest`,
  `mcp-serve`.
- Stack detector covering 11 stacks (Java/Spring, Python, Node/React,
  Go, COBOL, ABAP, IBM i RPG, VB6, .NET Framework, PowerBuilder, Delphi).
- Modern + legacy stack templates.
- Skeleton GitHub Action for PR review.
- `AGENTS.md`, `LICENSE` (Apache 2.0), `NOTICE`, `CONTRIBUTING.md`.

[Unreleased]: https://github.com/actyze/doctyze/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/actyze/doctyze/releases/tag/v0.1.0
[0.0.2]: https://github.com/actyze/doctyze/releases/tag/v0.0.2
[0.0.1]: https://github.com/actyze/doctyze/releases/tag/v0.0.1

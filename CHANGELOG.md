# Changelog — Doctyze

Format based on [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Opt-in CI freshness gate.** `doctyze watch --exit-code` exits non-zero when docs are
  stale, and the GitHub Action gains a `fail-on-stale` input (default `false`). Lets teams
  make stale docs a required merge check — *through Doctyze*, not bespoke scripting. Default
  stays warn-first, and the **local pre-commit hook stays warn-only** (a hook can't
  regenerate a doc, so blocking the commit just trains `--no-verify`). Recommendation +
  rationale documented as best practice in the README and [ADR-0006](docs/architecture/decisions/0006-opt-in-ci-freshness-gate.md)
  (amending ADR-0004).
- **`doctyze watch --base <ref>`** — diff against a git ref (e.g. `origin/main`) instead of
  the working tree. **Required for CI:** a clean CI checkout has no working-tree diff, so
  without `--base` the check silently reported "fresh" and never fired on a PR. The GitHub
  Action exposes a matching `base` input; the CLI runs in any CI (GitLab/Jenkins/…), with
  the Action being just a convenience wrapper. README documents GitHub + GitLab examples and
  the `fetch-depth: 0` requirement.

## [0.3.3] — 2026-07-02

### Changed
- **CLI is now the default path for the `doctyze` skill; MCP is an optional transport.**
  The deterministic steps (consolidate/bootstrap/index/distribute/freshness) are the same
  code whether run via the `doctyze` CLI (`uvx doctyze …`) or the MCP tools — and doc
  generation is always done by the model, never by either. The skill now defaults to the
  CLI, which needs **no approval**, and treats the MCP tools as a faster opt-in. This
  removes the first-run wall where `/doctyze` found no tools because the project-scoped
  `.mcp.json` server hadn't been approved yet (even though `claude mcp list` showed it
  "Connected").

### Fixed
- **Onboarding honesty about MCP approval.** `init` used to say only "reload your IDE,"
  but most assistants gate a project `.mcp.json` server behind an explicit approval before
  its tools load. `init` output, the `wire_mcp` docstring, and the README now (a) make the
  CLI the no-approval default and (b) spell out the one-time approval step for anyone who
  wants the MCP tools (Claude Code: `/mcp` → Enable; Cursor: Settings → MCP; VS Code:
  Start the server).

## [0.3.2] — 2026-07-01

Broader IDE coverage.

### Added
- `doctyze init` now wires more assistants, with **detection** (best-effort — binary
  on PATH or config dir — so it only writes configs for tools you actually have):
  **Codex** (`.codex/config.toml`, TOML `[mcp_servers.doctyze]`) and **Gemini CLI**
  (`.gemini/settings.json`), alongside Claude Code, Cursor, and VS Code/Copilot.
- Detects **Windsurf** and **Cline** (which only support a *global* MCP config) and
  prints exactly how to add the server there; both already read the installed
  `AGENTS.md`, so their playbook is covered. Config paths verified against each
  tool's official docs.

## [0.3.1] — 2026-07-01

Onboarding + cross-IDE parity.

### Added
- **One-command setup:** `uvx doctyze init` now wires the Doctyze MCP server into
  your IDE configs (`.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json` — project-
  scoped, merge-safe), installs the skills, and scaffolds `docs/`. Reload your IDE
  and invoke the `doctyze` prompt.
- **MCP prompts:** the server now serves each skill (the `doctyze` orchestrator +
  generators) as an MCP *prompt*, so any MCP client (Cursor, Copilot, Windsurf,
  Claude Code) gets the full guided playbook on the first run — not just the tools.
- **`install_freshness_hook` MCP tool** so the assistant can set up the pre-commit
  hook without a terminal.

### Fixed
- Plugin/MCP launch command (`uvx --from "doctyze[mcp]" doctyze-mcp`) — the server
  previously couldn't start because `mcp` is an optional extra.
- The pre-commit hook falls back to `uvx doctyze watch --staged`, so it runs even
  with no global `pip install` (the MCP-only setup).

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

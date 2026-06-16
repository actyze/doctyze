# ADR-0003: Pivot to a Repo Context-Layer Generator (Adopt-and-Enhance)

**Status:** 🟢 CONFIRMED
**Date:** 2026-06-14
**Deciders:** Rohit Mangal
**Consensus:** ✅ Approved
**Supersedes:** the v2 skills-first direction (incl. ADR-0002 Workspace Mode, which assumed the v2 scaffolder/renderer architecture)

## Problem / Context

A grounded, cited review this session found two things that invalidate the v2 plan:

1. **Most of what v2 built already exists** — code-coupled docs + CI enforcement = Swimm; AI docs-sync = Mintlify/DeepDocs/Dosu; "block PR if docs not updated" = Danger JS + Vale + CODEOWNERS (free OSS); agent-context generation = Nx. The v2 "paste skills to hand-write docs + enforce" thesis is largely re-implementing existing tools.
2. **v2 does not run** — the CLI can't be installed (optional `anthropic` imported unconditionally; entry point `doctyze.cli:main` missing; wheel packages a nonexistent `src/doctyze`), version is `0.0.2` while the CHANGELOG claims `v2.0.0-rc.1`, tests are red against phantom modules, `examples/` is empty, `NamespaceManager` is dead code, and ~18 of 23 skills are stubs.

The project is **free and open source** (no monetization goal), so the only competitive filter that applies is **do not re-implement what already exists for free**.

## Decision

Pivot Doctyze to a **repo context-layer generator and maintainer**, built by **adopting and enhancing existing OSS** rather than rebuilding it.

**What Doctyze does** (any repo, any stack), serving humans and AI agents:
- **Consolidate** scattered existing docs into a canonical `docs/` structure (non-destructive).
- **Bootstrap** the full SDLC artifact set from code: specs, architecture docs + Mermaid architecture/integration diagrams, dev/testing skills & rules, runbooks + incident/observability docs, deployment docs.
- **Maintain** all of it fresh via pre-commit hooks and PR-review agents.

**Adopt (don't rebuild):** CodeBoarding (Mermaid diagrams), DeepWiki-Open (prose patterns — harvest only), ruler (agent-file fan-out), fiberplane/drift (staleness detection), qodo/pr-agent + Danger JS (PR agent), pre-commit/lefthook (hooks). Maintenance health verified via GitHub API on 2026-06-14 (recorded in `docs/planning/DOCTYZE_V3_PLAN.md`); hard-depend only on the healthy tier, keep fallbacks for the solo/young projects (drift, ruler).

**Build (the defensible core, no OSS does it):** grounded spec extraction, repo→skills/rules generation, scattered-doc consolidation, and the freshness loop (drift → affected artifact → regenerate).

### Delivery model: BYO-agent (leverage the existing LLM, never force a key)
Developers already have an LLM in their IDE (Cursor/Claude Code/Copilot) and orgs have an agent in CI. Doctyze must not make them install a CLI to run an LLM or provide a second API key. **Doctyze brings the playbook; the existing agent brings the LLM.** It ships, in priority order: (1) **agent-native skills/rules** the existing agent executes with its own LLM (added once per repo, distributed to all formats via ruler); (2) an optional **MCP server** exposing deterministic tools to any agent; (3) a **deterministic helper** (doc discovery, git-mv consolidation, drift detection, fan-out, hook/CI install) that needs no LLM. LLM work is always borrowed — the IDE agent (interactive) or the org's CI agent (headless, using existing credentials). Doctyze itself never requires `ANTHROPIC_API_KEY`. *This rehabilitates v2's one good idea (skills the agent runs) while fixing its mistakes (few real generation skills, not 23 paste-by-hand stubs).*

### The four locked sub-decisions
1. **Engine language: Python — as a deterministic helper + MCP server, not an LLM caller.** Generation is delegated to the existing agent (see Delivery model above); the Python side does only the no-LLM mechanics and exposes MCP tools. Salvaged v2 skill bodies become the agent-run generation skills.
2. **Doc↔code binding for freshness: explicit frontmatter anchors** (e.g. `affects: [src/payments/**]`) plus drift's AST anchors. Deterministic by default; LLM inference is an optional helper.
3. **First proving repo: a representative service repo.** Prove the full loop end-to-end on one real workspace repo before going wide.
4. **Consolidation aggressiveness: propose-and-approve, non-destructive.** Always emit a migration plan for human approval; preserve git history; archive (never delete) stale docs.

## Consequences

### ✅ Positive
- Stops re-implementing Swimm/Mintlify/Danger/Nx; ~two-thirds of the stack is adopted OSS.
- Sharp, buildable scope: four connective-intelligence components nobody else ships together.
- Same context layer serves humans and AI agents (via ruler fan-out to CLAUDE.md/AGENTS.md/.cursor/MCP/skills).
- Consolidation makes Doctyze useful on day one for repos with scattered, pre-existing docs.

### ⚠️ Tradeoffs / risks
- **Dependency risk:** fiberplane/drift (3 months old, 3 contributors, Zig) and ruler (solo-maintained) — mitigated by keeping simple fallbacks (Danger JS gate; reimplement fan-out).
- **Spec hallucination:** generated specs must be grounded in CodeBoarding's static analysis, not free-form LLM prose.
- **Polyglot subprocess orchestration** (Python engine calling TS/Zig tools) adds operational surface.
- **Throwaway:** most of the v2 codebase is archived, not salvaged.

## Alternatives Considered

1. **Polish and ship v2 skills-first** — *Rejected:* re-implements existing tools; doesn't run; UX polish would be lipstick on an unshippable, undifferentiated product.
2. **Rebuild everything from scratch** — *Rejected:* diagrams, agent fan-out, hooks, PR-agents, and staleness detection all have healthy OSS bases; rebuilding them is wasted effort.
3. **Build on a docs platform (GitBook/Confluence/Forge) or fork Swimm** — *Rejected:* the differentiated half (generation + freshness) is platform-independent; Swimm isn't OSS; platform lock-in/churn.
4. **Standalone "affected-docs" primitive only** — *Rejected as too narrow:* it's just the freshness half; the real goal is the full context layer (generation + consolidation + freshness).
5. **Pure compose-OSS bundle** (Danger+Vale+pre-commit preset) — *Rejected as the product:* adds nothing over the free recipe; the intelligence layer is the value, the glue is plumbing.

## Implementation Plan

**Build the tool first; a representative service repo is the test fixture, used only at the end.** Detailed engineering plan in `docs/planning/DOCTYZE_V3_BUILD_PLAN.md`. Milestones (all engine milestones complete, tests green):
- [x] **M0** — clean-rewrite scaffold (`doctyze/` installs cleanly), archive v2, salvage 5 skills
- [x] **M1** — `consolidate` (audit → plan → apply, non-destructive, ADR-renumber, idempotent)
- [x] **M2** — `bootstrap` (stack detect + scaffold + CodeBoarding adapter + manifest + 7 generation skills)
- [x] **M3** — `distribute` (fan-out) + `watch` (affected-docs detector via anchors+git, warn-first hook)
- [x] **M4** — validated end-to-end on a clean snapshot of a representative service repo
- [ ] **Release** — PyPI + Claude Code plugin/marketplace + CI action (distribution, not engine)

## References
- `docs/planning/DOCTYZE_V3_PLAN.md` — full plan, adopt/build map, maintenance-health table
- Grounded review & strategic options (internal research from this session)
- [ADR-0002: Workspace Mode](./0002-workspace-mode-for-monorepo.md) (superseded direction)
- Adopted OSS: CodeBoarding, AsyncFuncAI/deepwiki-open, intellectronica/ruler, fiberplane/drift, qodo-ai/pr-agent, pre-commit, evilmartians/lefthook

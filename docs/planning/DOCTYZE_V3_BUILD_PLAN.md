# Doctyze v3 — Build Plan (the tool itself)

**Author:** Opus 4.8 · **Date:** 2026-06-14
**Companion to:** `DOCTYZE_V3_PLAN.md` (product/strategy) and `ADR-0003` (decision record).
**Scope of this doc:** the *engineering* plan — how Doctyze itself is built. a representative service repo is the **test fixture**, not part of the build; we run the finished tool against it at the end (M4). Nothing is executed on it before then.

---

## Delivery model (most important constraint)

**Doctyze brings the playbook; the developer's existing agent brings the LLM.** Developers already have an LLM in their IDE (Cursor/Claude Code/Copilot) or an agent in CI. Doctyze must NOT make them install a CLI just to run an LLM, nor provide a second API key. It leverages the existing agent/LLM in both IDE and interface-less modes.

What Doctyze ships, in priority order:
1. **Agent-native skills / rules** (primary surface) — instructions the *existing* agent executes (consolidate, generate, regenerate) using its own LLM. Distributed to all formats (Claude Code skill, `.cursor/rules`, `AGENTS.md`, Copilot) via ruler. Added once per repo (committed), so the whole team gets it. **No key, no separate LLM.**
2. **MCP server** (optional) — exposes Doctyze's deterministic tools so any MCP-capable agent (IDE or CI) can call them. No LLM of its own.
3. **Deterministic helper** (no LLM) — doc discovery, git-mv consolidation, drift detection, ruler fan-out, hook/CI-action install. Runs anywhere with no key.

**LLM work is always borrowed** from the environment: the IDE agent (interactive) or the org's existing CI agent (headless, using the org's existing credentials). Doctyze itself never requires `ANTHROPIC_API_KEY`. (This revises the earlier "Python engine that calls Anthropic" framing — the engine is now deterministic + MCP; generation is delegated to the existing agent.)

Modes:
- **IDE:** developer asks their agent "set up doctyze" / runs a `/doctyze` command → their agent does the generation. Zero install of an LLM, zero key.
- **Interface-less (CI):** a CI action runs the deterministic parts (consolidate/drift/distribute) with no LLM, and delegates generation/regeneration to the org's existing CI agent.

## 0. Rewrite decision

**Clean rewrite in a new package; archive v2 wholesale.** v2 doesn't install/run, is a different paradigm (paste-skills-to-hand-write vs. generate-and-maintain), and most of it is stubs. Refactoring it costs more than it saves.

- **New package:** `doctyze/` (replaces `cli/doctyze/`). Python (per ADR-0003 decision #1).
- **Remove:** delete all of `cli/` and the v2 skill catalog/renderer (kept in git history).
- **Salvage (only):** the 5 real skill bodies (`write-spec`, `write-adr`, `write-runbook`, `update-openapi`, `write-investigation`) → become generator prompts under `doctyze/prompts/`; the artifact taxonomy → the canonical `docs/` structure; the ADR convention → unchanged.

---

## 1. Package structure

```
doctyze/
├── cli.py                # entrypoint: 3 commands (consolidate, bootstrap, watch)
├── config.py             # .doctyze.yaml model + canonical docs/ taxonomy
├── model.py              # core types: Artifact, DocFile, MigrationPlan, Anchor, Finding
│
├── consolidate/          # JOB 1 — scattered docs → canonical structure (WE BUILD)
│   ├── audit.py          #   discover every doc (md/rst/adoc/wiki/loose), classify
│   ├── plan.py           #   map each → taxonomy slot; emit MigrationPlan (git mv ops)
│   └── apply.py          #   non-destructive apply: git mv, archive stale, fix links
│
├── generate/             # JOB 2 — generation GLUE (deterministic only; LLM = existing agent)
│   ├── architecture.py   #   optional CodeBoarding hook for high-fidelity diagrams (headless)
│   └── adapters/         #   thin wrappers: codeboarding.py (optional), deepwiki.py
│
├── distribute/           # JOB 2.5 — one source → all agent files (ADOPT, deterministic)
│   └── ruler.py          #   wraps `ruler` → CLAUDE.md/AGENTS.md/.cursor/MCP/skills
│
├── freshness/            # JOB 3 — keep it fresh (deterministic detect + delegate regen)
│   ├── anchors.py        #   frontmatter `affects:` schema; bind docs↔code
│   ├── detect.py         #   wraps fiberplane/drift (+ Danger JS fallback) — NO LLM
│   └── regenerate.py     #   asks the existing agent to refresh the affected artifact
│
├── mcp_server.py         # exposes the deterministic tools to any MCP-capable agent
├── skills/               # THE PRODUCT SURFACE — generation playbooks the agent runs
│   ├── consolidate.md    #   (uses the deterministic audit/plan/apply tools)
│   ├── write-spec.md     #   salvaged + reworked v2 bodies, now grounded generators
│   ├── write-architecture.md  #   (agent writes Mermaid from code; CodeBoarding optional)
│   ├── write-skills.md   #   repo → dev/testing skills & rules
│   └── write-runbook.md  #   runbooks + deploy + observability
└── tests/                # real unit tests + service-repo integration fixture (M4)
```

---

## 2. The three jobs (each is a skill the agent runs, backed by deterministic tools)

> Each job below exists as (a) an **agent skill** (primary — the existing IDE/CI agent runs it, doing all LLM steps) and (b) **deterministic tools/CLI** for the mechanical, no-LLM parts (file moves, drift, fan-out) that the skill or CI calls. Steps marked *(agent)* use the developer's existing LLM; steps marked *(deterministic)* need no key. An optional `doctyze init` skill chains all three as the guided front door.

**`doctyze consolidate [--apply]`** (Job 1)
1. `audit`: walk the repo, find every doc artifact (root loose files, `docs/`, `wiki/`, scattered READMEs, vendor agent files). Classify each (spec / ADR / runbook / architecture / stale / agent-context / keep-in-place) using heuristics + one LLM pass.
2. `plan`: map each to a canonical taxonomy slot; detect collisions (e.g. duplicate ADR numbers); produce a **MigrationPlan** = an ordered list of `git mv` / archive / link-fix operations, written to `docs/_consolidation-plan.md` for review.
3. Without `--apply`: stop (propose-and-approve, ADR-0003 #4). With `--apply`: execute via `git mv` (history-preserving), move stale → `docs/archive/`, rewrite internal links. Idempotent.

**`doctyze bootstrap [--only specs,architecture,...]`** (Job 2)
1. Run CodeBoarding → `docs/architecture/` + Mermaid diagrams.
2. Spec extractor → `docs/specs/<feature>.md`, grounded in CodeBoarding's component graph (no free-form hallucination).
3. Skills generator → `docs/skills/` + rules (detect stack, test frameworks, conventions).
4. Runbook/deploy/observability generator (uses salvaged prompts + CI/IaC config).
5. Every generated file gets frontmatter anchors (`generated_by`, `source`, `affects`, `last_verified`).
6. Call `distribute` → fan out to agent files via ruler.

**`doctyze watch [--install]`** (Job 3)
- `--install`: install a pre-commit hook (pre-commit/lefthook) + a qodo/pr-agent config.
- On change: `detect` (drift) flags which anchored docs went stale → in pre-commit, warn/block; in PR, comment → `regenerate` refreshes just the affected artifact and proposes the diff.

---

## 3. Key data model

**Canonical taxonomy** (`docs/`): `specs/`, `architecture/{overview,diagrams/,decisions/}`, `runbooks/`, `observability/`, `skills/` + `rules/`, `archive/`.

**Doc frontmatter anchor** (the freshness contract — ADR-0003 #2):
```yaml
---
doctyze:
  artifact: spec            # spec | adr | runbook | architecture | skill | ...
  generated_by: specs       # which generator owns regeneration
  source: [src/payments/]   # code this doc describes
  affects: [src/payments/**, pom.xml]   # globs that make this doc stale
  last_verified: 2026-06-14
---
```
Explicit + deterministic; drift's AST anchors layer on top; LLM inference is an optional fallback.

---

## 4. Orchestration of adopted OSS (how Python calls them)

| Adopted | Invocation | Failure fallback |
|---|---|---|
| CodeBoarding | Python import or subprocess (it's Python) | required for diagrams; degrade to "no diagrams" |
| ruler | `npx @intellectronica/ruler` subprocess | reimplement minimal fan-out (small) |
| fiberplane/drift | binary subprocess | Danger JS "did affected doc change?" gate |
| qodo/pr-agent | CI (GitHub Action / pipeline config we emit) | Danger JS comment |
| pre-commit / lefthook | generate hook config | plain git hook script |

All external tools are **optional at runtime** and lazily invoked — Doctyze's own commands must import and run with none of them installed (fixing v2's #1 bug: never import an optional dep at module top level).

---

## 5. Build milestones — STATUS (all engine milestones DONE, tests green)

- **M0 — Scaffold & archive. ✅ DONE.** New `doctyze/` package installs cleanly (fixed v2's 3 packaging bugs; no forced LLM dep), v2 archived, 5 skills salvaged.
- **M1 — `consolidate`. ✅ DONE.** audit → plan → apply, non-destructive (git-mv + link rewrite), ADR-collision renumbering, idempotent.
- **M2 — `bootstrap`. ✅ DONE.** stack detect + canonical-structure scaffold (anchored indexes) + CodeBoarding adapter (graceful) + manifest + 7 agent-run generation skills.
- **M3 — `distribute` + `watch`. ✅ DONE.** built-in fan-out (.claude/skills, .cursor/rules, AGENTS.md) + the affected-docs detector (anchors + git diff, our own primitive) + refresh manifest + warn-first pre-commit hook.
- **M4 — End-to-end. ✅ DONE.** Validated on a clean `git archive` snapshot of a real Java/Spring service (22 scattered docs → 14 consolidated; java+js detected; 7 skills fanned out; a change to a source file correctly flagged the anchored spec stale). Locked as a synthetic integration test (`test_end_to_end.py`).

Each milestone shipped with real tests (no phantom-module tests this time).

### Distribution / Release (in progress — the "how Sara installs it" step)
- [x] Packaging ready — skills ship in the wheel (package-data, verified); `doctyze` + `doctyze-mcp` entry points
- [x] MCP server implemented (lazy `mcp` import; tools: consolidate/bootstrap/distribute/check_freshness)
- [x] Claude Code plugin + marketplace scaffolded per official schema (`.claude-plugin/marketplace.json`, `plugins/doctyze/`); skills synced via `scripts/sync-plugin-skills.sh`
- [ ] **Publish to PyPI** (`doctyze`) — needs PyPI account/token; not done
- [ ] **Push to `github.com/actyze/doctyze`** so the marketplace is reachable; submit to `claude-plugins-community`
- [ ] `doctyze init` guided command that commits skills into the repo (zero-setup for teammates)
- [ ] reusable CI action (GitHub Action / Azure template)
- [ ] polish the concise generation skills (`write-adr` etc.) before public release

---

## 6. Definition of done (v3 MVP)
A clean-installing `doctyze` that, on any repo: consolidates scattered docs into a reviewed canonical structure, generates specs + architecture + Mermaid + skills + runbooks grounded in the code, fans them out to AI-agent files, and flags+regenerates the right doc when code changes — demonstrated end-to-end on a real service repo.

---

## 7. Open question for this plan
**M0 archive scope:** archive *all* of v2 `cli/` immediately (clean slate, my lean), or keep v2 runnable-ish alongside the new package during the rewrite? Lean: archive immediately — v2 doesn't run anyway, so there's nothing to preserve operationally.

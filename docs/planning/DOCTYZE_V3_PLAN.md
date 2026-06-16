# Doctyze v3 — Plan: The Repo Context Layer

**Author:** Opus 4.8 · **Date:** 2026-06-14
**Supersedes:** the v2 skills-first platform (see "Current State" below).
**Grounded in:** ten cited research streams from this session.

---

## 1. What Doctyze is (the goal)

**Doctyze generates and maintains a complete documentation "context layer" for any existing repository, any tech stack — covering every phase of the SDLC — and keeps it fresh automatically.** It serves both humans and AI coding agents. It is **free and open source**.

It does three jobs:

1. **BOOTSTRAP** — reverse-engineer a full documentation set *from the code that already exists*.
2. **CONSOLIDATE** — gather the **scattered, existing** docs in a repo (root README, `wiki/`, `src/*.md`, Confluence/Notion exports, stray `.txt` design notes) and fold them into one structured layer — non-destructively.
3. **MAINTAIN** — keep all of it fresh on every change via pre-commit hooks and PR-review agents.

### The artifacts it produces (the context layer)
| # | Artifact | Source |
|---|---|---|
| 1 | **Specs** — what each feature/capability actually does | reverse-engineered from code |
| 2 | **Architecture docs + Mermaid architecture & integration diagrams** | static analysis of code |
| 3 | **Skills + rules** for development & testing assistance | repo conventions, test frameworks |
| 4 | **Runbooks + incident/observability docs** | services, ops config, logs/metrics setup |
| 5 | **Deployment docs** (how it ships — can live in the runbook) | CI/CD, IaC, deploy config |
| 6 | **Consolidated existing docs** — whatever was already written, restructured | the repo's current scattered docs |

All of it is emitted in a canonical `docs/` structure **and** distributed to AI agents (CLAUDE.md / AGENTS.md / `.cursor/rules` / MCP / skills) so the same context serves people and tools.

---

## 2. Current state — what exists today (and why it's stale)

Honest assessment of the v2 codebase, verified against source this session:

- **It's a skills-first platform, not a generator.** 23 markdown "skill" files in `docs/skills/` + a Python CLI that recommends/renders them. The premise was "developer pastes skills into their AI tool to *write* docs by hand," not "Doctyze generates docs from the repo."
- **It doesn't run.** The CLI can't be installed (`anthropic` imported unconditionally though it's optional; entry point `doctyze.cli:main` doesn't exist; wheel packages a nonexistent `src/doctyze`). Version says `0.0.2` while the CHANGELOG claims `v2.0.0-rc.1`. Tests are red against phantom modules. `examples/` is empty; `NamespaceManager` is dead code.
- **The skills are mostly stubs.** Only ~5 (write-spec, write-adr, update-openapi, write-runbook, write-investigation) are real, detailed LLM instructions. The other ~18 are short intent descriptions.
- **Consolidation was already imagined but never built.** `audit-existing-documentation` (90 lines) and `migrate-existing-documentation` (85 lines) describe exactly the "consolidate scattered docs → canonical structure, non-destructive, preserve git history" job — as *intent*, not code.

**Verdict:** v2's *mechanism* (pasteable skills + enforcement) is superseded by this plan and should be **archived**. But three things are worth **salvaging**: (a) the artifact taxonomy (specs/ADRs/runbooks/etc.), (b) the long-form content of the ~5 real skills — reuse them as **generator prompts**, and (c) the consolidation concept — promote it to a first-class capability (Job 2 above).

---

## 3. Adopt vs. build

Two-thirds of this is adoptable OSS (MIT/Apache-2.0, multi-language, maintained in 2026). Doctyze's original contribution is the connective intelligence.

| Capability | ADOPT (don't rebuild) | BUILD (the missing part) |
|---|---|---|
| Architecture docs + **Mermaid** diagrams | **CodeBoarding** (MIT, multi-lang static analysis → Mermaid) | grounding/curation into our `docs/` structure |
| Repo→wiki prose / explanations / Q&A | **DeepWiki-Open** (MIT) | — (harvest patterns) |
| **Specs** (grounded feature docs) | — *(no good OSS base)* | **spec extractor** grounded in CodeBoarding's static analysis (hallucination-resistant) |
| **Skills + rules** for dev/testing | **ruler** (MIT) for fan-out to CLAUDE.md/AGENTS.md/.cursor/MCP/skills | **skills generator** that derives them from *your* repo (no OSS generates; sync tools only fan out) |
| **Consolidate** scattered docs | hook/orchestration only | **consolidator** (audit → classify → restructure, non-destructive) — promote the v2 migrate/audit skills to real code |
| **Freshness — detect** stale docs | **fiberplane/drift** (MIT, tree-sitter AST anchoring, hook + CI, multi-lang) | diff → *which* artifact is affected, mapped to our structure |
| **Freshness — PR agent** | **qodo/pr-agent** (Apache-2.0, extensible) + **Danger JS** (cheap deterministic gate) | custom doc-freshness/regenerate tool on top |
| **Freshness — regenerate** the stale doc | — *(no maintained OSS; RepoAgent is stale)* | **regenerator** (re-run the relevant generator for just the affected artifact) |
| Hook orchestration | **pre-commit** (polyglot) or **lefthook** (monorepo speed) | — |

**Not adoptable (closed source — study, don't fork):** Swimm, Dosu, DeepDocs, CodeRabbit.

### Maintenance health of adopted OSS (verified via GitHub API, 2026-06-14)
| OSS | Stars | Last release | Commits/90d | Contributors | Verdict |
|---|---|---|---|---|---|
| CodeBoarding | 2.2k | v0.12.2 (Jun 13) | ≥100 | 20 | ✅ Healthy, very active |
| qodo/pr-agent | 11.6k | v0.36 (Jun 1) | ≥100 | 100+ | ✅ Healthy, company-backed (Qodo) |
| pre-commit | 15.3k | v4.6 (Apr) | 19 | 100+ | ✅ Mature/stable |
| lefthook | 8.4k | v2.1.9 (May) | 32 | 100+ | ✅ Healthy, company-backed (Evil Martians) |
| ruler | 2.7k | v0.3.42 (May) | ≥100 | 21 | ✅ Active — ⚠️ solo-maintained (bus factor) |
| DeepWiki-Open | 16.9k | none | 9 | 66 | ⚠️ Popular but cadence thinning; "harvest patterns" only, not a hard dep |
| fiberplane/drift | 98 | v0.10 (May) | 44 | 3 | ⚠️ **Riskiest** — 3 months old, tiny, Zig |

**Risk policy:** hard-depend only on the green tier. For the two ⚠️ tiers, keep a fallback because their logic is simple: **drift** → fall back to a deterministic Danger JS "did the affected doc change?" gate, or reimplement AST-anchoring; **ruler** → the fan-out is small enough to reimplement; **DeepWiki-Open** → harvest prose patterns, don't import as a runtime dependency. Re-run this maintenance check before each adoption is locked.

**What's genuinely ours to build (the defensible core):** (1) grounded **spec extraction**, (2) repo→**skills/rules** generation, (3) **consolidation** of scattered docs, (4) the **freshness loop** that ties drift-detection → affected-artifact → regeneration. No OSS tool does these four together.

---

## 4. Architecture / pipeline

```
 EXISTING REPO (any stack)
        │
        ├─ (A) CONSOLIDATE ──────────────────────────────────────────┐
        │     audit scattered docs (README, wiki/, src/*.md, exports) │
        │     classify → map to canonical docs/ → move non-destruct.  │
        │     (preserve git history, archive stale, fix links)        │
        │                                                             ▼
        ├─ (B) BOOTSTRAP / GENERATE                            canonical docs/
        │     CodeBoarding  → architecture docs + Mermaid             ├─ specs/
        │     DeepWiki-Open → prose explanations                      ├─ architecture/ (+ .mmd)
        │     OUR spec extractor   → feature specs                    ├─ runbooks/ (+ deploy)
        │     OUR skills generator → dev/testing skills & rules       ├─ observability/
        │     runbook/deploy generator → ops + deploy docs            └─ skills/ rules/
        │                                                             │
        ▼                                                             ▼
   (C) DISTRIBUTE  ── ruler ──►  CLAUDE.md · AGENTS.md · .cursor/rules · MCP · skills
        │
        ▼   ── then on every change ──
   (D) MAINTAIN
        drift  → flags which artifact went stale
        pre-commit / qodo-pr-agent → surfaces it on commit/PR
        OUR regenerator → refreshes just the affected artifact
```

Three commands, conceptually: `doctyze consolidate`, `doctyze bootstrap`, `doctyze watch` (hooks/PR-agent install).

---

## 5. First slice — thin end-to-end on a real repo

Prove the whole loop on **one real repo** (a representative service repo is a good candidate) before going wide:

1. **Consolidate (A):** audit the service's existing scattered docs → propose a `docs/` layout → move non-destructively (git-preserving, human-approved plan).
2. **Generate (B):** run **CodeBoarding** → architecture doc + Mermaid; add **one grounded spec** for a real feature; generate **one dev/testing skill** from its conventions.
3. **Distribute (C):** use **ruler** to emit AGENTS.md + a `.cursor/rules` from the generated context.
4. **Maintain (D):** wire **fiberplane/drift** so that changing a real source file flags the affected doc as stale on commit.

**Definition of done:** on the service repo, a single `docs/` context layer exists (consolidated + generated), agents can read it, and a code change correctly flags a stale doc. Small, real, full loop.

---

## 6. What happens to v2

- **Remove** (kept in git history): the renderer/vendor system, the broken CLI packaging, the 18 stub skills, the dead `NamespaceManager`, empty `examples/`.
- **Salvage:** the ~5 real skills (write-spec/adr/runbook/openapi/investigation) → become **generator prompts**; the artifact taxonomy → becomes the canonical `docs/` structure; the audit/migrate skills → become the **consolidator** spec.
- **Drop the framing:** "developer pastes skills to hand-write docs" → replaced by "Doctyze generates and maintains the docs."

---

## 7. Open decisions before building

1. **Language/stack for the new engine** — the adopt list is mixed (CodeBoarding=Python, ruler/drift=TS/Zig). Engine in **Python** (reuse v2's real skills, CodeBoarding native) calling the others as subprocesses, or **TS** for ecosystem fit? *(Lean: Python engine, shell out to the rest.)*
2. **How docs bind to code for freshness** — explicit anchors/frontmatter (deterministic, drift's model) vs. inferred. *(Lean: explicit frontmatter `affects:` + drift anchors; LLM inference optional.)*
3. **First repo** — confirm the proving repo, or pick another workspace repo.
4. **Consolidation aggressiveness** — propose-and-approve only (safe) vs. auto-apply. *(Lean: always propose a plan, human approves, non-destructive.)*

---

*This plan should be captured as an ADR (`check-and-update-adrs`) once the direction is confirmed — it's a significant architectural decision with rejected alternatives (rebuild vs. adopt-and-enhance; skills-first vs. generate-and-maintain).*

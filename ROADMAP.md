# Doctyze Roadmap

Doctyze is **free, open-source (Apache-2.0)**, and stays that way. This roadmap is
prioritized by **usefulness + adoption + non-duplication** — not monetization. It is a
direction, not a promise; issues are where the real discussion happens.

## The wedge we protect

A grounded look at the landscape (Mintlify, Swimm, DeepWiki, Driver.ai, Backstage TechDocs,
GitBook, Cody, graphify, …) shows most of Doctyze's *pieces* already exist somewhere. What
almost **no one** combines is Doctyze's cell:

> **Reverse-engineer a broad doc set from code** × **a deterministic "affected-docs"
> freshness signal** × **BYO-agent (no API key)** × **docs committed in the repo** ×
> **OSS / free.**

The one true head-to-head (Swimm, Driver.ai) is proprietary, hosted, paid, and own-LLM. So
the strategy is simple: **double down on the affected-docs primitive and the BYO-agent /
in-repo / no-key model; refuse to re-fight the battles others have already won** (hosted
sites, chat, hosted models).

## Guiding principles

- **BYO-agent, never a key.** The deterministic engine never calls an LLM; generation is the
  model already in your IDE/CI.
- **Docs live in the repo.** Committed, diffable, inherited on clone, offline.
- **Deterministic core + agent generation.** The CLI does the mechanics; the model writes prose.
- **Warn-first; enforcement is opt-in** (ADR-0004, ADR-0006).
- **Non-duplication.** If a mature tool already does it well, integrate — don't rebuild.

## Themes & tracked work

### 1. Sharpen the wedge — affected-docs freshness (highest priority)
The differentiated primitive; where investment compounds.
- **[#16](https://github.com/actyze/doctyze/issues/16)** — anchor-coverage report: flag changed files **no doc covers** (deterministic, closes the "net-new/undocumented" blind spot).
- **[#17](https://github.com/actyze/doctyze/issues/17)** — `check-drift` skill: **semantic** drift check run by the IDE agent (BYO), complementing the deterministic tripwire.
- **[#18](https://github.com/actyze/doctyze/issues/18)** — opt-in `--smart` hook that delegates the drift check to the user's agent (`claude -p` / Ollama), kept out of the default hook.
- **[#19](https://github.com/actyze/doctyze/issues/19)** — *rfc:* finer-grained coupling (symbol/section or dependency-graph) vs today's path-glob anchors — **without** giving up the no-parser/no-LLM/stack-agnostic guarantees.

### 2. Prove it works — validation & adoption
Output quality rides on the user's model, so evidence matters.
- **[#20](https://github.com/actyze/doctyze/issues/20)** — examples gallery: reproducible `docs/` trees on real OSS repos across stacks (+ dogfood Doctyze itself), with provenance.
- **[#15](https://github.com/actyze/doctyze/issues/15)** — a short demo of the current flow for the README.

### 3. Lower friction — newcomer & release hygiene
- **[#21](https://github.com/actyze/doctyze/issues/21)** — extend stack-detection signatures (C#, Swift, Elixir, Scala, C/C++, Nix, …). *good first issue.*
- **[#22](https://github.com/actyze/doctyze/issues/22)** — single-source the version (stop pyproject/`__init__`/plugin drift). *good first issue.*
- **[#23](https://github.com/actyze/doctyze/issues/23)** — maintain a moving `v0` major tag for the GitHub Action (so `@v0` works like `actions/checkout@v4`).

### 4. Publish without rebuilding — interop
- **[#24](https://github.com/actyze/doctyze/issues/24)** — render the `docs/` tree via **existing** SSGs (MkDocs / Docusaurus / Backstage TechDocs). Interop + a guide, **not** a Doctyze website.

## Non-goals (deliberate)

Doctyze will **not** chase these — they duplicate mature tools and pull against the wedge:

- **A hosted docs website / publishing SaaS.** Docusaurus, Mintlify, GitBook, Read the Docs,
  Backstage TechDocs already do this. We integrate (#24), we don't rebuild.
- **An own or hosted LLM / API-key path.** Breaks BYO-agent; already decided against
  (closed [#8](https://github.com/actyze/doctyze/issues/8)).
- **An interactive chat / "ask the codebase" product.** The IDE agent + the MCP server + the
  distributed `AGENTS.md`/skills already give agents repo context; DeepWiki/Cody/Unblocked own
  the hosted-chat space.
- **A per-language AST parser as the deterministic core.** It would trade away
  stack-agnosticism and the no-LLM guarantee; keep path-glob deterministic + semantic work in
  the agent (see #19).

## Where we're honestly weak today

(Openly, so contributors know the trade-offs — most map to a theme above or a non-goal.)

- No hosted site / search / theming → **interop** (#24), not a rebuild.
- Coarser path-glob coupling than Swimm/Driver's symbol-level → **#19**.
- Blind to changes no doc anchors, and to semantic completeness → **#16**, **#17**.
- Less proven at massive/legacy scale; output quality depends on the IDE model → **#20** (evidence).

Have an idea or disagree with a priority? Open an issue (`idea`/`rfc` labels) — that's the point.

# Doctyze

**Generate the docs a repo is missing from its code — and flag exactly which ones each change makes stale. For humans and AI agents, using the LLM already in your IDE.**

[![PyPI](https://img.shields.io/pypi/v/doctyze.svg)](https://pypi.org/project/doctyze/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-supported-green)](https://agents.md)

![Change a function, and Doctyze flags exactly which docs it made stale](scripts/demo/freshness-loop.gif)

---

## What it does

Point Doctyze at your repository — it's stack-agnostic by design. Your IDE's AI assistant then:

1. **Consolidates** scattered docs (loose READMEs, wiki notes, design files) into one canonical `docs/` tree — non-destructively.
2. **Generates** the missing docs from the actual code: feature specs, architecture + Mermaid diagrams, decisions (ADRs), runbooks, observability, dev/testing skills.
3. **Keeps them fresh** — when code changes, it flags exactly which docs are now stale.

No API key. Doctyze uses the **AI you already have in your IDE** (Cursor / Claude Code / Copilot) — it never calls an LLM itself or asks for a key.

### The flow at a glance

```text
$ uvx doctyze init                 # install skills + scaffold docs/  (one time)
  ↳ reload your IDE

  in your assistant:  /doctyze      # the agent consolidates existing docs,
  ↳ reads your code and writes:       specs · architecture + Mermaid · ADRs ·
                                      runbooks · observability · dev/testing skills
  ↳ runs the deterministic steps via the `doctyze` CLI — nothing to approve

$ git commit                       # the warn-first hook flags exactly which docs
  ↳ a code change made stale, so you regenerate only those
```

---

## Get started — one command

In your repo (nothing to pre-install — `uvx` fetches Doctyze on demand; needs `uv` + network):

```bash
uvx doctyze init
```

That one command **sets Doctyze up in your repo** — it:
- installs the **skills / playbook** your assistant runs (`.claude/skills`, `.cursor/rules`, `AGENTS.md`) — this is what powers the `doctyze` prompt,
- scaffolds the canonical `docs/` structure,
- registers the Doctyze **MCP server** in project configs (`.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`, and — if detected — `.codex/config.toml`, `.gemini/settings.json`) as an **optional, faster transport** for the deterministic steps. All repo-scoped and merge-safe (won't touch your other servers).

*(Windsurf and Cline only support a global MCP config, so `init` detects them and prints how to add the server there; both read `AGENTS.md`, so their playbook is already covered.)*

Then **reload your IDE** and invoke the **`doctyze`** prompt (Claude Code: `/doctyze` — or just say *"set up the documentation for this repo with Doctyze"*). Your assistant organizes existing docs, reads the code, and writes the new docs — using **its own model, no API key**. The deterministic steps run via the `doctyze` CLI (over `uvx`), so **there's nothing to approve** — it works right after reload.

> **Optional — faster MCP tools instead of the CLI.** `init` also registers Doctyze as an MCP server. To use it, **approve the server once**: project-scoped MCP servers need a one-time OK before their tools load, so reloading alone isn't enough (Claude Code: run `/mcp` → select `doctyze` → **Enable**; Cursor: Settings → MCP; VS Code: **Start** the server when prompted). The `doctyze` prompt works either way.

Commit the result and your teammates inherit the skills + config on `git clone` — **zero setup for the CLI/skills path** (the optional MCP tools still need a one-time approval per machine, see below).

Works across the major AI assistants — full support for **Claude Code, Cursor, VS Code/Copilot, Codex, Gemini**; **Windsurf and Cline** get the `AGENTS.md` playbook (+ a manual MCP add). The playbook reaches each IDE through the installed skills / rules / `AGENTS.md` (no setup, no approval); the MCP server *additionally* serves it as a prompt and exposes the deterministic tools for MCP-native clients that prefer them.

<details><summary>Prefer to add the MCP server manually, or on another IDE?</summary>

The server is identical everywhere:
```json
{ "mcpServers": { "doctyze": { "command": "uvx", "args": ["--from", "doctyze[mcp]", "doctyze-mcp"] } } }
```
| Assistant | How |
|---|---|
| **Claude Code** | `claude mcp add doctyze -- uvx --from 'doctyze[mcp]' doctyze-mcp` |
| **Cursor** | add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) |
| **VS Code / Copilot** | run **“MCP: Add Server”**, or add to `.vscode/mcp.json` (a `servers` map with `"type": "stdio"`) |
| **Codex CLI** | `codex mcp add doctyze -- uvx --from doctyze[mcp] doctyze-mcp`, or `[mcp_servers.doctyze]` in `.codex/config.toml` |
| **Gemini CLI** | add to `.gemini/settings.json` (`mcpServers`) |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` (`mcpServers`) — global only |
| **Cline** | its **“Configure MCP Servers”** UI (global) |

Every entry runs the same server: `uvx --from "doctyze[mcp]" doctyze-mcp`.

</details>

**What you get:** a `docs/` tree — `specs/`, `architecture/{diagrams,decisions}/`, `runbooks/`, `observability/`, `guides/`, `skills/` — with a `docs/index.md` table of contents, fanned out to `AGENTS.md` / `.cursor/rules` / Claude Code skills so every assistant on the repo inherits the context.

Each generated doc carries a freshness **anchor** so a code change flags the *specific* docs it makes stale:
```yaml
---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/payments/**]
  last_verified: 2026-06-28
---
```

---

## For CI & automation (optional)

The same operations are a small CLI, for pipelines and scripting (this is what the assistant calls under the hood — you don't need it for normal use):

```bash
pip install doctyze
doctyze --help     # init · consolidate · bootstrap · index · distribute · watch
```

Wire `doctyze watch` into a pre-commit hook or PR check to keep docs from drifting. These commands are **deterministic** (file moves, drift detection) and never call an LLM — generation stays with your IDE/CI agent.

### Freshness in CI — warn or block? (you choose)

The check is just a CLI command, so it runs in **any CI** (GitHub, GitLab, Jenkins, CircleCI, Azure…). The GitHub Action below is only a convenience wrapper around it.

```bash
# Any CI: report only (warn-first) — the raw primitive
doctyze watch --base "origin/$BASE_BRANCH"

# Any CI: gate the merge (fail the job when a doc is stale)
doctyze watch --base "origin/$BASE_BRANCH" --exit-code
```

> ⚠️ **In CI you must pass `--base` and fetch full history.** A CI checkout is *clean* —
> the change is already committed — so the default working-tree diff sees nothing and the
> check silently passes. `--base origin/<target-branch>` diffs the PR against its base so
> committed changes are detected. Make sure the base ref is fetched (e.g. `fetch-depth: 0`,
> or `git fetch origin <target-branch>`).

**GitHub Action** (wraps the above):

```yaml
# .github/workflows/docs-freshness.yml
- uses: actions/checkout@v4
  with: { fetch-depth: 0 }                 # REQUIRED so the base ref exists
- uses: actyze/doctyze@v0.3.4              # pin to a released tag
  with:
    base: origin/${{ github.base_ref }}    # the PR's target branch
    fail-on-stale: false                   # default: warn-only (report, don't block)
    # fail-on-stale: true                  # opt-in: fail the check to gate a merge
```

**GitLab CI** (no Action — just the CLI):

```yaml
docs-freshness:
  image: python:3.12
  variables: { GIT_DEPTH: 0 }              # full history
  script:
    - pip install doctyze
    - doctyze watch --base "origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME" --exit-code
```

**Recommendation (best practice):**

- **Local pre-commit stays warn-only — always.** A hook can't regenerate a doc (that needs
  your agent's model), so blocking the commit just trains `git commit --no-verify`. Doctyze
  will not make the local hook blocking.
- **Enforce at the *merge*, not the commit** — only if you want to. Set `fail-on-stale: true`
  and mark the check **required** in branch protection. It gates the shared branch without
  interrupting anyone's local flow.
- **Only turn the gate on if your `affects:` anchors are narrow.** Broad anchors flag every
  PR as "stale" and the check becomes noise people disable. Warn-first is the safe default.

The full rationale is in [ADR-0006](docs/architecture/decisions/0006-opt-in-ci-freshness-gate.md) (amending [ADR-0004](docs/architecture/decisions/0004-warn-first-not-enforced.md)).

**Doing AI-assisted code review?** The deterministic check flags *which* docs to revisit; when you already have a model in the loop (an IDE agent or a CI agent), you can also check *semantic* drift — does the changed functionality exist in the docs, is it net-new, has an existing doc drifted. See **[Checking Documentation Drift](docs/guides/checking-documentation-drift.md)** for exactly what to invoke and how (interactive `/doctyze`, headless `claude -p`, or a local model), plus a copy-paste reference prompt.

---

## How Doctyze compares

Documentation tooling is crowded, and much of it overlaps with pieces of Doctyze. Here is where Doctyze sits — and, just as importantly, where it doesn't.

**"Why not just use Swimm, Dosu, Mintlify, or DeepWiki?"** Often you should — they're mature and solve problems Doctyze doesn't. Reach for them when you want a SaaS editor with code-coupled walkthroughs (Swimm), a hosted bot that rewrites docs on every PR with its own model (Dosu / DeepDocs), a customer-facing docs website (Mintlify), or a browsable auto-generated wiki with Q&A (DeepWiki). Doctyze makes a narrower bet: generate the typed SDLC docs a repo is missing (specs, ADRs, architecture, runbooks, observability) straight into `docs/` using the model already in your IDE, then — deterministically, with no model of its own — flag which of those docs a change touches, by matching each doc's declared `affects:` globs against the changed files. No service, no API key, no site.

| | OSS / free | Runs its own LLM / needs a key | Freshness mechanism | Output | Hosted? |
|---|---|---|---|---|---|
| **Doctyze** | Yes (Apache-2.0) | No — BYO-agent; never calls an LLM, no key | `affects:` frontmatter anchors + `git diff`, deterministic; opt-in CI gate | In-repo `docs/` tree: specs, ADRs, architecture + Mermaid, runbooks, observability, dev/testing skills; `AGENTS.md` / rules fan-out | No — plain files in your repo |
| **Swimm** | No — proprietary SaaS | Yes (its own AI) | Snippet-coupled auto-sync: flags when coupled code drifts | Code-coupled docs / walkthroughs (in-repo `.md`, SaaS editor) | Yes (SaaS) |
| **Dosu / DeepDocs** | No — closed CI bot | Yes — its own LLM | Full-repo re-scan on each PR | PR comments / doc edits | Yes (hosted bot) |
| **Mintlify** | No — hosted product | Yes (AI writer) | Manual authoring (no code-drift signal) | Customer-facing docs website | Yes |
| **DeepWiki** | Cognition's is hosted/free; DeepWiki-Open is OSS | Yes | Re-index / regenerate the repo | Browsable wiki + Q&A | Yes (self-host for Open) |

Competitor columns reflect each tool's public positioning and may change; the Doctyze column maps to shipped capabilities (the `doctyze` CLI, the `write-*` generation skills, `affects:` anchors + `doctyze watch`, and the freshness GitHub Action).

**What Doctyze is NOT.** It is not a hosted documentation website (that's Mintlify), not a browsable wiki with Q&A (that's DeepWiki), not a source of external-library docs (that's Context7), and not a paid CI bot that runs its own model on every PR (that's Dosu / DeepDocs). It keeps canonical, human- and agent-readable docs *in the repo* and answers one question deterministically: which of these docs a change touches, by matching each doc's declared `affects:` anchors against the changed files.

**Complementary tools.** [Context7](https://github.com/upstash/context7) serves docs for *external* libraries over MCP — the external-docs counterpart to Doctyze's *in-repo* docs, so run both. Rather than out-build the tools that already own a stage, Doctyze wires them in: it already uses CodeBoarding as an optional architecture-diagram adapter (if it isn't installed, your IDE agent draws the Mermaid diagrams instead) and ruler as an optional fan-out backend for distributing rules to many agents (Doctyze ships its own fan-out otherwise) — both degrade gracefully when absent. [Graphify](https://github.com/Graphify-Labs/graphify) is the named interop partner (below).

---

## Works alongside your other tools — Graphify

Doctyze and [Graphify](https://github.com/Graphify-Labs/graphify) solve **adjacent halves** of the same problem, and they compose cleanly because the seam between them is a directory of files, not an API.

- **Doctyze authors the prose.** It writes the grounded artifacts — feature specs, architecture + Mermaid, ADRs, runbooks, `AGENTS.md` — by having your IDE's agent read the actual code, then keeps them consolidated and fresh. What lands on disk is a `docs/` tree of Markdown.
- **Graphify indexes it.** It turns your code **plus** those artifacts into one queryable knowledge graph (`graph.json`) — code structure via tree-sitter AST, docs turned into concept nodes — reachable over a CLI and an MCP server.

Neither reimplements the other: Doctyze has no graph or query layer, and Graphify authors no documentation. The output of one is the input of the other.

| | Doctyze | Graphify (`graphifyy`) |
|---|---|---|
| **Job** | Generate & maintain grounded docs | Index code + docs into a queryable graph |
| **Produces** | `docs/` Markdown (specs, ADRs, arch+Mermaid, runbooks), `AGENTS.md` | `graphify-out/graph.json` + MCP retrieval |
| **Retrieval surface** | `affects:` anchors + `git diff` (freshness), not search | `query` / `path` / `explain` / `affected` + MCP tools |
| **LLM usage** | BYO-agent; never calls an LLM itself | BYO-agent for docs/images; code AST is free/local |

Both are **BYO-agent** — they borrow the model already in your IDE rather than shipping a key — so the pairing adds no new credentials.

```bash
# 1. Doctyze authors the docs/ tree from your code (agent-written prose)
uvx doctyze init            # scaffold docs/, install skills, register optional MCP
#   …then invoke /doctyze in your IDE to generate the specs/ADRs/architecture/runbooks

# 2. Graphify indexes code + those docs into one graph
uv tool install graphifyy   # note the double-y PyPI name
graphify install            # register the skill in your assistant
/graphify .                 # run the pipeline over the repo (code AST + docs/ extraction)

# 3. Query the merged graph
graphify query "how does auth token refresh work?"
python -m graphify.serve graphify-out/graph.json   # or expose it to an agent over MCP
```

> **Affected-docs across both (proposed, not yet built).** Doctyze already answers "which docs did this change make stale?" deterministically via `affects:` anchors + `git diff`; Graphify ships its own `graphify affected` (reverse-BFS impact over the *code* graph). They're separate today. Using Graphify's deterministic code-dependency graph to give Doctyze *transitive* reachability — the one thing hand-written globs can't do — is a promising integration, evaluated in [ADR-0007](docs/architecture/decisions/0007-graphify-graph-for-affected-docs.md). Its doc↔code cross-links are LLM-inferred, so that layer stays advisory; the deterministic anchor+diff remains the gate.

**Full walkthrough:** [Using Doctyze with Graphify](docs/guides/using-doctyze-with-graphify.md) — a step-by-step recipe (generate docs → index code+docs → query the graph), with the honest boundary between the two.

---

## How it's built

A deterministic Python engine (no LLM, no key) exposed as both an MCP server and a CLI, plus agent-run generation skills. See `CONTRIBUTING.md` and `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md`.

## License

Apache 2.0. Free and open source for everyone.

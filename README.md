# Doctyze

**Turn any repo into living documentation — for humans and AI agents — using the LLM already in your IDE.**

[![PyPI](https://img.shields.io/pypi/v/doctyze.svg)](https://pypi.org/project/doctyze/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-supported-green)](https://agents.md)

---

## What it does

Point Doctyze at any repository, any stack. Your IDE's AI assistant then:

1. **Consolidates** scattered docs (loose READMEs, wiki notes, design files) into one canonical `docs/` tree — non-destructively.
2. **Generates** the missing docs from the actual code: feature specs, architecture + Mermaid diagrams, decisions (ADRs), runbooks, observability, dev/testing skills.
3. **Keeps them fresh** — when code changes, it flags exactly which docs are now stale.

No API key. Doctyze uses the **AI you already have in your IDE** (Cursor / Claude Code / Copilot) — it never calls an LLM itself or asks for a key.

---

## Get started — one command

In your repo (nothing to install — `uvx` fetches it on demand):

```bash
uvx doctyze init
```

That one command **wires Doctyze into your IDEs** — it:
- registers the Doctyze **MCP server** in project configs (`.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`) — scoped to the repo and merge-safe (won't touch your other servers),
- installs the **skills** (`.claude/skills`, `.cursor/rules`, `AGENTS.md`),
- scaffolds the canonical `docs/` structure.

Then **reload your IDE** and, in your assistant, invoke the **`doctyze`** prompt (Claude Code: `/doctyze` — or just say *"set up the documentation for this repo with Doctyze"*). Your assistant organizes existing docs, reads the code, and writes the new docs — using **its own model, no API key**.

Commit the result and your teammates inherit Doctyze (MCP config + skills) on `git clone` — **zero setup for them**.

Works with **any MCP-capable assistant** — Claude Code, Cursor, Windsurf, GitHub Copilot (VS Code), and others. The MCP server ships both the **tools** *and* the **playbook** (as an MCP prompt), so every IDE gets the full guided workflow on the first run.

<details><summary>Prefer to add the MCP server manually, or on another IDE?</summary>

The server is identical everywhere:
```json
{ "mcpServers": { "doctyze": { "command": "uvx", "args": ["--from", "doctyze[mcp]", "doctyze-mcp"] } } }
```
| Assistant | How |
|---|---|
| **Claude Code** | `claude mcp add doctyze -- uvx --from 'doctyze[mcp]' doctyze-mcp` |
| **Cursor** | add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) |
| **Windsurf** | Settings → Cascade → MCP servers |
| **VS Code / Copilot** | run **“MCP: Add Server”**, or add to `.vscode/mcp.json` (uses a `servers` map with `"type": "stdio"`) |

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

Wire `doctyze watch` into a pre-commit hook or PR check to keep docs from drifting in CI. These commands are **deterministic** (file moves, drift detection) and never call an LLM — generation stays with your IDE/CI agent.

---

## How it's built

A deterministic Python engine (no LLM, no key) exposed as both an MCP server and a CLI, plus agent-run generation skills. See `CONTRIBUTING.md` and `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md`.

## License

Apache 2.0. Free and open source for everyone.

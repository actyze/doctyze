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

In your repo (nothing to install — `uvx` fetches it on demand):

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

Commit the result and your teammates inherit Doctyze (MCP config + skills) on `git clone` — **zero setup for them**.

Works with **any AI assistant** — Claude Code, Cursor, VS Code/Copilot, Codex, Gemini, Windsurf, Cline, and more. The playbook reaches every IDE through the installed skills / rules / `AGENTS.md` (no setup, no approval); the MCP server *additionally* serves it as a prompt and exposes the deterministic tools for MCP-native clients that prefer them.

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

Wire `doctyze watch` into a pre-commit hook or PR check to keep docs from drifting in CI. These commands are **deterministic** (file moves, drift detection) and never call an LLM — generation stays with your IDE/CI agent.

---

## How it's built

A deterministic Python engine (no LLM, no key) exposed as both an MCP server and a CLI, plus agent-run generation skills. See `CONTRIBUTING.md` and `docs/architecture/decisions/0003-pivot-to-context-layer-generator.md`.

## License

Apache 2.0. Free and open source for everyone.

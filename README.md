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

## Get started — add it to your AI assistant, once

Doctyze runs as an **MCP server**, so it works with **any MCP-capable assistant** — Claude Code, Cursor, Windsurf, GitHub Copilot (VS Code), and others. You add the server **once**; after that you just *ask your assistant* — you never run Doctyze by hand.

The server is identical everywhere (no install needed — `uvx` fetches it on demand):

```json
{
  "mcpServers": {
    "doctyze": {
      "command": "uvx",
      "args": ["--from", "doctyze[mcp]", "doctyze-mcp"]
    }
  }
}
```

**Where to add it** (one-time — each IDE has its own MCP config):

| Assistant | How to add the server |
|---|---|
| **Claude Code** | `claude mcp add doctyze -- uvx --from 'doctyze[mcp]' doctyze-mcp` (terminal). *Builds with the plugin UI can instead use `/plugin marketplace add actyze/doctyze` then `/plugin install doctyze@doctyze`.* |
| **Cursor** | add the block above to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) |
| **Windsurf** | Settings → Cascade → MCP servers → add the command |
| **VS Code / GitHub Copilot** | run **“MCP: Add Server”**, or add it to `.vscode/mcp.json` |

**Then, in your repo, just say:**
> *"set up the documentation for this repo with Doctyze"*  (Claude Code: `/doctyze`)

Your assistant calls Doctyze's tools to organize existing docs, reads the code, writes the new docs, and builds a navigable `docs/` — using its own model. No API key.

> The MCP server gives your assistant the **tools**. The **playbook** (how to generate good, grounded docs) ships as skills: Claude Code loads them from the plugin, and after the first run `distribute` writes them to `AGENTS.md` / `.cursor/rules` so every assistant on the repo inherits the guidance.

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

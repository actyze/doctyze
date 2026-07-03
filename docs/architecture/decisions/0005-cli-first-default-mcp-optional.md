# ADR-0005: CLI Is the Default Transport for the Skill; MCP Is Optional

**Status:** 🟢 ACCEPTED
**Date:** 2026-07-03
**Deciders:** Rohit Mangal

## Context

Doctyze exposes its deterministic operations (consolidate, bootstrap, index, distribute,
freshness) through **two transports over the same `api.py`**: the `doctyze` **CLI** (run via
`uvx`) and an **MCP server** wired into the IDE by `init`. Doc generation itself is done by
the agent's model in both cases — neither transport generates prose.

The `doctyze` skill originally told the agent to prefer the **MCP tools**, falling back to
the CLI. In practice this created a first-run wall: `init` writes a **project-scoped**
`.mcp.json`, and most assistants (Claude Code, Cursor, VS Code) gate a project MCP server
behind a **one-time approval** before its tools load. Until the user approves, `/doctyze`
found *no* tools — even though `claude mcp list` reported the server "Connected" (the health
check connects regardless of session approval). The skill sent the agent hunting for tools
that weren't there yet.

Peer tools confirmed the pattern: graphify avoids the gate entirely by delivering via a
CLI + git hook + skill file (no MCP in the default path); caveman/obsidian register at
user scope (`claude mcp add`) which is auto-trusted. Doctyze already ships the equivalent
CLI + skill + freshness-hook — the MCP wrapper was simply made the default, and it is the
only piece that needs approval.

## Decision

**The `doctyze` skill defaults to the CLI (`uvx doctyze …`), which needs no approval. The
MCP tools are presented as an optional, faster transport — "use only if you can't run the
CLI."** Both run identical code, so the workflow is unchanged; only the default transport
the skill reaches for changed.

`init` keeps writing the project `.mcp.json` (for the committable, teammates-inherit,
cross-IDE-prompt story), but its onboarding output, the README, and `setup.py` now present
the CLI as the no-approval default and demote MCP approval to an explicitly optional step.

## Rationale

1. **Doctyze is build-time, not a long-running service.** Its ops are a one-shot generate +
   a freshness hook — exactly what a CLI delivers. A persistent MCP server is not required
   for the core workflow.
2. **Zero-friction first run.** The CLI (`uvx`) needs no per-project approval, so `/doctyze`
   works immediately after `init` + reload. This removes the single biggest onboarding
   failure without sacrificing anything.
3. **Nothing is lost.** Generation was never in the CLI or the MCP server — it is always the
   model. Dropping the MCP default changes no output; the committable `.mcp.json` and the
   cross-IDE MCP *prompt* remain available for anyone who opts in.

## Consequences

- **Positive:** no approval wall on first run; the skill is honest about who does what
  (model generates, CLI/MCP only run deterministic steps); doctyze keeps the committable +
  cross-IDE advantages MCP provides for those who enable it.
- **Tradeoff:** the CLI path shells out to `uvx` (a first-run fetch, and it needs shell +
  network). In locked-down sandboxes an *approved* MCP server can be more reliable — hence
  MCP stays a first-class opt-in, not a removed feature.

## Alternatives Considered

- **Auto-enable the MCP server in `init`** (write `enabledMcpjsonServers` into the user's
  `~/.claude.json`) — rejected: contradicts the "never touch global settings" guarantee and
  is Claude-Code-specific.
- **Drop MCP entirely (graphify-style)** — rejected: loses the cross-IDE MCP prompt and the
  committable-server story that peers lack.
- **Keep MCP-first, only fix the messaging** — rejected as insufficient: the wall recurs
  every time a user skips the approval step; the default should be the path that always
  works.

## Related ADRs

- [ADR-0003: Pivot to a Repo Context-Layer Generator](./0003-pivot-to-context-layer-generator.md)
  — already ranks agent-run skills (1) above the optional MCP server (2); this ADR makes the
  skill's runtime default consistent with that ordering.
- [ADR-0004: Warn-First — Doctyze Does Not Enforce Doc Writes](./0004-warn-first-not-enforced.md)
  — same philosophy: low-friction, IDE-agnostic, no mandatory gates.

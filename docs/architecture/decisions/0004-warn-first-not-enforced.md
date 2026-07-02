# ADR-0004: Warn-First — Doctyze Does Not Enforce Doc Writes

**Status:** 🟢 ACCEPTED
**Date:** 2026-07-02
**Deciders:** Rohit Mangal

## Context

A recurring question: should Doctyze *enforce* a rule every time a documentation / `.md` file is written — e.g. block or auto-correct any doc that isn't in the canonical `docs/` structure or is missing a freshness anchor? The intuition is reasonable: if docs must live in a proper folder with an anchor, why not guarantee it mechanically?

Three concrete enforcement points were considered: a Claude Code **PostToolUse hook** (fire on every `.md` write), a **blocking git pre-commit** check, and a repo-wide **`.md` linter**.

## Decision

**Doctyze stays warn-first. It does NOT enforce doc-placement or anchor rules at write-time or commit-time.** Correct placement is achieved at **generation time**, through the skills/playbook the developer's agent runs — not by a policing layer. Any future validation is **opt-in and docs-scoped**, never a mandatory gate.

## Rationale

1. **Not every `.md` is a doc.** A repo is full of Markdown that is not part of the docs context layer — `README`, `CHANGELOG`, `CONTRIBUTING`, issue templates, inline module notes, vendored files. Doctyze cannot reliably infer intent, so policing "every `.md`" produces constant false positives, and users disable it. The only files Doctyze can legitimately reason about are those already in `docs/` or already carrying a `doctyze:` anchor.
2. **There is no universal "on-write" moment.** Claude Code has PostToolUse hooks; Cursor, Copilot, Codex, and Gemini do not (uniformly). A git pre-commit hook only fires *if the user commits*. So "enforced every time a doc is written" cannot be honestly delivered across the any-IDE, BYO-agent model — partial enforcement is worse than none because it implies coverage that doesn't exist.
3. **v3 is warn-first by design.** The v3 rewrite deliberately replaced v2's *"skills-first, paste-by-hand + enforce"* model (see [ADR-0003](./0003-pivot-to-context-layer-generator.md) and the CHANGELOG). Re-adding blocking enforcement regresses the core decision that defines the current product.

## Consequences

- **Positive:** Doctyze remains non-intrusive and IDE-agnostic; the pre-commit freshness hook stays warn-only (code→stale-docs, never blocking); placement quality lives in one honest place — the generation playbook.
- **Tradeoff:** correct placement/anchors depend on the agent following the skill's guidance; there is no mechanical guarantee. If real-world use shows docs drifting, the fix is to **sharpen the skill's placement rules**, not to add a gate.

## Alternatives Considered

- **PostToolUse hook that validates every `.md` write** — rejected: Claude-Code-only (not cross-IDE), and fires on non-doc Markdown.
- **Blocking git pre-commit check** — rejected: doesn't fire if the user doesn't commit; blocking contradicts warn-first.
- **Repo-wide `.md` linter** — rejected: wrong unit (most `.md` aren't docs).

## Future Option (Not Now)

If drift is observed in practice, add an **opt-in, docs-scoped `doctyze check`**: a read-only lint over the `docs/` tree (+ anchored files) reporting missing/too-broad anchors, orphan files, and broken index links. Surface it as (a) an MCP tool the agent calls as a self-check right after generating (fixes issues inline, no commit needed, any IDE), and (b) a plain `doctyze check` CLI users can wire into *their own* CI/pre-commit. Warn-first, never blocking. **Validate the need before building it.**

## Related ADRs

- [ADR-0003: Pivot to a Repo Context-Layer Generator](./0003-pivot-to-context-layer-generator.md) — establishes the warn-first, BYO-agent delivery model this ADR upholds.

# ADR-0001 — Record architecture decisions

- Status: accepted
- Date: 2026-06-06
- Confidence: 🟢 CONFIRMED

## Context

We need a durable record of significant architectural decisions: what we chose,
why, what alternatives were considered, and what consequences followed. Without
it, the *why* lives in chat threads and gets lost.

## Decision

Use [MADR](https://adr.github.io/madr/) format. Store ADRs in
`docs/architecture/decisions/`. One ADR per file, numbered sequentially.

The Doctyze PR review action enforces this: any change that adds an external
dependency, swaps a major component, or introduces a non-obvious pattern must
include a corresponding ADR.

## Alternatives rejected

- **No ADRs at all** — the legacy-modernization pain Doctyze targets is
  exactly this. We won't recreate it ourselves.
- **ADRs in Confluence** — drifts from the code, can't be reviewed in the
  same PR, harder for AI agents to find.
- **Notion / Linear docs** — same drift problem; not repo-native.

## Consequences

- (+) Every significant decision captured with reasoning at the time it was made.
- (+) AI coding agents have access to the *why* behind the *what*.
- (−) ~15–30 min overhead per architecturally-significant change.

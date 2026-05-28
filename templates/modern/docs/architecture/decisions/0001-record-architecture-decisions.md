# ADR-0001 — Record architecture decisions

- Status: accepted
- Date: {{GENERATION_DATE}}
- Confidence: 🟢 CONFIRMED (this ADR is self-evident — the existence of this folder is the decision)

## Context

We need to keep a durable record of significant architectural decisions:
what was chosen, why, what alternatives were considered, and what
consequences followed. Without a written record, this knowledge lives
only in chat threads and senior engineers' heads — and gets lost when
people change roles or leave.

## Decision

We use [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)
format, stored in [`docs/architecture/decisions/`](.) in this repository,
one ADR per file, numbered sequentially.

Each ADR has the following sections:

- **Status** — accepted | proposed | deprecated | superseded by ADR-NNNN
- **Date** — when the decision was finalized
- **Context** — the situation forcing the decision
- **Decision** — what we chose
- **Alternatives rejected** — what we considered and why we didn't pick it
- **Consequences** — what follows from this decision (positive and negative)

The PR review GitHub Action enforces this convention: any change that
adds a new external dependency, a new architectural component, or a
significant new pattern must be accompanied by an ADR.

## Alternatives rejected

- **No ADRs at all** — design decisions get lost; new joiners (and AI
  coding agents) cannot reconstruct intent from code alone. The
  legacy-modernization pain we built Doctyze to solve is exactly this.
- **ADRs in Confluence / external wiki** — drifts from the code,
  cannot be reviewed in the same PR, harder for AI coding agents to
  find. Repo-native wins.
- **Lightweight Decision Records (LDR)** or other formats — MADR is
  widely understood and tool-supported.

## Consequences

- **+** Every significant decision is captured at the time it is made,
  with reasoning.
- **+** AI coding agents reading this repo immediately have access to
  the *why* behind the *what*.
- **+** The PR review bot can enforce ADR creation on dependency changes,
  reducing decision-rot.
- **−** Small overhead for each architecturally-significant change
  (writing an ADR takes ~15–30 minutes).
- **−** Requires discipline to mark old decisions as `superseded` when
  new ADRs replace them.

## Links

- [MADR specification](https://adr.github.io/madr/)
- [Doctyze README](../../../README.md)
- [AGENTS.md](../../../AGENTS.md)

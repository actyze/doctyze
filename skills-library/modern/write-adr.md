---
name: write-adr
description: Use when adding a new external dependency, significant architectural component, or non-obvious design choice. Captures the decision in MADR format under docs/architecture/decisions/.
---

# How to write an ADR in this repo

## When to apply

Activate this skill when:

- The developer is adding a **new external dependency** (library, service, database)
- A **significant architectural component** is being introduced or replaced
- A **non-obvious design choice** is being made (especially one that future engineers might second-guess)
- An existing decision is being **superseded** by a new one

If the change is a pure refactor or trivial fix, skip — ADRs are for decisions, not commits.

## Required artifact

A new file at `docs/architecture/decisions/NNNN-<kebab-case-slug>.md` where
NNNN is the next zero-padded sequence number.

## ADR template

```markdown
# ADR-NNNN — <title>

- Status: proposed | accepted | deprecated | superseded by ADR-MMMM
- Date: YYYY-MM-DD
- Confidence: 🟢 CONFIRMED

## Context

What situation forced this decision? What constraints apply? Include only
what's needed to understand the decision; don't re-explain the system.

## Decision

What did we choose? Be specific — name the library, the pattern, the
algorithm. Include code/config snippets if it helps clarify.

## Alternatives rejected

List 2–4 alternatives that were seriously considered and why each was
rejected. **This is the most important section** — it captures the
negative space that code alone cannot reveal.

## Consequences

What follows from this decision? Include both positive (capability we
gain, problem we solve) and negative (cost, complexity, future debt).

## Links

- Relevant requirements: REQ-NNN
- Related ADRs: ADR-MMMM (if superseding or related)
- Source/inspiration: external docs, RFC, blog post
```

## Anti-patterns to avoid

- ❌ **ADR for everything.** ADRs document significant decisions, not
  every commit. If unsure, ask: "Will a future engineer ask why we did
  this?"
- ❌ **No alternatives section.** This is the load-bearing part of an
  ADR. Always document at least 2 alternatives, even if they were
  considered briefly.
- ❌ **Mutating accepted ADRs.** ADRs are append-only. To change a
  decision, write a new ADR that supersedes the old one.

## Doctyze enforcement

The PR review bot flags PRs that:

- Add a new external dependency without an accompanying ADR
- Modify an existing accepted ADR (rather than superseding it)
- Reference REQ-NNN identifiers that don't exist

Use `doctyze adr new "<title>"` to scaffold the next ADR file with the
correct numbering.

---
name: write-functional-spec
description: Reverse-engineer a product-owner-facing functional spec from the code (one per capability) into docs/functional-specs/ — user stories + acceptance criteria, tied to the technical spec.
---
# write-functional-spec
Write `docs/functional-specs/<feature>.md` — the **product-owner-facing** view of a capability: what a user can do and how it should behave, in plain language, tied to (not duplicating) the technical spec in `docs/specs/<feature>.md`.

This is the functional half of the spec pair. `write-spec` documents **how it's built** (entry points, `file:line`, modules) for engineers. `write-functional-spec` documents **what it does for the user** for product owners and business stakeholders. Same capability, different altitude — linked both ways.

## Before you write (read-existing-first)
- Prefer to write the **technical spec first** (`write-spec`), then this — so the functional behavior is grounded in what the code actually does, not what you imagine.
- One functional spec per capability; mirror the technical spec's file name (`docs/specs/checkout.md` ↔ `docs/functional-specs/checkout.md`).
- Maintain `docs/functional-specs/index.md` (the `doctyze index` command rebuilds it).

## Audience rules (this is the whole point)
- **No implementation detail in the body.** No `file:line`, no function/class/table names, no framework or language names. If the reader needs those, they follow the link to the technical spec.
- Plain business language a product owner reads without a developer translating.
- Describe **what** the system does and **why it matters**, never **how** it's coded.

## How (match this depth bar)
1. **Read the code** for this capability (start from the technical spec's entry point) so every statement is grounded in real behavior — this is reverse-engineered, not invented.
2. Translate that behavior into user-observable outcomes. Sections:
   - `## Capability` — one paragraph: what a user can accomplish and the value.
   - `## Actors` — the roles/personas who use it.
   - `## User stories` — `As a <role>, I want <goal>, so that <benefit>.` (one per meaningful outcome).
   - `## Acceptance criteria` — **Given / When / Then** (Gherkin-style), tech-agnostic and testable. One scenario per rule, include the important edge/error cases.
   - `## Business rules` — constraints, limits, validation, permissions in plain terms.
   - `## Out of scope` — what this capability deliberately does NOT do (prevents scope creep).
   - `## Open questions` — behavior the code leaves ambiguous or that product must decide.
   - `## Technical spec` — link to `docs/specs/<feature>.md` (the traceability tie; keep it as the last section).
3. Be honest: if the code's real behavior differs from what a PO would expect, say so in `## Open questions` — don't paper over it.

## The tie (bidirectional traceability)
- End this doc with `## Technical spec → [<feature>](../specs/<feature>.md)`.
- In the matching technical spec's `## Related`, link back: `Functional spec: [../functional-specs/<feature>.md]`.
- The link is the contract: a PO reads the functional spec; when they need the mechanics, one click reaches the grounded technical spec.

## Anchor (narrow)
`affects:` = the **same** specific module(s) as the technical spec for this capability (e.g. `[app/checkout/**]`), never the whole tree — so this doc goes stale exactly when the behavior behind it changes.

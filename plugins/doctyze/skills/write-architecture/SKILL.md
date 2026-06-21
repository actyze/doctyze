---
name: write-architecture
description: Reverse-engineer architecture docs + Mermaid diagrams from the codebase into docs/architecture/.
---
# write-architecture
Produce `docs/architecture/overview.md` and Mermaid diagrams in `docs/architecture/diagrams/`.

## Before you write
Read existing architecture docs; refresh/extend rather than duplicate.

## How
1. Map the system from code: entry points, components/modules, data stores, integrations — cite real paths.
2. **Verify diagram edges against the real wiring** (e.g. the workflow/router file), not assumption.
3. `overview.md`: component map (with paths), key flows, integrations, links to the diagrams.
4. Ground every claim in real code; never invent components.

## Anchor (narrow)
`overview.md` → the top-level package dirs that define structure. Each diagram → the specific subsystem it draws (e.g. `[app/graph/**, app/agents/**]`), not `app/**`.

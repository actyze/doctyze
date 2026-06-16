---
name: write-architecture
description: Reverse-engineer architecture docs and Mermaid architecture/integration diagrams from the codebase.
---
# write-architecture
Produce `docs/architecture/overview.md` plus Mermaid diagrams in `docs/architecture/diagrams/`.

## overview.md sections
- **Purpose** of the system.
- **Component map** — the real modules/services and their responsibilities (cite paths).
- **Key flows** — the main request/data flows.
- **Integrations** — external systems, datastores, queues.
- Links to each diagram.

## Diagrams (Mermaid, in diagrams/)
- A **pipeline/component** diagram (`flowchart`) of the system's parts.
- A **sequence** diagram for the most important flow.
- An **integration** diagram if there are external systems.
Mark optional/external nodes distinctly. Ground every node in real code — never invent components.

## Anchor (required)
```yaml
---
doctyze:
  artifact: architecture     # use `diagram` for files in diagrams/
  generated_by: write-architecture
  affects: [<top-level source dirs>/**]
  last_verified: <YYYY-MM-DD>
---
```

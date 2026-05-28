# {{SERVICE_NAME}} — Architecture overview (Legacy stack)

> Confidence: 🟡 INFERRED unless noted. Doctyze generated this from scanning
> the codebase. Verify with senior engineers — this is time-sensitive.

## Purpose

{{ONE_PARAGRAPH_PURPOSE}}

## How this system is organized

Legacy systems don't fit the modern "containers + microservices" mental
model cleanly. The natural units of work are:

- **Programs** — individual COBOL programs, ABAP reports, RPG programs, VB6 forms.
  One md per significant program in [`docs/programs/`](../programs/).
- **Jobs** — JCL batch jobs (z/OS), SAP batch variants, IBM i job scheduler entries.
  See [`docs/jobs/`](../jobs/).
- **Transactions** — CICS transactions, SAP t-codes, IBM i 5250 menu entries.
  Mapped in [`diagrams/transaction-map.mmd`](diagrams/transaction-map.mmd).
- **Interfaces** — inbound (consumers) and outbound (downstream).
  See [`docs/interfaces/`](../interfaces/).

## Data flow is the architecture

```mermaid
{{DATA_FLOW_MERMAID}}
```

See [`data-flow/`](data-flow/) for the source.

## Job dependency graph

How batch jobs chain together (critical for production scheduling):

```mermaid
{{JOB_DEPENDENCY_MERMAID}}
```

See [`diagrams/job-dependencies.mmd`](diagrams/job-dependencies.mmd) for source.

## Copybook / shared-structure graph

Legacy systems use shared data structures (copybooks in COBOL, includes
in ABAP, DDS in IBM i). Cross-program coupling lives here:

```mermaid
{{COPYBOOK_GRAPH_MERMAID}}
```

See [`diagrams/copybook-graph.mmd`](diagrams/copybook-graph.mmd) for source.

## External interfaces

| Direction | Interface | Protocol | Owner |
|---|---|---|---|
| Inbound  | ... | ... | ... |
| Outbound | ... | ... | ... |

Detail in [`docs/interfaces/`](../interfaces/).

## 🔴 GAP — for the senior-engineer interview

These need a human to answer. Doctyze has prepared the questions in
[`docs/investigations/adr-archaeology/pending-questions.md`](../investigations/adr-archaeology/pending-questions.md).

- Why was this stack chosen originally (the ADR before there were ADRs)?
- Which programs are "do not touch" without coordinating with named operators?
- What's the history of the most-painful production incidents in this system?

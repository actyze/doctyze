# ADR-0002: Workspace Mode for Monorepo/Multirepo Documentation

**Status:** 🔴 SUPERSEDED by [ADR-0003](./0003-pivot-to-context-layer-generator.md) — this describes the v2 scaffolder/renderer architecture, now archived. Kept for history.
**Date:** 2026-06-10
**Deciders:** Rohit Mangal, Actyze team
**Consensus:** ✅ Approved

## Problem

Doctyze originally supported single-repository scaffolding. Teams with monorepo
or multirepo architectures needed to either:

1. Run `doctyze init` separately on each repo (N API calls, inconsistent context)
2. Build custom orchestration to aggregate docs post-hoc (manual, error-prone)

This created bottlenecks for:
- **Inconsistent service context** — each repo scaffolded independently
- **No top-level system documentation** — C4 diagrams, service index, cross-service runbooks
- **Idempotence failures** — overwriting hand-authored docs on re-runs
- **Token inefficiency** — one LLM call per repo instead of batch-filling all placeholders together

## Decision

Implement **Workspace Mode** to scaffold all service repos and generate top-level
documentation in a single unified pass.

### Design Principles

1. **Single unified pass:** One `doctyze workspace <root>` command (monorepo) or with `--docs-repo` (multirepo)
2. **Parallel scaffolding:** All service repos scaffold + extract independently in parallel
3. **Idempotent merge:** Preserve hand-authored content; only scaffold missing artifacts
4. **Top-level aggregation:** Generate C4 system landscape, service graph, cross-service runbooks
5. **Efficient LLM usage:** One aggregated extraction call fills all placeholders across all repos

### Architecture

```
Phase 1: Discovery
  ├─ WorkspaceDetector scans <root> for service repos
  └─ Identify stack per service (Go, Python, Node, Java, etc.)

Phase 2: Context Aggregation
  ├─ WorkspaceContextAggregator reads existing AGENTS.md files
  ├─ Collects all ADRs, skills from all repos
  └─ Builds service dependency map

Phase 3: Individual Repo Scaffolding (Parallel)
  ├─ For each service:
  │  ├─ Scaffolder(idempotent=True) with status: GENERATE/SKIP/MERGE
  │  ├─ write() respects idempotence flags
  │  └─ extract_and_fill() with aggregated context
  └─ Render vendor files per service

Phase 4: Top-Level Aggregation
  ├─ TopLevelScaffolder generates workspace-level templates
  ├─ C4 system landscape from aggregated context
  ├─ Service index with links to individual repos
  ├─ Cross-service runbooks
  └─ extract_and_fill() with workspace stack type
```

### Idempotent Merge Semantics

When `Scaffolder(idempotent=True)`:

- `plan()` marks each file with a status:
  - **GENERATE:** file doesn't exist, create it
  - **SKIP:** file exists, don't touch (non-template)
  - **MERGE:** file exists, it's a template → rewrite but extraction will fill placeholders

- `write()` honors status:
  - GENERATE: write the file
  - SKIP: skip it
  - MERGE: copy template (extraction will update placeholders next)

- `extract_and_fill()` always runs (already idempotent):
  - Only replaces `{{PLACEHOLDER}}` tokens
  - Non-placeholder content is untouched

**Result:** Run twice → same output. Hand-authored files survive.

### Configuration: `.doctyze.workspace.yaml`

```yaml
workspace:
  # For multirepo only
  docs_repo: /path/to/separate/docs-repo

  # Service discovery patterns
  service_patterns:
    - services/*
    - modules/*
    - cmd/*

  # Exclude directories
  exclude:
    - tools/
    - examples/
    - scripts/

  # Stack family overrides
  family: modern  # or "legacy" or "mixed"
```

## Consequences

### ✅ Positive

- **Single command** handles all repos at once
- **Efficient LLM usage** — one call with full workspace context
- **Consistent output** — all repos see the same service dependency map
- **Top-level system docs** — C4, service index, cross-service runbooks
- **Idempotent** — hand-authored content preserved across re-runs
- **Parallel execution** — all repos scaffold independently
- **Monorepo + multirepo support** — flexible deployment model

### ⚠️ Tradeoffs

- **Complexity:** Added WorkspaceDetector, WorkspaceContextAggregator, TopLevelScaffolder
- **Template expansion:** New templates for workspace-top-level in both modern and legacy families
- **Discovery heuristics:** Repo detection relies on stack signatures (go.mod, package.json, etc.)
  - Can be configured via `.doctyze.workspace.yaml`
- **Single LLM call:** All placeholders in one extraction request
  - Risk: very large workspace could hit token limits
  - Mitigation: streaming + batching strategies in future

## Alternatives Considered

### 1. Sequential per-repo scaffolding + external aggregation
- Run doctyze on each repo separately
- External script aggregates results
- **Rejected:** N API calls, no context sharing, manual orchestration

### 2. Doctyze as a library (programmatic API)
- Python/JS library instead of CLI tool
- User scripts orchestrate multi-repo
- **Rejected:** Moves complexity to users, loses CLI benefits

### 3. Git submodules or monorepo hooks
- Pre-commit hook runs doctyze on changed repos
- **Rejected:** Only handles incremental, not full workspace refresh

## Implementation Plan

- [x] Extend Scaffolder with `idempotent` flag and `SKIP`/`MERGE` status
- [x] Create WorkspaceDetector to find service repos
- [x] Create WorkspaceContextAggregator to build service map
- [x] Create TopLevelScaffolder for workspace-level templates
- [x] Add `doctyze workspace` CLI command
- [x] Workspace templates for modern and legacy families
- [x] Update README with workspace examples
- [ ] Integration tests for workspace mode
- [ ] GitHub issue #14 resolution

## Related Docs

- [ADR-0001: Record Architecture Decisions](./0001-record-architecture-decisions.md)

## References

- [AGENTS.md specification](https://agents.md)
- [C4 Model](https://c4model.com/)
- [Architecture Decision Records (ADR)](https://adr.github.io/)

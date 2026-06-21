---
name: write-runbook
description: Operational + deployment runbooks under docs/runbooks/, grounded in the ops/CI/deploy config.
---
# write-runbook
Write runbooks in `docs/runbooks/` (including deployment).

## Before you write
Read existing ops/deploy docs; refresh, don't duplicate.

## How
1. Read CI/CD pipelines, Dockerfile, IaC, scripts, health endpoints, `settings`.
2. Document: build/run locally, deploy per environment, rollback, common operational tasks. One runbook per concern (`deployment.md`, `operations.md`, incident-specific ones).
3. Ground in real files; cite paths.

## Anchor (narrow)
`affects:` = the deploy/ops files (Dockerfile, pipeline yaml, scripts, settings), not `app/**`.

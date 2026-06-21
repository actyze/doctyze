---
name: write-observability
description: Incident-investigation, metrics, logging, and alerting docs under docs/observability/.
---
# write-observability
Write `docs/observability/` docs covering how to investigate incidents.

## Before you write
Read existing observability/logging docs; refresh, don't duplicate.

## How
1. Read logging/metrics/tracing/alerting config and the error-code registry — cite real modules.
2. Document: key signals & dashboards, how to triage common failures, escalation, the error-code map, resilience/breaker monitoring.
3. Ground in real code; honest about gaps.

## Anchor (narrow)
`affects:` = the observability/logging/resilience/exceptions modules, not `app/**`.

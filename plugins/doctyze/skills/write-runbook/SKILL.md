---
name: write-runbook
description: Create operational and deployment runbooks under docs/runbooks/ from the ops/CI/deploy configuration.
---
# write-runbook
Write step-by-step runbooks in `docs/runbooks/` (one per concern; deployment lives here too).

## Sections
- **Local setup** — install/build/run locally.
- **Test** — how to run the test suite.
- **Deploy** — how the service ships, per environment (cite the pipelines/IaC).
- **Rollback** — how to revert a bad deploy.
- **Common operations** — routine tasks, plus incident-specific runbooks (e.g. `high-error-rate.md`).

## Rules
Read CI/CD pipelines, Dockerfiles, IaC, scripts, Makefile targets — describe what they actually do.

## Anchor (required) — `affects` the ops files this runbook describes
```yaml
---
doctyze:
  artifact: runbook
  generated_by: write-runbook
  affects: [.github/workflows/**, Dockerfile, scripts/**]
  last_verified: <YYYY-MM-DD>
---
```

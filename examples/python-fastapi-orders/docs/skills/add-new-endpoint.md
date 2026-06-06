---
name: add-new-endpoint
description: Use when adding a new HTTP endpoint or changing an existing endpoint's public contract. Ensures docs/api/openapi.yaml, specs, and runbooks update in the same PR.
---

# How to add a new endpoint in orders-api

## When to apply

- Adding a new FastAPI route
- Modifying request/response schemas of an existing route
- Adding a new version of an existing route (`/v1/...` → `/v2/...`)

## Required updates (all in the same PR)

### 1. Code

Implement the endpoint in `src/orders/api/` per FastAPI conventions. Follow
the existing patterns for auth dependency injection, error handling, and
response models.

### 2. OpenAPI contract

Update `docs/api/openapi.yaml`:

- Add the new path with full request/response schemas
- Reference component schemas in `components/schemas/`
- Declare auth scope in `security:` block

### 3. Spec

Update `docs/specs/<feature>/spec.md` with the new endpoint, including
a worked request/response example.

### 4. Runbook (placeholder is fine)

At minimum, add a placeholder for the most likely failure mode of the new
endpoint to `docs/runbooks/`. The Doctyze PR review will accept a
TODO-marked stub; it just can't be missing.

### 5. ADR (only if architecturally significant)

If the endpoint introduces a new external call, a new auth method, or a
new trust boundary, write an ADR. Otherwise skip.

## Naming & versioning

- Path style: `/api/v{N}/<resource>` (kebab-case for paths, snake_case
  for query params and body fields)
- HTTP methods: strict REST
- Auth: every endpoint declares its scope in OpenAPI's `security:`
- Versioning: never modify a v1 endpoint's contract; add v2 instead

## Don't

- Don't expose internal fields in response DTOs (PII risk)
- Don't skip the runbook placeholder — Doctyze PR review will reject
- Don't change existing endpoint contracts in place; add a new version
- Don't introduce a new auth method without an ADR

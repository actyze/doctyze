---
name: add-new-endpoint
description: Use when adding a new REST/gRPC endpoint or changing an existing endpoint's public contract. Ensures docs/api/openapi.yaml, specs, and runbooks update in the same PR.
---

# How to add a new endpoint in this repo

## When to apply

The developer is:

- **Adding a new HTTP / gRPC endpoint** (any new route handler)
- **Modifying the public contract** of an existing endpoint (request schema,
  response schema, status codes, headers, auth)
- **Adding a new version** of an endpoint (e.g., `/api/v2/...`)

## Required updates (all in the same PR)

### 1. Code
Implement the endpoint per `src/api/` conventions. Follow the existing
naming, auth, and error-handling patterns.

### 2. OpenAPI contract
Update `docs/api/openapi.yaml`:

- Add the new path with full request/response schemas
- Reference component schemas in `components/schemas/`
- Declare auth scopes in `security:` block

### 3. Spec
Update the relevant spec at `docs/specs/<feature>/spec.md`:

- Add or modify the **Requirements** section with `REQ-NNN` ID(s)
- Include a worked request/response example

### 4. Runbook
At minimum, add a placeholder runbook entry for the most likely failure
mode (timeout, auth failure, payload too large) in `docs/runbooks/`.
Even a stub is better than nothing — the bot will block PRs without it.

### 5. ADR (only if architecturally significant)
If the endpoint:
- Introduces a new sync external call
- Adds a new persistence path
- Adopts a non-standard auth scheme
- Crosses a new trust boundary

…then write an ADR. Otherwise skip.

## Naming conventions

- Path style: `/api/v{N}/<resource>` (kebab-case)
- HTTP methods: strict REST — POST creates, PUT replaces, PATCH partial-updates
- Versioning: never modify a v1 endpoint's contract; add v2 instead
- Auth scopes: declare explicitly in OpenAPI's `security:` block

## Don't

- Don't expose internal fields in response DTOs (PII leak risk)
- Don't skip the runbook placeholder — the bot will reject the PR
- Don't change existing endpoint contracts in place; add a new version
- Don't introduce a new auth method without an ADR

## Doctyze enforcement

The PR review bot blocks merge when:
- A new route handler is added but `docs/api/openapi.yaml` is unchanged
- A response DTO field is added/removed but OpenAPI schemas don't reflect it
- A new error path is introduced but no runbook references it

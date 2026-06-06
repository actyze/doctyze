# orders-api — Agent context

> This file follows the AGENTS.md / AAIF standard. Read by every AI coding
> agent (Claude Code, Codex CLI, Cursor, Copilot, Cline, Windsurf, Aider).

## What this service does

A small FastAPI orders service. Accepts orders, validates them, persists to
Postgres, fires an event. Used as a Doctyze worked example, not a production
service.

## Hard constraints

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (see ADR-0002)
- **Pricing dependency**: fails open per ADR-0003 — never block an order
  on a pricing-service error
- **License**: Apache 2.0

## Code conventions

- `ruff` + `black` for lint/format, settings in `pyproject.toml`
- `pytest` for tests; coverage target 80% on new code
- Endpoints follow REST: POST creates, PUT replaces, PATCH partial-updates
- All endpoints declare auth scope in `docs/api/openapi.yaml`
- Errors raise `HTTPException` with structured detail; no string-only messages

## Build commands

```bash
pip install -e .
pytest
uvicorn orders.main:app --reload
```

## Gotchas worth knowing

- **Pricing fails open.** If the pricing service is unreachable, we apply
  the SKU's last-known price and log a warning. This is desired behavior
  per ADR-0003. Do not "fix" this by raising an exception — it will cause
  a customer-visible outage that the design specifically prevents.
- **Order IDs are ULIDs**, not UUIDs. Sortable by creation time.
- **Idempotency**: POST /orders accepts an `Idempotency-Key` header;
  duplicate requests within 24h return the original response, not a new order.

## Where decisions live

- ADRs: [docs/architecture/decisions/](docs/architecture/decisions/)
- Runbooks: [docs/runbooks/](docs/runbooks/)
- Specs: [docs/specs/](docs/specs/)
- API contract: [docs/api/openapi.yaml](docs/api/openapi.yaml)

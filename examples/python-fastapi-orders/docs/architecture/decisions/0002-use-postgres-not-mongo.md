# ADR-0002 — Use PostgreSQL for the orders store

- Status: accepted
- Date: 2026-06-06
- Confidence: 🟢 CONFIRMED

## Context

The orders service needs durable storage with:

- Strong consistency (an order either exists or doesn't — no eventual-consistency
  surprises for the customer)
- Rich querying (orders by customer, by SKU, by date range, by status)
- Indexability on multiple columns
- A path to read-replicas as we scale
- Schema evolution we can review in PRs

## Decision

PostgreSQL 16+. One Postgres cluster per environment; orders live in a single
`orders` schema. Migrations managed via Alembic, reviewed in PR.

## Alternatives rejected

- **MongoDB** — fits the "order document" shape on its face, but our actual
  queries are highly relational (joins to customers, products, shipping
  addresses). The denormalization MongoDB would force on us is operational
  debt the team has been burned by before.
- **DynamoDB** — single-key access pattern is fine, but our analytics team
  needs ad-hoc SQL queries against the orders data. Adding a Postgres
  replica for them on top of DynamoDB is two systems where one would do.
- **MySQL** — workable, but Postgres has stronger JSONB support (we use it
  for order metadata) and our team is more experienced with Postgres
  operationally.
- **Cockroach / Yugabyte** — overkill for our scale; would push us into
  distributed-SQL operational complexity we don't yet need.

## Consequences

- (+) Standard, well-understood SQL access patterns.
- (+) JSONB lets us store order metadata flexibly without a separate doc store.
- (+) Strong consistency by default.
- (−) Single-cluster scale ceiling. We'll need to shard or move to a
  distributed-SQL system if we hit ~10k orders/sec.
- (−) Schema migrations require discipline (Alembic, reviewed in PRs).

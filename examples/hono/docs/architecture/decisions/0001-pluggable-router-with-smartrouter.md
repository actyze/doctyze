---
doctyze:
  artifact: adr
  generated_by: write-adr
  affects: [src/router.ts, src/router/smart-router/router.ts, src/router/reg-exp-router/router.ts, src/router/trie-router/router.ts, src/hono.ts]
  last_verified: 2026-07-05
---
# ADR-0001: A pluggable Router interface with a runtime-selecting SmartRouter

**Status:** 🟢 ACCEPTED (reverse-engineered from the code — describes Hono's existing design)
**Date:** 2026-07-05
**Deciders:** Hono maintainers (inferred)

> Reverse-engineered by Doctyze from the code as a demonstration of the `write-adr` skill. It documents
> a decision Hono already embodies; it is not a proposal to change Hono.

## Context

Routing is the hot path of a web framework — every request pays for a match. But no single matching
strategy is best for every route table:

- A **regex** approach can pre-compile an entire method's routes into one large `RegExp`, giving very
  fast matching, but it cannot express every path pattern.
- A **trie** walk handles every pattern (nested params, wildcards, optional segments) at a modest,
  predictable cost.

Forcing users to hand-pick a matcher would be a footgun (the fast one silently fails on some routes),
and hard-wiring one matcher would leave performance or generality on the table. The core also needs to
stay decoupled from matching so alternative strategies can exist. **How should Hono match routes so
that the common case is fast, every pattern still works, and the strategy is swappable?**

## Decision

Hono defines a minimal **`Router<T>` interface** (`router.ts`) with just three members — `name`,
`add(method, path, handler)`, and `match(method, path): Result<T>` — and ships several
implementations: `RegExpRouter`, `TrieRouter`, `LinearRouter`, and `PatternRouter`. The app
(`hono-base.ts`) depends only on this interface.

The default matcher is a **meta-router, `SmartRouter`** (`router/smart-router/router.ts`), which the
`Hono` constructor (`hono.ts`) instantiates as
`new SmartRouter({ routers: [new RegExpRouter(), new TrieRouter()] })`. `SmartRouter`:

- **buffers** every `add` into an internal `#routes` list instead of committing to a matcher up front;
- on the **first** `match`, replays all buffered routes into each candidate router in order and calls
  `match`. If a candidate throws `UnsupportedPathError` while ingesting the routes, `SmartRouter`
  moves on to the next candidate;
- once a candidate succeeds, **locks it in**: it rebinds `this.match = router.match.bind(router)`,
  reduces `#routers` to the winner, and clears the buffer — so every subsequent request matches with
  zero selection overhead. Its `name` reports the choice, e.g. `"SmartRouter + RegExpRouter"`.

In effect the route table itself decides the matcher: if `RegExpRouter` can compile it, you get the
fast path; otherwise Hono transparently falls back to `TrieRouter`.

## Rationale

1. **Interface over implementation.** A three-method `Router<T>` is a tiny contract, so the framework
   is agnostic to matching strategy and users can inject their own via `new Hono({ router })`.
2. **Fast-by-default, correct-always.** Deferring the choice to the first `match` lets Hono attempt the
   fastest matcher and fall back only when a real route needs it — no configuration, no silent failure.
3. **`UnsupportedPathError` as the selection signal.** Making "I can't express this path" an explicit,
   catchable error (rather than a wrong match) is what makes automatic fallback safe.
4. **One-time cost.** Selection happens once; rebinding `match` to the winner removes the abstraction
   from the steady-state hot path.

## Consequences

- **Positive:** best-available routing performance with zero tuning; full pattern support; a clean
  extension seam (custom routers, or presets like `hono/quick` / `hono/tiny` that pick a specific
  matcher).
- **Tradeoff:** the first matched request pays to build **every** candidate matcher until one succeeds,
  and routes are buffered in memory until then — a latency/allocation cost concentrated on cold start.
- **Constraint:** adding a route after the matcher is built throws
  `MESSAGE_MATCHER_IS_ALREADY_BUILT`; route registration must finish before the first request.
- **Constraint:** if no candidate can serve the table, `SmartRouter.match` throws a fatal error — the
  set of routers must jointly cover every supported pattern (the default `[RegExpRouter, TrieRouter]`
  pair does).

## Related
- [Architecture overview](../overview.md) · [App & routing](../../specs/app-and-routing.md) ·
  [Object model](../diagrams/object-model.md)

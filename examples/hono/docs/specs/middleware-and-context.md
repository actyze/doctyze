---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/compose.ts, src/context.ts, src/request.ts, src/types.ts]
  last_verified: 2026-07-05
---
# Spec — Middleware & context

## Summary

Hono runs a matched route's handlers as a Koa-style **onion**: `compose` (`compose.ts`) turns the
`[handler, …]` array into one async function where each middleware calls `next()` to descend into the
next layer and awaits it. Every handler receives the same per-request `Context` (`c`) — the object
that carries request state and builds the response — whose `c.req` is a `HonoRequest` wrapping the raw
`Request`.

## Definitions (grounded in code)

| Concept | Where | Meaning |
|---|---|---|
| `compose` | `compose.ts` | Composes middleware into `(context, next?) => Promise<Context>`; derived from `koa-compose`. |
| `Handler` / `MiddlewareHandler` | `types.ts` | `(c, next) => Response \| …`. A `MiddlewareHandler` returns `Promise<Response \| void>`; `H` is the union of the two. |
| `Next` | `types.ts` | `() => Promise<void>` — the callback each middleware invokes to run the rest of the chain. |
| `Context` | `context.ts` | Per-request object (`c`): `env`, `error`, `finalized`, `req`, and the response builders. |
| `HonoRequest` | `request.ts` | Wrapper over the raw `Request`: `param`, `query`, `header`, body parsers, `valid`. |

## Behavior

### The onion (`compose`)
`compose(middleware, onError?, onNotFound?)` returns a function that starts `dispatch(0)`. For index `i`:

1. A monotonic `index` cursor guards against re-entry — `if (i <= index) throw 'next() called multiple times'`.
2. The handler at position `i` is `middleware[i][0][0]`; `context.req.routeIndex` is set to `i` so
   `c.req.param()` resolves against the right matched route.
3. The handler is called as `handler(context, () => dispatch(i + 1))`. Awaiting `next()` runs the rest
   of the chain, so any code a middleware places **after** `await next()` executes on the way back out.
4. A thrown `Error` is caught: if `onError` is set, it becomes `context.error`, `onError` produces the
   response, and `isError` is flagged; otherwise the error re-throws.
5. Past the last handler, if the response is still not finalized and `onNotFound` is set, the
   not-found handler runs.
6. The result is committed with `if (res && (context.finalized === false || isError)) context.res = res`
   — i.e. a returned `Response` becomes `c.res` unless the context was already finalized (and errors
   always overwrite).

### The `Context` (`c`)
A `Context` is constructed by `#dispatch` with the `matchResult`, `env`, `executionCtx`, `path`, and
`notFoundHandler`. Notable members (`context.ts`):

- **Request/response:** `c.req` (lazily builds the `HonoRequest`), `c.res` (lazily creates an empty
  `Response`; assigning it sets `finalized = true` and merges prior headers), `c.finalized`, `c.error`.
- **Response builders:** `c.body`, `c.text`, `c.json`, `c.html`, `c.newResponse`, `c.redirect`
  (default `302`), and `c.notFound`. `c.text` takes a fast path returning a bare `new Response(text)`
  when no headers/status were set; `c.json` serializes with `JSON.stringify` and defaults
  `Content-Type: application/json`.
- **Headers/status:** `c.header(name, value, { append })` and `c.status(code)` (buffered and applied
  by the next builder).
- **Per-request variables:** `c.set(key, value)` / `c.get(key)` back a private `Map`, and `c.var`
  returns a read-only snapshot. Middleware uses these to pass data down the chain (e.g. an
  authenticated user).
- **Rendering:** `c.setRenderer` / `c.render` / `c.setLayout` support layout-based HTML responses.
- **Runtime handles:** `c.env` (bindings/env), `c.executionCtx` (throws if absent), and `c.event`
  (throws unless a `FetchEvent` is present).

### `HonoRequest`
`c.req` (`request.ts`) wraps the raw `Request` and adds routing-aware accessors:

- `c.req.param('id')` / `c.req.param()` read path params out of the router `matchResult` (URL-decoded
  on demand), keyed by the current `routeIndex`.
- `c.req.query` / `c.req.queries` read the query string; `c.req.header` reads request headers.
- Body accessors `json` / `text` / `arrayBuffer` / `bytes` / `blob` / `formData` / `parseBody` share a
  `bodyCache` so the body can be read more than once without re-consuming the stream.
- `c.req.valid(target)` returns data stashed by validator middleware via `addValidatedData`.

## Invariants
- One `Context` exists per request and is shared by reference across the whole middleware chain — so a
  value `c.set` in an early middleware is visible to every later handler.
- `next()` may be called at most once per middleware invocation.
- The request body may be consumed repeatedly through `HonoRequest`'s methods because of `bodyCache`;
  consuming `c.req.raw` directly bypasses that cache.

## Edge cases
- If the chain completes and `context.finalized` is still `false`, `#dispatch` throws the
  "Context is not finalized…" error — a handler must return a `Response` or `await next()`.
- Assigning `c.res` when a response already exists re-creates it and carefully re-applies previous
  headers, treating `set-cookie` specially so multiple cookies survive.

## Related
- [App & routing](app-and-routing.md) · [Architecture overview](../architecture/overview.md) ·
  [Request lifecycle](../architecture/diagrams/invocation-lifecycle.md)

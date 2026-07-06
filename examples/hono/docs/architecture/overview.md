---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [src/hono.ts, src/hono-base.ts, src/context.ts, src/request.ts, src/compose.ts, src/router.ts]
  last_verified: 2026-07-05
---
# Architecture overview — Hono

Hono is a small, runtime-agnostic web framework built entirely on the Web-standard `Request` /
`Response` types. An app is a tree of registered routes plus middleware; at runtime a single
`fetch(request, env, executionCtx)` entry point resolves the request path against a pluggable
**router**, builds a per-request `Context`, and runs the matched handlers through a Koa-style
middleware **onion** (`compose`). Nothing in the core depends on Node, Bun, Deno, or Workers — each
runtime is bridged by a thin **adapter** that just hands a `Request` to `app.fetch`.

## Layers

The core is deliberately layered so that the app object, the router, and the runtime bindings each
have one job and no knowledge of the layers above them.

| Layer | Module(s) | Responsibility |
|---|---|---|
| **App / registration** | `hono.ts`, `hono-base.ts` | The `Hono` app: `.get/.post/.on/.use/.route/.mount`, `.fetch`, error/404 handlers. Registers routes into the router and dispatches requests. |
| **Router (pluggable)** | `router.ts`, `src/router/*` | The `Router<T>` interface (`name` / `add` / `match`) and its implementations — `RegExpRouter`, `TrieRouter`, `LinearRouter`, `PatternRouter`, and the meta `SmartRouter`. |
| **Request pipeline** | `compose.ts`, `context.ts`, `request.ts` | `compose` runs the matched handler chain as an onion; `Context` (`c`) is the per-request state + response builder; `HonoRequest` wraps the raw `Request`. |
| **Runtime adapters** | `src/adapter/*` | Per-runtime helpers (`serveStatic`, `upgradeWebSocket`, `getConnInfo`, `handle`, `toSSG`) that let one app run on Node/Bun/Deno/Workers/Lambda via `app.fetch`. |
| **Types** | `types.ts` | `Env`, `Handler`, `MiddlewareHandler`, `H`, `Next`, `RouterRoute`, `ErrorHandler`, `NotFoundHandler`, and the heavily-typed handler/route inference. |

## The core objects

- **`Hono` / `HonoBase`** (`hono.ts` extends `hono-base.ts`) — the app. `HonoBase` is written as an
  abstract-style base that intentionally has **no router**; the concrete `Hono` subclass installs one
  in its constructor. The HTTP-verb methods (`get`, `post`, `put`, `delete`, `options`, `patch`,
  `all`) and `on` / `use` are wired up in the `HonoBase` constructor, and every registration funnels
  through the private `#addRoute`, which calls `this.router.add(method, path, [handler, r])` and
  records a `RouterRoute` in `this.routes`.
- **`Router<T>`** (`router.ts`) — a three-member interface: `name`, `add(method, path, handler)`, and
  `match(method, path): Result<T>`. Because the app only depends on this interface, the matcher is
  swappable. `Hono`'s default is a `SmartRouter` that picks the fastest usable matcher at runtime —
  see [ADR-0001](decisions/0001-pluggable-router-with-smartrouter.md).
- **`Context`** (`context.ts`) — one per request, exposed to every handler as `c`. It holds `env`,
  `error`, `finalized`, the lazily-built `req` (`HonoRequest`), and the response builders
  `c.json` / `c.text` / `c.html` / `c.body` / `c.newResponse` / `c.redirect`, plus the per-request
  variable bag `c.set` / `c.get` / `c.var`.
- **`compose`** (`compose.ts`) — a Koa-`compose`-derived function that turns the matched
  `[handler, …]` array into one async function. Each middleware receives `(c, next)`; calling
  `next()` descends to the next layer and awaits it, giving the onion (before → next → after)
  execution model.

## Runtime flow (one request)

```text
app.fetch(request, env, executionCtx)          # the universal entry point (hono-base.ts)
  └─ #dispatch(request, executionCtx, env, method)
       ├─ getPath(request)                      # derive the path (strict / host-aware)
       ├─ router.match(method, path)            # SmartRouter → RegExpRouter | TrieRouter
       ├─ new Context(request, { matchResult, env, executionCtx, notFoundHandler })
       ├─ if exactly one handler → call it directly (fast path, skip compose)
       └─ else compose(matchResult[0], errorHandler, notFoundHandler)(c)
              └─ dispatch(0) → handler(c, () => dispatch(1)) → … → handler(c, () => dispatch(n))
       └─ finalized? return c.res : throw / onNotFound
```

`#dispatch` special-cases `HEAD` (it re-dispatches as `GET` and strips the body) and takes a fast
path when a route matched exactly one handler — in that case `compose` is skipped entirely. Any
thrown `Error` is routed to the app's `errorHandler` (`onError`); an unmatched request falls to the
`notFoundHandler` (`notFound`).

## Multi-runtime

The same `app` object runs everywhere because the runtime only ever needs to call `app.fetch`:
`export default app` on Cloudflare Workers, `Deno.serve(app.fetch)` on Deno,
`Bun.serve({ fetch: app.fetch })` on Bun, and `handle(app)` wrappers for Cloudflare Pages and the
Service Worker API. Runtime-specific capabilities (static files, WebSocket upgrade, connection info)
are opt-in helpers under `src/adapter/*` that read from `c.env`. See
[Multi-runtime adapters](../specs/multi-runtime-adapters.md).

## Diagrams

- [Object model](diagrams/object-model.md) — `Hono` / `Router` / `Context` / `HonoRequest` and how they relate.
- [Request lifecycle](diagrams/invocation-lifecycle.md) — `fetch` → `match` → `compose` → `Response`.

## Key specifications

- [App & routing](../specs/app-and-routing.md)
- [Middleware & context](../specs/middleware-and-context.md)
- [Multi-runtime adapters](../specs/multi-runtime-adapters.md)

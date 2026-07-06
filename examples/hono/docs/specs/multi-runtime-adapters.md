---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/hono-base.ts, src/adapter/cloudflare-workers/index.ts, src/adapter/cloudflare-pages/handler.ts, src/adapter/service-worker/handler.ts, src/adapter/deno/conninfo.ts, src/adapter/bun/server.ts]
  last_verified: 2026-07-05
---
# Spec — Multi-runtime adapters

## Summary

A Hono app is runtime-agnostic because its only runtime contract is a single Web-standard method:
`app.fetch(request, env, executionCtx)` (`hono-base.ts`), which takes a `Request` and returns a
`Response`. Every supported runtime is bridged by handing that method a `Request`; the per-runtime
directories under `src/adapter/*` add *optional* helpers (static file serving, WebSocket upgrade,
connection info, SSG) that read runtime specifics out of `c.env`.

## Definitions (grounded in code)

| Concept | Where | Meaning |
|---|---|---|
| `app.fetch` | `hono-base.ts` | `(request, Env?, executionCtx?) => Response \| Promise<Response>`; forwards to the private `#dispatch`. The universal entry point. |
| Cloudflare Workers adapter | `adapter/cloudflare-workers/index.ts` | Re-exports `serveStatic`, `upgradeWebSocket`, `getConnInfo`. Workers calls `app.fetch(request, env, ctx)` directly via `export default app`. |
| Cloudflare Pages adapter | `adapter/cloudflare-pages/handler.ts` | `handle(app)` returns a `PagesFunction` that calls `app.fetch`. |
| Service Worker adapter | `adapter/service-worker/handler.ts` | `handle(app)` returns a `fetch`-event listener that calls `app.fetch`. |
| Bun adapter | `adapter/bun/server.ts` | `getBunServer(c)` reads the Bun `Server` out of `c.env`. |
| Deno adapter | `adapter/deno/conninfo.ts` | `getConnInfo(c)` reads `c.env.remoteAddr`. |

## Behavior

### The universal entry point
`app.fetch(request, Env?, executionCtx?)` positions its arguments to match the shapes runtimes pass:
`fetch = (request, ...rest) => this.#dispatch(request, rest[1], rest[0], request.method)`. So the
second argument is treated as `env` (bindings) and the third as the `ExecutionContext`. Those two
values become `c.env` and `c.executionCtx`.

### How each runtime attaches
- **Cloudflare Workers** — a module Worker's `export default app` means the runtime invokes
  `app.fetch(request, env, ctx)` itself; the adapter only provides helpers. (`adapter/cloudflare-workers/index.ts`.)
- **Deno** — `Deno.serve(app.fetch)`; the adapter's `getConnInfo` reads `c.env.remoteAddr`
  (`adapter/deno/conninfo.ts`).
- **Bun** — `Bun.serve({ fetch: app.fetch })`; `getBunServer(c)` (`adapter/bun/server.ts`) exposes the
  Bun `Server` that Bun injects into the environment.
- **Cloudflare Pages** — `handle(app)` (`adapter/cloudflare-pages/handler.ts`) returns a `PagesFunction`
  that calls `app.fetch(eventContext.request, { ...eventContext.env, eventContext }, { waitUntil, passThroughOnException, props })`.
  A companion `handleMiddleware` lets a single Hono middleware run as a Pages function.
- **Service Worker** — `handle(app)` (`adapter/service-worker/handler.ts`) returns a listener that does
  `evt.respondWith(app.fetch(evt.request, {}, evt))` and, on a `404`, optionally falls back to the real
  network `fetch`.
- **Node / AWS Lambda / Netlify / Vercel / Lambda@Edge** — additional adapter directories exist under
  `src/adapter/*` following the same pattern: translate the platform's request event into a `Request`,
  call `app.fetch`, and translate the `Response` back.

### Optional per-runtime capabilities
Because the core stays Web-standard, anything a runtime does *beyond* request/response is an opt-in
helper imported from that runtime's adapter and configured through `c.env`:

- `serveStatic` — static asset serving (each runtime resolves files its own way).
- `upgradeWebSocket` — WebSocket upgrade.
- `getConnInfo` — remote address / port / transport, read from the runtime-specific `c.env` shape.
- `toSSG` — static site generation (Bun, Deno).

## Invariants
- The core never imports a runtime SDK; portability comes from depending only on `Request` / `Response`
  and treating `env` / `executionCtx` as opaque pass-throughs.
- `c.executionCtx` and `c.event` throw if the current runtime did not supply them, so handlers that
  need `waitUntil` degrade loudly rather than silently.

## Edge cases
- The Service Worker adapter treats a `404` from `app.fetch` as "not mine" and can defer to the network
  `fetch`, enabling Hono to coexist with other Service Worker routes.
- On Cloudflare Pages the platform's own `eventContext` is threaded into `c.env` so middleware can call
  `eventContext.next()` (see `handleMiddleware`).

## Related
- [Architecture overview](../architecture/overview.md) · [App & routing](app-and-routing.md) ·
  [Request lifecycle](../architecture/diagrams/invocation-lifecycle.md)

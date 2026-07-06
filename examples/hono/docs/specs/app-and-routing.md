---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/hono.ts, src/hono-base.ts, src/router.ts, src/router/smart-router/router.ts, src/router/reg-exp-router/router.ts, src/router/trie-router/router.ts, src/types.ts]
  last_verified: 2026-07-05
---
# Spec — App & routing

## Summary

A Hono app is a `Hono` instance (subclass of `HonoBase`) that holds a `Router` and an ordered list of
`RouterRoute`s. Routes are registered declaratively with the HTTP-verb methods, `on`, and `use`;
matching is delegated to a pluggable `Router<T>` whose default (`SmartRouter`) selects the fastest
usable matcher at runtime.

## Definitions (grounded in code)

| Concept | Where | Meaning |
|---|---|---|
| `HonoBase` | `hono-base.ts` | The app class minus a router. Wires `get/post/…/all`, `on`, `use` in its constructor; owns `#addRoute`, `#dispatch`, `fetch`, `route`, `basePath`, `mount`, `onError`, `notFound`. |
| `Hono` | `hono.ts` | Subclass that installs the default router in its constructor. |
| `Router<T>` | `router.ts` | Interface: `name`, `add(method, path, handler)`, `match(method, path): Result<T>`. |
| `SmartRouter` | `router/smart-router/router.ts` | A `Router` that wraps candidate routers and picks one at first match. |
| `RegExpRouter` / `TrieRouter` | `router/reg-exp-router/router.ts` / `router/trie-router/router.ts` | The two default matcher implementations. `LinearRouter` and `PatternRouter` are additional implementations. |
| `RouterRoute` | `types.ts` | `{ basePath, path, method, handler }` — the metadata record kept in `app.routes`. |

## Behavior

### Registering routes
- The HTTP-verb methods are generated in the `HonoBase` constructor from
  `METHODS = ['get','post','put','delete','options','patch']` plus `all`. Each supports both
  `app.get(path, ...handlers)` and the chained `app.get(handler)` form (a bare handler reuses the
  last path stored on the instance).
- `app.on(method, path, ...handlers)` registers arbitrary/custom methods and accepts arrays of
  methods and paths (it flattens both). `app.use(...)` registers a `MiddlewareHandler` for
  `METHOD_NAME_ALL` (`'ALL'`); with no path it defaults the path to `'*'`.
- Every path ultimately runs through the private `#addRoute(method, path, handler, baseRoutePath?)`,
  which uppercases the method, merges the app's `_basePath`, calls
  `this.router.add(method, path, [handler, r])`, and pushes a `RouterRoute` onto `this.routes`.

### Grouping and mounting
- `app.route(path, subApp)` (`hono-base.ts`) re-registers each of `subApp.routes` under `path` on the
  parent. If the sub-app installed a custom `errorHandler`, its handlers are wrapped so the sub-app's
  error handling is preserved (`compose([], app.errorHandler)` around the original handler).
- `app.basePath(path)` returns a **clone** of the app whose `_basePath` is extended — the clone shares
  the same `router`, `routes`, `errorHandler`, and `notFoundHandler`.
- `app.mount(path, applicationHandler, options?)` mounts a foreign fetch-style handler (e.g.
  itty-router) under `path` by registering a middleware that rewrites the request path and forwards it.

### Matching a request
On `#dispatch`, the app derives the path with `getPath`, calls `router.match(method, path)`, and builds
the `Context` from the `matchResult`. A `Result<T>` is either `[[handler, paramIndexMap][], paramStash]`
or `[[handler, params][]]` (`router.ts`) — the two shapes let matchers return either indexed params
(resolved from a shared stash) or already-materialized param maps.

### Choosing a router (SmartRouter)
`Hono`'s default is `new SmartRouter({ routers: [new RegExpRouter(), new TrieRouter()] })`. `SmartRouter`
buffers every `add` into an internal `#routes` list. On the **first** `match`, it tries each candidate
router in order: it replays all buffered routes into that router and calls `match`. If registration
throws `UnsupportedPathError`, it moves to the next candidate; on success it rebinds
`this.match = router.match.bind(router)`, drops the other candidates, and clears the buffer — so all
later matches go straight to the winner. Its `name` becomes e.g. `"SmartRouter + RegExpRouter"`. See
[ADR-0001](../architecture/decisions/0001-pluggable-router-with-smartrouter.md).

## Invariants
- The app depends only on the `Router<T>` interface, so a caller can pass any conforming matcher via
  `new Hono({ router })` and the rest of the framework is unchanged.
- Route registration order is preserved in `app.routes`, and middleware registered with `use('*')`
  matches ahead of more specific routes because it is stored under `METHOD_NAME_ALL`.
- Adding a route after a matcher has been built throws
  `MESSAGE_MATCHER_IS_ALREADY_BUILT` ("Can not add a route since the matcher is already built.").

## Edge cases
- `HEAD` is never matched as `HEAD`: `#dispatch` re-dispatches it as `GET` and returns a null-body
  response with the same headers/status.
- A route that matched exactly one handler skips `compose` entirely (a measured fast path).
- `RegExpRouter` cannot express every pattern; when a path is unsupported it raises
  `UnsupportedPathError`, which is precisely the signal `SmartRouter` uses to fall back to `TrieRouter`.

## Related
- [Middleware & context](middleware-and-context.md) · [Architecture overview](../architecture/overview.md) ·
  [ADR-0001: Pluggable Router with a runtime-selecting SmartRouter](../architecture/decisions/0001-pluggable-router-with-smartrouter.md)

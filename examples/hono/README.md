# Example — [honojs/hono](https://github.com/honojs/hono) (TypeScript)

The **code-grounded structured docs Doctyze generated for Hono**, reverse-engineered from its source at
commit [`d6b1d32`](https://github.com/honojs/hono/tree/d6b1d32a697ef9ba9f5036753fe9bde1121c0ff9). See
[PROVENANCE.md](./PROVENANCE.md) for exact source/version and scope.

Each doc is anchored to the `src/*.ts` it describes, so a code change flags it stale (demonstrated in
PROVENANCE).

## What's in `docs/`

| Doc | Grounded in |
|---|---|
| [architecture/overview.md](docs/architecture/overview.md) | The core: app (`Hono`/`HonoBase`), routing, middleware compose, `Context`, multi-runtime adapters |
| [architecture/diagrams/object-model.md](docs/architecture/diagrams/object-model.md) | `Hono` / `Router` / `Context` / `HonoRequest` relationships (Mermaid) |
| [architecture/diagrams/invocation-lifecycle.md](docs/architecture/diagrams/invocation-lifecycle.md) | `fetch(request)` → route match → middleware onion → handler (Mermaid) |
| [specs/app-and-routing.md](docs/specs/app-and-routing.md) | `Hono`, `.get/.post/.on/.route`, the `Router` interface + `SmartRouter`/`RegExpRouter`/`TrieRouter` |
| [specs/middleware-and-context.md](docs/specs/middleware-and-context.md) | `compose.ts` onion model, `next()`, the `Context` object and `c.*` helpers, `HonoRequest` |
| [specs/multi-runtime-adapters.md](docs/specs/multi-runtime-adapters.md) | How one app runs on Node/Bun/Deno/Workers via `app.fetch(request, env, executionCtx)` |
| [architecture/decisions/0001-pluggable-router-with-smartrouter.md](docs/architecture/decisions/0001-pluggable-router-with-smartrouter.md) | Why a pluggable `Router` interface + a runtime-selecting `SmartRouter` |

> Source-file references are by filename at the
> [pinned commit](https://github.com/honojs/hono/tree/d6b1d32a697ef9ba9f5036753fe9bde1121c0ff9/src).

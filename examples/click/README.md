# Example — [pallets/click](https://github.com/pallets/click) (Python)

The **code-grounded structured docs Doctyze generated for Click**, reverse-engineered from its source at
commit [`16fc00e`](https://github.com/pallets/click/tree/16fc00e2f4a2717a521084f193709a6058afc693). See
[PROVENANCE.md](./PROVENANCE.md) for exact source/version and scope.

Click already has excellent hand-written narrative docs; what it lacked was a spec/architecture/ADR layer
tied to the code. That's what Doctyze added here — and each doc is anchored to the `src/click/*.py` it
describes, so a code change flags it stale (demonstrated in PROVENANCE).

## What's in `docs/`

| Doc | Grounded in |
|---|---|
| [architecture/overview.md](docs/architecture/overview.md) | The four layers: decorators → core object model → parser → types |
| [architecture/diagrams/object-model.md](docs/architecture/diagrams/object-model.md) | `Command` / `Group` / `Parameter` / `Context` class relationships (Mermaid) |
| [architecture/diagrams/invocation-lifecycle.md](docs/architecture/diagrams/invocation-lifecycle.md) | `argv` → parse → convert → invoke, for a nested command (Mermaid) |
| [specs/command-and-group-model.md](docs/specs/command-and-group-model.md) | `Command`/`Group`/`CommandCollection`, subcommand resolution, chaining |
| [specs/parameter-processing.md](docs/specs/parameter-processing.md) | The parse → `process_value` → `ParamType.convert` pipeline; `ParameterSource` |
| [specs/parameter-types.md](docs/specs/parameter-types.md) | `ParamType` and the built-in types (`Choice`, `IntRange`, `File`, `Path`, `Tuple`, …) |
| [architecture/decisions/0001-context-threads-invocation-state.md](docs/architecture/decisions/0001-context-threads-invocation-state.md) | Why a per-command `Context` (with `parent`) threads nested state |

> Source-file links in these docs are repo-relative to click's tree; browse them at the
> [pinned commit](https://github.com/pallets/click/tree/16fc00e2f4a2717a521084f193709a6058afc693/src/click).

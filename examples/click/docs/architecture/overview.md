---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [src/click/core.py, src/click/decorators.py, src/click/parser.py, src/click/types.py]
  last_verified: 2026-07-05
---
# Architecture overview — Click

Click is a library for building command-line interfaces by *composing* small, self-describing
objects. A CLI author writes ordinary Python functions and annotates them with decorators; Click
turns each function into a `Command`, wires its `Parameter`s, and — at runtime — parses `argv`,
converts each value through a typed `ParamType`, and invokes the function inside a `Context` that
threads shared state through arbitrarily nested subcommands.

## Layers

Click is organized as four cooperating layers. Higher layers depend on lower ones; the lower layers
have no knowledge of the decorator sugar above them.

| Layer | Module(s) | Responsibility |
|---|---|---|
| **Declarative API** | [`decorators.py`](../../../src/click/decorators.py) | `@command` / `@group` / `@option` / `@argument` and the `pass_*` family. Attach `Parameter`s to a function, then build a `Command` from it. |
| **Object model** | [`core.py`](../../../src/click/core.py) | `Context`, `Command`, `Group`, `CommandCollection`, `Parameter`, `Option`, `Argument`. The runtime that parses, converts, and invokes. |
| **Parsing** | [`parser.py`](../../../src/click/parser.py) | The internal `_OptionParser` — turns a raw token list into (option, argument) assignments. Deliberately private. |
| **Type system** | [`types.py`](../../../src/click/types.py) | `ParamType` and its built-ins (`Choice`, `IntRange`, `File`, `Path`, `Tuple`, …) — convert + validate a raw string into a Python value. |

Supporting modules: [`formatting.py`](../../../src/click/formatting.py) (help/usage rendering),
[`termui.py`](../../../src/click/termui.py) (prompts, progress bars, styling),
[`exceptions.py`](../../../src/click/exceptions.py) (the `UsageError` hierarchy that becomes formatted
output instead of tracebacks), and [`shell_completion.py`](../../../src/click/shell_completion.py).

## The core objects

- **`Context`** ([`core.py:204`](../../../src/click/core.py)) — one per invoked command. Holds the parsed
  `params`, the user object `obj`, a free-form `meta` map, and a `parent` link. Because each nested
  command gets a child `Context` pointing at its parent, shared state (a DB handle, a config) set on a
  parent group is reachable from any subcommand. See [ADR-0001](decisions/0001-context-threads-invocation-state.md).
- **`Command`** ([`core.py:956`](../../../src/click/core.py)) — the fundamental invocable unit. Its
  lifecycle methods are `make_context()` → `parse_args()` → `invoke()`, driven by the public entry point
  `main()`. `main()` is what `if __name__ == "__main__"` ultimately calls.
- **`Group(Command)`** ([`core.py:1601`](../../../src/click/core.py)) — a `Command` that dispatches to
  registered subcommands via `add_command()` / `get_command()` / `list_commands()` / `resolve_command()`.
  Flags `chain`, `invoke_without_command`, and `result_callback` control multi-command invocation.
- **`Parameter(ABC)`** ([`core.py:2139`](../../../src/click/core.py)) — base for `Option` and `Argument`.
  Owns the parse→convert→validate pipeline (`handle_parse_result()` → `process_value()`) and records
  where each value came from via `ParameterSource`.

## Runtime flow (one invocation)

```text
main(argv)                        # Command.main — the entry point
  └─ make_context()               # build a Context (link to parent if nested)
       └─ parse_args()            # _OptionParser splits argv into opt/arg assignments
            └─ for each Parameter:
                 handle_parse_result()
                   └─ process_value()
                        └─ ParamType.convert()   # typed coercion + validation; UsageError on failure
  └─ invoke()                     # call the user's callback with converted **params
       └─ (Group) resolve_command() → recurse into the subcommand's Context
```

A `Group` invocation runs the group's own callback (if `invoke_without_command`), then resolves the next
`argv` token to a subcommand and recurses — each hop creating a child `Context`. With `chain=True`, a
single command line may name several subcommands in sequence, and `result_callback` receives all their
return values.

## Diagrams

- [Object model](diagrams/object-model.md) — the class relationships (`Command`/`Group`/`Parameter`/`Context`).
- [Invocation lifecycle](diagrams/invocation-lifecycle.md) — the parse → convert → invoke sequence for a nested command.

## Key specifications

- [Command & group model](../specs/command-and-group-model.md)
- [Parameter processing](../specs/parameter-processing.md)
- [Parameter type system](../specs/parameter-types.md)

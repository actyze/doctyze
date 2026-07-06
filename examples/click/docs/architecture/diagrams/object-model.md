---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [src/click/core.py]
  last_verified: 2026-07-05
---
# Object model

The runtime objects in [`core.py`](../../../../src/click/core.py) and how they relate. `Group` is a
`Command` (so groups nest like commands), and `Option`/`Argument` are both `Parameter`s.

```mermaid
classDiagram
    class Context {
        +Command command
        +Context parent
        +dict params
        +Any obj
        +dict meta
        +invoke(callback)
        +get_parameter_source(name)
    }
    class Command {
        +str name
        +list~Parameter~ params
        +Callable callback
        +make_context(info_name, args)
        +parse_args(ctx, args)
        +invoke(ctx)
        +main(args)
    }
    class Group {
        +bool chain
        +bool invoke_without_command
        +add_command(cmd, name)
        +get_command(ctx, name)
        +list_commands(ctx)
        +resolve_command(ctx, args)
    }
    class CommandCollection {
        +list~Group~ sources
    }
    class Parameter {
        <<abstract>>
        +str name
        +ParamType type
        +bool required
        +Any default
        +handle_parse_result(ctx, opts, args)
        +process_value(ctx, value)
    }
    class Option
    class Argument
    class ParamType {
        <<abstract>>
        +convert(value, param, ctx)
        +fail(message)
    }

    Command <|-- Group
    Group <|-- CommandCollection
    Parameter <|-- Option
    Parameter <|-- Argument
    Command "1" o-- "many" Parameter : params
    Parameter "1" --> "1" ParamType : type
    Command ..> Context : make_context()
    Context "child" --> "parent" Context : parent
    Group ..> Command : dispatches to
```

Notes grounded in the code:

- **`Group <|-- CommandCollection`** ([`core.py:2071`](../../../../src/click/core.py)) — a collection
  merges the subcommands of several source groups behind one namespace.
- **`Context.parent`** is the mechanism behind nested state sharing (see
  [ADR-0001](../decisions/0001-context-threads-invocation-state.md)).
- Every `Parameter` delegates coercion to its `ParamType.convert()` — the type system is the single
  place values become non-string Python objects.

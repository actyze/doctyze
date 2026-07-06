---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [src/click/core.py, src/click/parser.py, src/click/types.py]
  last_verified: 2026-07-05
---
# Invocation lifecycle

What happens between `argv` and the user's callback, for a group with one subcommand
(`app db migrate --steps 3`). Grounded in `Command.main` / `parse_args` / `invoke`
([`core.py`](../../../../src/click/core.py)) and `_OptionParser` ([`parser.py`](../../../../src/click/parser.py)).

```mermaid
sequenceDiagram
    autonumber
    participant U as argv
    participant G as Group (app)
    participant P as _OptionParser
    participant T as ParamType
    participant S as Subcommand (migrate)

    U->>G: main(["db", "migrate", "--steps", "3"])
    G->>G: make_context() → Context(app)
    G->>P: parse_args(ctx, args)
    P-->>G: opts/args split; remaining = ["migrate", "--steps", "3"]
    G->>G: invoke(ctx)
    Note over G: invoke_without_command? run group callback first
    G->>G: resolve_command() → picks "migrate"
    G->>S: recurse with child Context(parent=app)
    S->>P: parse_args(ctx, ["--steps", "3"])
    loop each Parameter
        S->>S: handle_parse_result() → process_value()
        S->>T: convert("3", param, ctx)
        T-->>S: 3  (or raises UsageError → formatted message)
    end
    S->>S: invoke(ctx) → callback(steps=3)
    Note over S: obj/meta set on app's Context<br/>are reachable here via ctx.parent
```

Key facts:

- **Failure path:** if `ParamType.convert()` calls `fail()`, Click raises a `UsageError`
  ([`exceptions.py`](../../../../src/click/exceptions.py)) that `main()` catches and renders as a
  usage message + non-zero exit — the user never sees a traceback.
- **`chain=True`** groups loop `resolve_command()` over the remaining tokens, invoking several
  subcommands in one run; `result_callback` then receives the list of their return values.
- **Parameter processing order** is not source order — `iter_params_for_processing()`
  ([`core.py:138`](../../../../src/click/core.py)) orders parameters so that eager options
  (e.g. `--help`, `--version`) and dependencies resolve correctly.

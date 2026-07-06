---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/click/core.py, src/click/parser.py]
  last_verified: 2026-07-05
---
# Spec — Parameter processing

## Summary

Every value a command receives flows through one pipeline: the low-level `_OptionParser` splits `argv`
into raw assignments, then each `Parameter` runs `handle_parse_result() → process_value()` to apply the
default, coerce via its `ParamType`, enforce `required`/`nargs`, and record a `ParameterSource`.

## The pipeline (grounded in code)

```text
_OptionParser.parse_args()            # parser.py:298 — raw tokens → {opt: value}, [args]
   ↓
Parameter.handle_parse_result()       # core.py:2677 — pick the raw value for this param
   ↓
Parameter.process_value()             # core.py:2550 — default → convert → validate
   ↓  (delegates coercion)
ParamType.convert()                   # types.py — typed value, or .fail() → UsageError
```

- **Parsing** — `_OptionParser` ([`parser.py:224`](../../../src/click/parser.py)) matches long opts
  (`_match_long_opt`), short/combined opts (`_match_short_opt`, so `-xvf` works), and positional
  arguments against the parameters registered via `add_option` / `add_argument`. It is deliberately
  private (underscore-prefixed) — Click reserves the right to change it.
- **Value selection** — `handle_parse_result()` ([`core.py:2677`](../../../src/click/core.py)) chooses
  the raw value for a parameter, considering the parsed opts, the environment
  (`envvar`), and the context `default_map`.
- **Conversion & validation** — `process_value()` ([`core.py:2550`](../../../src/click/core.py)) applies
  the default when absent, runs it through `ParamType.convert()` (once per item when `nargs != 1`),
  applies any `callback`, and enforces `required`.

## ParameterSource

Click records **where** each value came from, exposed via `Context.get_parameter_source(name)`. As of
8.3.3 `ParameterSource` ([`core.py:165`](../../../src/click/core.py)) is an `IntEnum` ordered
most→least explicit:

| Member | Meaning |
|---|---|
| `PROMPT` | Obtained via an interactive prompt |
| `COMMANDLINE` | Given as a CLI argument |
| `ENVIRONMENT` | Read from an `envvar` |
| `DEFAULT_MAP` | Supplied by `Context.default_map` |
| `DEFAULT` | The parameter's own default |

Because it is an ordered `IntEnum`, `source < ParameterSource.DEFAULT_MAP` is the idiomatic test for
"the user explicitly provided this" — a real API contract, per the class docstring.

## `Option` vs `Argument`
- **`Option`** ([`core.py:2805`](../../../src/click/core.py)) — named (`--flag`), may be a boolean flag,
  multiple, prompted, or an eager option (e.g. `--help`) that short-circuits processing.
- **`Argument`** ([`core.py:3545`](../../../src/click/core.py)) — positional; simpler, no prompting,
  order-sensitive. `nargs=-1` consumes all remaining positionals.

## Invariants
- A value reaches the callback **only** after passing `ParamType.convert()`; there is no bypass.
- Conversion failure never crashes — it becomes a `UsageError` rendered as a usage message.

## Related
- [Parameter type system](parameter-types.md) · [Command & group model](command-and-group-model.md) ·
  [Invocation lifecycle](../architecture/diagrams/invocation-lifecycle.md)

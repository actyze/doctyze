---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/click/types.py]
  last_verified: 2026-07-05
---
# Spec — Parameter type system

## Summary

A `ParamType` ([`types.py:42`](../../../src/click/types.py)) is the single unit that turns a raw string
(or default) into a validated Python value. Every built-in type subclasses it and implements
`convert()`; on bad input it calls `fail()`, which raises a `UsageError` rather than a traceback.

## Contract

```python
class ParamType(abc.ABC):
    def convert(self, value, param, ctx) -> T: ...   # coerce + validate; may call self.fail(...)
    def fail(self, message, param=None, ctx=None):    # raise BadParameter/UsageError
    def get_metavar(self, param): ...                 # how the type shows in help (e.g. INTEGER, [a|b])
```

- `convert()` receives the raw value plus the owning `param` and `ctx`, so a type can produce
  context-aware error messages.
- Types are usually **stateless singletons** (e.g. `BOOL`, `STRING`), but parameterized types
  (`Choice([...])`, `IntRange(0, 10)`, `Path(exists=True)`) are instances carrying their config.

## Built-in types (grounded in `types.py`)

| Type | Where | Converts / validates |
|---|---|---|
| `StringParamType` (`STRING`) | [`:246`](../../../src/click/types.py) | Passthrough string (with decoding). |
| `Choice` | [`:284`](../../../src/click/types.py) | Membership in a fixed set; renders as `[a\|b\|c]`; optional case-insensitivity. |
| `IntParamType` / `IntRange` | [`:678`](../../../src/click/types.py) / [`:686`](../../../src/click/types.py) | Integer; range-bounded with optional clamping. |
| `FloatParamType` / `FloatRange` | [`:710`](../../../src/click/types.py) / [`:718`](../../../src/click/types.py) | Float; range-bounded. |
| `BoolParamType` (`BOOL`) | [`:761`](../../../src/click/types.py) | Truthy/falsey strings → `bool`. |
| `UUIDParameterType` | [`:830`](../../../src/click/types.py) | Parse to `uuid.UUID`. |
| `DateTime` | [`:464`](../../../src/click/types.py) | Parse against a list of formats → `datetime`. |
| `File` | [`:857`](../../../src/click/types.py) | Open a file handle (lazy/atomic modes); managed by the `Context`. |
| `Path` | [`:1001`](../../../src/click/types.py) | Filesystem path with `exists` / `file_okay` / `dir_okay` / `writable` checks. |
| `Tuple` | [`:1196`](../../../src/click/types.py) | A `CompositeParamType` — converts each position with its own sub-type. |

## Notable behaviors
- **Range clamping** — `IntRange`/`FloatRange` (`_NumberRangeBase`, [`:574`](../../../src/click/types.py))
  can either fail or *clamp* out-of-range values, depending on `clamp`.
- **`File` lifecycle** — opened file handles are registered with the `Context` and closed when it tears
  down, so callbacks don't leak descriptors.
- **Composite conversion** — `Tuple` converts element-wise, enabling `nargs`-style typed tuples
  (e.g. `--point FLOAT FLOAT`).

## Extension
Any callable `str -> value` is accepted as a type (wrapped by `FuncParamType`,
[`:206`](../../../src/click/types.py)); subclass `ParamType` when you need custom `get_metavar`,
help text, or shell-completion behavior.

## Related
- [Parameter processing](parameter-processing.md) · [Architecture overview](../architecture/overview.md)

---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [src/click/core.py, src/click/decorators.py]
  last_verified: 2026-07-05
---
# Spec — Command & group model

## Summary

Click represents a CLI as a tree of `Command` objects. A leaf `Command` wraps one callback; a `Group`
is a `Command` that dispatches to child commands. The tree is built declaratively with `@command` /
`@group` and traversed at runtime by resolving successive `argv` tokens to subcommands.

## Definitions (grounded in code)

| Concept | Where | Meaning |
|---|---|---|
| `Command` | [`core.py:956`](../../../src/click/core.py) | An invocable unit: name, `params`, a `callback`, and the `make_context → parse_args → invoke` lifecycle. |
| `Group` | [`core.py:1601`](../../../src/click/core.py) | A `Command` holding a registry of subcommands; overrides `invoke()` to dispatch. |
| `CommandCollection` | [`core.py:2071`](../../../src/click/core.py) | A `Group` that presents the union of several source groups' commands. |
| `@command` / `@group` | [`decorators.py:138`](../../../src/click/decorators.py) / [`:263`](../../../src/click/decorators.py) | Build a `Command`/`Group` from a function, pulling in `Parameter`s attached by `@option`/`@argument`. |

## Behavior

### Building the tree
- `@command` reads the parameters that `@option`/`@argument` stashed on the function (via the private
  `_param_memo`, [`decorators.py:314`](../../../src/click/decorators.py)) and constructs a `Command`
  whose `params` list is those parameters in declaration order.
- `@group` does the same but returns a `Group`. `group.add_command(cmd)`
  ([`core.py:1733`](../../../src/click/core.py)) — or the `@group.command()` sugar — registers children.

### Resolving a subcommand
On invocation a `Group`:
1. runs its own callback first **iff** `invoke_without_command=True`;
2. calls `resolve_command()` ([`core.py:2018`](../../../src/click/core.py)) to map the next token to a
   child via `get_command()` / `list_commands()`;
3. builds a **child `Context`** whose `parent` is the group's context, and recurses.

An unknown token raises `NoSuchCommand` ([`exceptions.py`](../../../src/click/exceptions.py)).

### Multi-command (chaining)
With `chain=True`, `resolve_command()` is applied repeatedly to the remaining tokens so one command line
may invoke several subcommands in order. `result_callback` then receives the **list** of their return
values. `_check_nested_chain` ([`core.py:78`](../../../src/click/core.py)) forbids nesting a group under
a chained group (an ambiguous grammar), so this is validated, not silently mis-parsed.

## Invariants
- A `Group` is-a `Command`, so groups nest to arbitrary depth with uniform lifecycle handling.
- Subcommand resolution is data-driven (`get_command`/`list_commands`), so `Group` subclasses can serve
  commands from anywhere (a plugin dir, an entry-point registry) by overriding those two methods.

## Edge cases
- Empty invocation of a group: `no_args_is_help` (defaults to the opposite of `invoke_without_command`)
  decides between showing help vs. running the callback.
- `CommandCollection` name collisions resolve in source order (first source wins).

## Related
- [Parameter processing](parameter-processing.md) · [Architecture overview](../architecture/overview.md) ·
  [ADR-0001: Context threads invocation state](../architecture/decisions/0001-context-threads-invocation-state.md)

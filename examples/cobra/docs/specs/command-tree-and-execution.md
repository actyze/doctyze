---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [command.go, args.go, cobra.go]
  last_verified: 2026-07-05
---
# Spec — Command tree & execution

## Summary

Cobra represents a CLI as a tree of `Command` structs linked by `parent`/`commands`. A single call to
`Execute()` re-roots at the tree root, resolves `os.Args` to a target command, parses its flags,
validates its positional arguments, and runs an ordered chain of hooks culminating in the target's
`Run`/`RunE`. There is no distinct "group" type — a command is a group precisely when it has children.

## Definitions (grounded in code)

| Concept | Where | Meaning |
|---|---|---|
| `Command` | `command.go:54` | A node: config (`Use`, `Args`, `*Run` hooks, …) plus private tree/flag state. |
| `AddCommand` | `command.go:1342` | Register children: sets `child.parent`, appends to `commands`, updates help padding, panics if a command is added to itself. |
| `Execute` / `ExecuteC` | `command.go:1070` / `:1084` | Entry points. `Execute` returns only the error; `ExecuteC` also returns the resolved `*Command`. |
| `execute` | `command.go:905` | The per-command runner: parse flags, validate args, run the hook chain. |
| `Find` | `command.go:757` | Default resolver: strip flags, descend by matching non-flag tokens to children. |
| `Traverse` | `command.go:821` | Resolver used when `TraverseChildren=true`: parses each ancestor's flags while descending. |
| `Runnable` | `command.go:1596` | `Run != nil || RunE != nil`. |

## Behavior

### Building the tree
`parent.AddCommand(child)` (`command.go:1342`) is the only wiring step. Children are stored unsorted and
sorted lazily by `Commands()` (`command.go:1332`) when `EnableCommandSorting` is true (the default).
`Name()` (`command.go:1541`) is the **first word of `Use`**, so `Use: "migrate [flags]"` yields the name
`migrate`; `CommandPath()` (`command.go:1465`) joins names from the root for help and error text.

### Resolving the target
`ExecuteC` first calls `c.Root().ExecuteC()` (`command.go:1090`) so execution always starts at the root,
then chooses a resolver:

1. **`Find`** (default) — `stripFlags` removes flags/values, then `findNext` (`command.go:798`) matches
   the leading non-flag token against each child's `Name()` or alias (`HasAlias`, `command.go:1551`),
   honoring `EnableCaseInsensitive` and, if `EnablePrefixMatching` is on, unambiguous prefixes. It
   recurses until no child matches, returning the deepest command plus the leftover args.
2. **`Traverse`** — when `TraverseChildren=true`, flags encountered before the subcommand token are
   accumulated and `ParseFlags` is run on each ancestor before recursing (`command.go:854`), so a
   parent's *local* flag may appear after the subcommand name.

An unresolved token on a root that *has* subcommands surfaces via `legacyArgs` (`args.go:28`) as
`unknown command "X" for "app"` with a Levenshtein-based "Did you mean this?" suggestion
(`findSuggestions`, `command.go:781`; distance via `ld`, `cobra.go:192`).

### The hook chain (order in `execute`)
Once the target is found, `execute` runs, in this exact order (`command.go:959`–`1042`):

1. `preRun()` → package-global `OnInitialize` funcs (`cobra.go:99`); `defer postRun()` → `OnFinalize`.
2. `ValidateArgs(argWoFlags)` — the `Args` positional validator.
3. **`PersistentPreRun(E)`** — walk from the target up to the root; by default run **only the first**
   ancestor that defines one (`command.go:984`). If `EnableTraverseRunHooks` (`cobra.go:66`) is set, run
   the whole chain root→leaf instead.
4. **`PreRun(E)`** — the target command only.
5. `ValidateRequiredFlags()` (`command.go:1180`) and `ValidateFlagGroups()`.
6. **`Run`/`RunE`** — the actual work. `RunE`'s error propagates out of `Execute`.
7. **`PostRun(E)`** — the target command only.
8. **`PersistentPostRun(E)`** — walk up to the root, first-found unless `EnableTraverseRunHooks`.

The `E` variant is preferred when present; e.g. if both `RunE` and `Run` are set, `RunE` is called
(`command.go:1014`). Because the hooks live *after* the `Runnable()`/help gate, they only fire for
commands that declare a `Run`/`RunE`.

## Invariants

- `Execute()` is idempotent about *where* it is called: it always re-roots to `Root()` first.
- A non-`Runnable` command with subcommands returns `flag.ErrHelp` and renders help rather than erroring.
- Persistent hooks are **inherited but shadowed**: the nearest-defined `PersistentPreRun` wins by
  default; ancestors' versions do not also run unless `EnableTraverseRunHooks` is enabled. See
  [ADR-0001](../architecture/decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md).
- Adding a command to itself panics (`command.go:1344`); adding a subcommand with an undeclared
  `GroupID` panics at execution via `checkCommandGroups` (`command.go:1205`).

## Edge cases

- **`DisableFlagParsing`** — skips `ParseFlags`, and the raw args (not `Flags().Args()`) are passed to
  the validator and `Run` (`command.go:964`).
- **Auto-injected commands/flags** — `execute`/`ExecuteC` lazily add a `help` command
  (`InitDefaultHelpCmd`, `command.go:1263`), `-h/--help` (`InitDefaultHelpFlag`, `command.go:1219`), a
  `completion` command, and — when `Version != ""` — a `-v/--version` flag (`InitDefaultVersionFlag`,
  `command.go:1238`), each only if the author has not already defined one.
- **Deprecated commands** — running a command whose `Deprecated` string is set prints that notice first
  (`command.go:910`).

## Related

- [Args & flags](args-and-flags.md) · [Shell completion](shell-completion.md) ·
  [Architecture overview](../architecture/overview.md) ·
  [Invocation lifecycle](../architecture/diagrams/invocation-lifecycle.md) ·
  [ADR-0001](../architecture/decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md)

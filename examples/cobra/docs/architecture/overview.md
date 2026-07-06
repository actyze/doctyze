---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [command.go, args.go, cobra.go, completions.go, flag_groups.go]
  last_verified: 2026-07-05
---
# Architecture overview — Cobra

Cobra is a Go library for building modern, git-style CLIs (`kubectl get pods`, `gh pr list`). A CLI
author builds a **tree of one struct** — `Command` — wiring each node's `Use`, its flags, its `Args`
validator, and a `Run`/`RunE` callback. At runtime a single call to `Execute()` walks that tree to the
target command, parses flags with the `github.com/spf13/pflag` library, validates the positional
arguments, runs an inherited chain of pre/post hooks, and finally invokes the leaf's `Run`. The same
tree also powers shell completion and auto-generated help.

Unlike frameworks that use separate `Command` and `Group` classes, Cobra models everything with one
`Command` type: a command *is* a group exactly when it has children (`AddCommand`). Cobra's `Group`
struct (`command.go:45`) is unrelated — it is only a `{ID, Title}` label used to bucket subcommands in
help output.

## Files and responsibilities

Cobra keeps its runtime in a handful of root-level `.go` files. Higher-level concerns (completion,
flag groups) build on the `Command` core; the core has no knowledge of them beyond a few hook points.

| Area | File(s) | Responsibility |
|---|---|---|
| **Command core** | `command.go` | The `Command` struct, tree building (`AddCommand`), the entry points `Execute`/`ExecuteC`, target resolution (`Find`/`Traverse`), the flag accessors, and the per-command `execute` that runs the hook chain. |
| **Argument validation** | `args.go` | The `PositionalArgs` type and its built-in validators (`NoArgs`, `ExactArgs`, `MinimumNArgs`, `OnlyValidArgs`, `MatchAll`, …). |
| **Package config & helpers** | `cobra.go` | Global switches (`EnablePrefixMatching`, `EnableCommandSorting`, `EnableCaseInsensitive`, `EnableTraverseRunHooks`), `OnInitialize`/`OnFinalize`, the help/usage template funcs, and the Levenshtein `ld` used for "did you mean" suggestions. |
| **Flag groups** | `flag_groups.go` | `MarkFlagsRequiredTogether` / `MarkFlagsOneRequired` / `MarkFlagsMutuallyExclusive` and their `ValidateFlagGroups` enforcement. |
| **Completion engine** | `completions.go` | The hidden `__complete` command, `getCompletions`, `ShellCompDirective`, `CompletionFunc`, and the user-facing `completion` command that emits shell scripts. |
| **Completion annotations** | `shell_completions.go`, `active_help.go` | `MarkFlagRequired` / `MarkFlagFilename` / `MarkFlagDirname` (pflag annotations consumed by completion) and the ActiveHelp mechanism. |

Flags themselves are **not** implemented in Cobra: `Command` embeds `*pflag.FlagSet` values from
`github.com/spf13/pflag` (aliased `flag` throughout `command.go`), which provides POSIX/GNU-style
parsing (`--flag`, `-f`, `-abc`, `--flag=value`).

## The core objects

- **`Command`** (`command.go:54`) — the one and only node type. Public config fields (`Use`, `Aliases`,
  `Short`/`Long`, `Args`, `ValidArgs`, the `*Run` hooks, `Version`, `TraverseChildren`,
  `DisableFlagParsing`, …) sit next to private tree/flag state (`parent *Command`, `commands []*Command`,
  and the five `*flag.FlagSet` caches `flags`/`pflags`/`lflags`/`iflags`/`parentsPflags`).
- **`PositionalArgs`** (`args.go:22`) — `func(cmd *Command, args []string) error`. A command's `Args`
  field is one of these; `ValidateArgs` (`command.go:1172`) calls it, defaulting to `ArbitraryArgs`.
- **`Group`** (`command.go:45`) — `{ID, Title}`. A *help-display* grouping registered with `AddGroup`,
  not a container of commands. `checkCommandGroups` (`command.go:1205`) panics if a subcommand names a
  `GroupID` its parent never declared.
- **`CompletionFunc`** (`completions.go:139`) — `func(cmd, args, toComplete) ([]Completion, ShellCompDirective)`.
  A command's `ValidArgsFunction` (`command.go:90`), or a per-flag function registered via
  `RegisterFlagCompletionFunc`, supplies dynamic completions.

## Runtime flow (one invocation)

```text
Execute()                         # command.go:1070 — thin wrapper over ExecuteC
  └─ ExecuteC()                   # command.go:1084
       ├─ c.Root().ExecuteC()     # always re-roots: execution starts at the tree root
       ├─ InitDefaultHelpCmd / initCompleteCmd / InitDefaultCompletionCmd
       ├─ Find(args) | Traverse(args)   # walk the tree to the target command + leftover args
       └─ cmd.execute(flags)      # command.go:905 — run the target
            ├─ InitDefaultHelpFlag / InitDefaultVersionFlag
            ├─ ParseFlags(a)      # pflag parses the merged flag set
            ├─ (help? version? not Runnable?) → flag.ErrHelp
            ├─ ValidateArgs(argWoFlags)          # the Args validator
            ├─ PersistentPreRun chain (inherited from ancestors)
            ├─ PreRun (this command only)
            ├─ ValidateRequiredFlags / ValidateFlagGroups
            ├─ Run / RunE                         # the actual work
            ├─ PostRun (this command only)
            └─ PersistentPostRun chain (inherited from ancestors)
```

`ExecuteC` always restarts at `c.Root()` (`command.go:1090`), so `Execute()` works no matter which node
it is called on. Errors flow back up: a `flag.ErrHelp` sentinel triggers the help renderer; any other
error is printed with a `Run '<path> --help' for usage.` hint unless `SilenceErrors`/`SilenceUsage` are
set.

## Two inheritance mechanisms (the heart of Cobra)

Both flags and hooks flow **down** the tree, but with different rules — see
[ADR-0001](decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md):

- **Persistent flags inherit and accumulate.** `mergePersistentFlags` (`command.go:1898`) folds a
  command's own `PersistentFlags()` plus every ancestor's persistent flags (`parentsPflags`) into the
  flag set actually parsed, so `--verbose` declared on the root is usable on any descendant.
- **Persistent hooks inherit but only the nearest fires.** `execute` walks from the target up to the
  root and, by default, runs **only the first** `PersistentPreRun(E)` it finds (`command.go:984`); a
  child that defines its own shadows its parents' — unless the global `EnableTraverseRunHooks`
  (`cobra.go:66`) is set, which runs the whole chain root-to-leaf.

## Diagrams

- [Object model](diagrams/object-model.md) — the `Command` tree and its collaborators (`pflag.FlagSet`, `PositionalArgs`, `CompletionFunc`).
- [Invocation lifecycle](diagrams/invocation-lifecycle.md) — `Execute` → `Find` → `execute` → the hook chain, as a sequence.

## Key specifications

- [Command tree & execution](../specs/command-tree-and-execution.md)
- [Args & flags](../specs/args-and-flags.md)
- [Shell completion](../specs/shell-completion.md)

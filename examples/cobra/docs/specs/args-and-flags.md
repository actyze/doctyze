---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [args.go, command.go, flag_groups.go]
  last_verified: 2026-07-05
---
# Spec — Args & flags

## Summary

Cobra separates a command's **positional arguments** from its **flags**. Positional arguments are
validated by a single `PositionalArgs` function stored in the command's `Args` field (`args.go`). Flags
are not implemented by Cobra at all — each `Command` owns `*pflag.FlagSet` values from
`github.com/spf13/pflag` (aliased `flag` throughout the code), which does the POSIX/GNU-style parsing.
Cobra layers two things on top of pflag: **persistent flags** that inherit down the command tree, and
**flag groups** (`flag_groups.go`) that add required-together / one-required / mutually-exclusive
constraints.

## Positional argument validators (`args.go`)

A validator has the type `PositionalArgs = func(cmd *Command, args []string) error` (`args.go:22`). It
receives the positional tokens *after* flag parsing and returns an error to reject the invocation.
`ValidateArgs` (`command.go:1172`) calls the command's `Args` field, defaulting to `ArbitraryArgs` when
`Args == nil`. The built-in validators:

| Validator | Where | Rejects when |
|---|---|---|
| `NoArgs` | `args.go:42` | any positional arg is present (`unknown command "X" for "path"`). |
| `ArbitraryArgs` | `args.go:82` | never — accepts anything. |
| `OnlyValidArgs` | `args.go:51` | an arg is not listed in the command's `ValidArgs` (tab descriptions stripped first). |
| `MinimumNArgs(n)` | `args.go:87` | `len(args) < n`. |
| `MaximumNArgs(n)` | `args.go:97` | `len(args) > n`. |
| `ExactArgs(n)` | `args.go:107` | `len(args) != n`. |
| `RangeArgs(min, max)` | `args.go:117` | `len(args) < min || len(args) > max`. |
| `NoDuplicateArgs` | `args.go:69` | the same arg value appears twice. |
| `MatchAll(pargs...)` | `args.go:127` | any of the composed validators returns an error. |

`MatchAll` is the composition primitive: it runs each supplied validator in order and returns the first
error. The deprecated `ExactValidArgs(n)` (`args.go:142`) is now literally
`MatchAll(ExactArgs(n), OnlyValidArgs)`. When a validator is not set on a command that has subcommands,
`Find` falls back to `legacyArgs` (`args.go:28`): a root command with subcommands rejects unknown
leading tokens with a "did you mean" suggestion, while leaf/child commands accept arbitrary args.

## Flags: local vs. persistent (via pflag)

Each `Command` lazily builds several `*pflag.FlagSet` values (`command.go:54` struct fields
`flags`, `pflags`, `lflags`, `iflags`, `parentsPflags`):

- **`Flags()`** (`command.go:1688`) — the *merged* set that is actually parsed: this command's local +
  persistent flags plus every ancestor's persistent flags.
- **`PersistentFlags()`** (`command.go:1775`) — flags declared on this command that should be visible to
  it *and all descendants*.
- **`LocalFlags()`** (`command.go:1716`) — flags specific to this command (not inherited).
- **`InheritedFlags()`** (`command.go:1744`) — flags contributed by ancestor commands.

The inheritance is assembled by `mergePersistentFlags` (`command.go:1898`), which calls
`updateParentsPflags` (`command.go:1907`) to walk `VisitParents` and fold each ancestor's
`PersistentFlags()` into `parentsPflags`, then adds both the command's own persistent flags and the
inherited ones into `Flags()`. This is why a `--verbose` persistent flag declared on the root command is
parseable on any subcommand. `ParseFlags` (`command.go:1868`) performs this merge and then calls
`c.Flags().Parse(args)` — the pflag parser. See
[ADR-0001](../architecture/decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md).

### POSIX/GNU parsing (pflag)

pflag provides the actual token grammar: long flags (`--flag`, `--flag=value`), short flags (`-f`),
combined shorthands (`-abc`), and `--` to terminate flag parsing. Cobra's own `stripFlags` /
`argsMinusFirstX` / `Traverse` helpers (`command.go`) mirror this grammar when they need to tell a flag
from a subcommand token during tree resolution — e.g. `hasNoOptDefVal` (`command.go:654`) consults a
flag's pflag `NoOptDefVal` to decide whether the following token is the flag's value or the next arg.
`ArgsLenAtDash()` (`command.go:901`) exposes pflag's record of where `--` appeared. Flag-parse errors
are routed through `FlagErrorFunc`, and `FParseErrWhitelist` (`command.go:42`, a
`flag.ParseErrorsAllowlist`) can whitelist unknown-flag errors.

## Required flags and flag groups (`flag_groups.go`)

- **Required flags.** `MarkFlagRequired` (`shell_completions.go:24`) sets the pflag annotation
  `BashCompOneRequiredFlag`; `ValidateRequiredFlags` (`command.go:1180`) later errors if any so-annotated
  flag was not `Changed`.
- **Required together.** `MarkFlagsRequiredTogether` (`flag_groups.go:33`) annotates a set with
  `requiredAsGroupAnnotation`; `validateRequiredFlagGroups` (`flag_groups.go:144`) errors unless the set
  is *all set or all unset*.
- **One required.** `MarkFlagsOneRequired` (`flag_groups.go:49`) annotates with `oneRequiredAnnotation`;
  `validateOneRequiredFlagGroups` (`flag_groups.go:167`) errors unless at least one is set.
- **Mutually exclusive.** `MarkFlagsMutuallyExclusive` (`flag_groups.go:65`) annotates with
  `mutuallyExclusiveAnnotation`; `validateExclusiveFlagGroups` (`flag_groups.go:188`) errors if more than
  one is set.

All three are checked by `ValidateFlagGroups` (`flag_groups.go:81`), which is a no-op when
`DisableFlagParsing` is true. It works by having pflag `VisitAll` every flag through
`processFlagForGroupAnnotation` (`flag_groups.go:121`) to build a per-group "which members are set" map,
then applying the three rules. A parallel `enforceFlagGroupsForCompletion` (`flag_groups.go:225`) reuses
the same annotations at completion time to auto-suggest the rest of a required group and hide the
alternatives of a mutually-exclusive one.

## Order of validation (in `execute`)

`ValidateArgs` runs **before** the pre-run hooks, whereas `ValidateRequiredFlags` and
`ValidateFlagGroups` run **after** the pre-run hooks but before `Run`/`RunE` (`command.go:1007`–`1012`).
The practical consequence: a `PersistentPreRun` may legitimately set a required flag programmatically and
still pass validation.

## Invariants

- A command's `Args` validator sees the tokens *after* flag removal, unless `DisableFlagParsing` is set,
  in which case the raw args are passed through untouched (`command.go:964`).
- Persistent flags are inherited but a child may **shadow** an ancestor's flag of the same name; the
  local flag wins in `LocalFlags()` (`command.go:1733`).
- Flag-group validation is skipped entirely under `DisableFlagParsing` (`flag_groups.go:82`).

## Related

- [Command tree & execution](command-tree-and-execution.md) · [Shell completion](shell-completion.md) ·
  [Architecture overview](../architecture/overview.md) ·
  [ADR-0001: persistent flags & hooks inherit down the tree](../architecture/decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md)

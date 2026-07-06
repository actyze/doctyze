---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [completions.go, shell_completions.go, active_help.go, command.go, bash_completions.go, zsh_completions.go, fish_completions.go, powershell_completions.go]
  last_verified: 2026-07-05
---
# Spec — Shell completion

## Summary

Cobra completes commands, flags, and arguments the same way for every shell: a small shell script (bash,
zsh, fish, or powershell) calls back into the compiled program itself via a hidden `__complete` command,
which returns a list of candidates plus a `ShellCompDirective` bitmask telling the shell what to do next.
The heavy lifting is in Go — `getCompletions` (`completions.go:316`) — so completion logic lives with the
command definitions instead of being duplicated per shell.

## The completion request cycle

1. The shell script the program emits calls `<program> __complete <args> <toComplete>`.
   `ShellCompRequestCmd = "__complete"` and its no-description alias
   `ShellCompNoDescRequestCmd = "__completeNoDesc"` (`completions.go:31`, `:34`).
2. `initCompleteCmd` (`completions.go:231`) registers that hidden command during `ExecuteC`. Its `Run`
   calls `cmd.getCompletions(args)`, prints each completion on its own line, and prints the directive as
   a trailing `:<directive>` line for the script to parse (`completions.go:289`). The command is removed
   again unless it is actually the one being invoked, to avoid giving a single-command program a stray
   subcommand (`completions.go:298`).
3. `getCompletions` (`completions.go:316`) resolves the real target command (via `Find` or, when
   `TraverseChildren` is set, `Traverse`), parses the already-typed flags, then decides what is being
   completed and produces `([]Completion, ShellCompDirective)`.

The last argument is the partially-typed word (`toComplete`) and is deliberately split off before
resolution (`completions.go:319`).

## What gets completed (decision order in `getCompletions`)

- **Flag values** — `checkIfFlagCompletion` (`completions.go:657`) detects that the cursor follows a
  flag expecting a value. If the flag carries a filename/dir annotation (`BashCompFilenameExt` →
  `ShellCompDirectiveFilterFileExt`, `BashCompSubdirsInDir` → `ShellCompDirectiveFilterDirs`) those are
  returned directly; otherwise the flag's registered completion function is used.
- **Flag names** — when `toComplete` begins with `-`, `getFlagNameCompletions` (`completions.go:599`)
  suggests matching `--long`/`-s` flags, first surfacing required flags via `completeRequireFlags`
  (`completions.go:632`), and returning `ShellCompDirectiveNoFileComp`.
- **Subcommand names** — when no arg has been consumed yet, available child commands (and the `help`
  command) whose name prefixes `toComplete` are suggested with their `Short` as the description
  (`completions.go:520`).
- **Static `ValidArgs`** — if the command declares `ValidArgs` (`[]Completion`), matching entries are
  returned for the first positional, plus `ArgAliases` as a fallback (`completions.go:535`).
- **Dynamic `ValidArgsFunction`** — otherwise the command's `ValidArgsFunction` (`command.go:90`) is
  invoked. `getCompletions` picks `completionFn = finalCmd.ValidArgsFunction` (`completions.go:574`) and
  appends whatever it returns. Only one of `ValidArgs` or `ValidArgsFunction` may be used per command.

## `ValidArgsFunction` / `CompletionFunc`

```
CompletionFunc = func(cmd *Command, args []string, toComplete string) ([]Completion, ShellCompDirective)
```

(`completions.go:139`). `Completion` is a `string` type alias (`completions.go:136`); a completion may
carry a description after a TAB, produced by `CompletionWithDesc` (`completions.go:142`). Both a
command's `ValidArgsFunction` and any per-flag function registered with
`RegisterFlagCompletionFunc` (`completions.go:170`) have this type. Cobra ships reusable implementations:
`NoFileCompletions` (`completions.go:151`, disables file completion) and `FixedCompletions`
(`completions.go:160`, always returns the same set).

## `ShellCompDirective` (the bitmask)

`ShellCompDirective` is an `int` bitmask (`completions.go:45`) returned alongside the candidates:

| Directive | Value | Meaning |
|---|---|---|
| `ShellCompDirectiveError` | `1 << iota` (`:58`) | an error occurred; ignore completions. |
| `ShellCompDirectiveNoSpace` | `:62` | do not add a space after a single completion. |
| `ShellCompDirectiveNoFileComp` | `:66` | do not fall back to file completion. |
| `ShellCompDirectiveFilterFileExt` | `:73` | treat the completions as file-extension filters. |
| `ShellCompDirectiveFilterDirs` | `:80` | complete directory names only. |
| `ShellCompDirectiveKeepOrder` | `:84` | preserve the returned order (don't sort). |
| `ShellCompDirectiveDefault` | `0` (`:95`) | let the shell do its default (file) completion. |

Because it is a bitmask, directives combine with `|`. The internal `string()` method
(`completions.go:200`) decodes a value for the human-readable line printed to stderr, and
`shellCompDirectiveMaxValue` bounds valid values.

## ActiveHelp

`AppendActiveHelp` (`active_help.go:38`) lets a `CompletionFunc` inject informational lines (prefixed
with the internal `activeHelpMarker`) into the completion stream. `GetActiveHelpConfig`
(`active_help.go:47`) reads the per-program `<PROGRAM>_ACTIVE_HELP` env var (and the global
`COBRA_ACTIVE_HELP=0` kill switch); `getCompletions`' caller strips ActiveHelp lines when it is disabled
(`completions.go:257`).

## Per-shell script generators

The `__complete` protocol is identical across shells; only the wrapper script differs. Each generator
lives in its own file and emits the shell function that shells out to `__complete`:

| Shell | Generator | File |
|---|---|---|
| bash | `GenBashCompletionV2` (`bash_completionsV2.go:482`), legacy `GenBashCompletion` (`bash_completions.go:683`) | `bash_completionsV2.go`, `bash_completions.go` |
| zsh | `GenZshCompletion` (`zsh_completions.go:31`) | `zsh_completions.go` |
| fish | `GenFishCompletion` (`fish_completions.go:276`) | `fish_completions.go` |
| powershell | `GenPowerShellCompletion` (`powershell_completions.go:337`) | `powershell_completions.go` |

`InitDefaultCompletionCmd` (`completions.go:748`) wires a user-facing `completion` subcommand
(`compCmdName = "completion"`, `completions.go:100`) that prints these scripts; `CompletionOptions`
(`completions.go:107`) can disable it or the `--no-descriptions` flag.

## Invariants

- A single Go function per flag/command drives completion for **all** shells — there is no per-shell
  completion logic beyond the emitted wrapper script.
- `ValidArgs` and `ValidArgsFunction` are mutually exclusive for a command; if `ValidArgs` is set,
  `getCompletions` returns before ever calling `ValidArgsFunction` (`completions.go:558`).
- The directive is always emitted, even on error, so the shell can still behave sanely
  (`completions.go:289`).

## Related

- [Command tree & execution](command-tree-and-execution.md) · [Args & flags](args-and-flags.md) ·
  [Architecture overview](../architecture/overview.md) ·
  [Object model](../architecture/diagrams/object-model.md)

---
doctyze:
  artifact: architecture
  generated_by: write-architecture
  affects: [command.go, args.go, flag_groups.go]
  last_verified: 2026-07-05
---
# Invocation lifecycle

What happens between `os.Args` and the leaf command's `Run`, for a root with one subcommand
(`app db migrate --steps 3`). Grounded in `Execute` / `ExecuteC` / `Find` / `execute`
(`command.go`), the `Args` validator (`args.go`), and `ValidateFlagGroups` (`flag_groups.go`).

```mermaid
sequenceDiagram
    autonumber
    participant OS as os.Args
    participant R as Root (app)
    participant F as Find
    participant P as pflag.FlagSet
    participant S as Target (migrate)

    OS->>R: Execute() → ExecuteC()
    R->>R: c.Root().ExecuteC()  (re-root)
    R->>R: InitDefaultHelpCmd / initCompleteCmd / InitDefaultCompletionCmd
    R->>F: Find(["db","migrate","--steps","3"])
    Note over F: stripFlags → findNext walks<br/>app → db → migrate
    F-->>R: (migrate, leftover=["--steps","3"])
    R->>S: cmd.execute(["--steps","3"])
    S->>S: InitDefaultHelpFlag / InitDefaultVersionFlag
    S->>P: ParseFlags — merged local + inherited persistent flags
    P-->>S: steps=3; Flags().Args()=[]  (positionals)
    alt --help / --version / not Runnable
        S-->>R: return flag.ErrHelp → HelpFunc renders help
    end
    S->>S: ValidateArgs(argWoFlags)  → the Args validator (e.g. NoArgs)
    S->>S: PersistentPreRun chain (nearest ancestor that defines one)
    S->>S: PreRun (migrate only)
    S->>S: ValidateRequiredFlags + ValidateFlagGroups
    S->>S: Run / RunE  ← the actual work runs here
    S->>S: PostRun (migrate only)
    S->>S: PersistentPostRun chain
    S-->>R: err (nil on success)
    Note over R: on non-nil err, print error + "Run 'app migrate --help' for usage."<br/>unless SilenceErrors / SilenceUsage
```

Key facts:

- **Execution always re-roots.** `ExecuteC` calls `c.Root().ExecuteC()` (`command.go:1090`) before doing
  anything, so `rootCmd.Execute()` and `anySubCmd.Execute()` behave identically — resolution always
  begins at the tree root.
- **`Find` vs `Traverse`.** With `TraverseChildren=false` (the default) `Find` (`command.go:757`) strips
  flags, then descends by matching the first non-flag token to a child via `findNext` (`command.go:798`).
  With `TraverseChildren=true`, `Traverse` (`command.go:821`) instead parses each ancestor's flags *as it
  descends*, which is what lets a parent's local flag appear after a subcommand name.
- **The Run gate.** `execute` returns `flag.ErrHelp` early if `--help` is set, or if the command is not
  `Runnable()` (`command.go:955`). Because the `*PreRun`/`*PostRun` hooks live after that gate, they
  only fire for commands that actually declare a `Run`/`RunE` — a non-runnable "group" node shows help
  instead.
- **Two validation points.** Positional arguments are checked *before* the pre-run hooks
  (`ValidateArgs`), while required-flag and flag-group constraints are checked *after* the pre-run hooks
  but *before* `Run` (`ValidateRequiredFlags` / `ValidateFlagGroups`, `command.go:1007`) — so a
  `PersistentPreRun` can legitimately set a required flag's value programmatically.
- **Global init/finalize.** `execute` runs the package-level `OnInitialize` functions via `preRun`
  (`command.go:1047`) and defers the `OnFinalize` functions via `postRun`, independent of the
  per-command hooks.

See [ADR-0001](../decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md) for the hook
inheritance rules and the `EnableTraverseRunHooks` variant.

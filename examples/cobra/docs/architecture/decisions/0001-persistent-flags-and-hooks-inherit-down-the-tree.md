---
doctyze:
  artifact: adr
  generated_by: write-adr
  affects: [command.go, args.go, flag_groups.go]
  last_verified: 2026-07-05
---
# ADR-0001: Persistent flags and run hooks inherit down the command tree

**Status:** 🟢 ACCEPTED (reverse-engineered from the code — describes Cobra's existing design)
**Date:** 2026-07-05
**Deciders:** Cobra maintainers (inferred)

> Reverse-engineered by Doctyze from the code as a demonstration of the `write-adr` skill. It documents a
> decision Cobra already embodies (verified in `command.go`); it is **not** a proposal to change Cobra.

## Context

A Cobra CLI is a tree of one struct — `Command` (`command.go:54`) — linked by `parent`/`commands`
(`git`-style: `app db migrate`). Two kinds of state naturally belong to a *subtree* rather than a single
command:

1. **Cross-cutting flags** — `--verbose`, `--config`, `--context` should be accepted by every command
   under the root, not redeclared on each leaf.
2. **Cross-cutting behavior** — opening a config/DB connection, setting up logging, or auth should happen
   once for a whole family of subcommands.

The design question: how does a command expose a flag or a setup step to *all its descendants* without
each descendant re-declaring or re-invoking it, while still letting a specific subcommand override the
behavior when it needs to?

## Decision

Cobra makes both **flags** and **run hooks** inheritable down the tree, but with deliberately different
inheritance rules.

**Persistent flags accumulate.** A command's `PersistentFlags()` (`command.go:1775`) are merged into the
flag set that is actually parsed for every descendant. `mergePersistentFlags` (`command.go:1898`) →
`updateParentsPflags` (`command.go:1907`) walks `VisitParents` and folds every ancestor's persistent
flags into `parentsPflags`, which `Flags()` (`command.go:1688`) then includes. Result: a persistent flag
declared once on an ancestor is parseable on any descendant, and a child may *shadow* an ancestor's flag
of the same name via its local flags (`command.go:1733`).

**Persistent hooks inherit but only the nearest fires (by default).** The hook fields
`PersistentPreRun(E)` / `PersistentPostRun(E)` (`command.go:128`–`146`) are documented as "children of
this command will inherit and execute." In `execute` (`command.go:905`), the pre-run loop walks from the
target command up to the root and runs **only the first** `PersistentPreRun(E)` it finds, then `break`s
(`command.go:984`). The post-run loop does the same walking up (`command.go:1028`). The package-global
switch `EnableTraverseRunHooks` (`cobra.go:66`) changes this: when set, the pre-runs execute root→leaf
and the post-runs leaf→root — i.e. *every* level runs, not just the nearest.

The non-persistent `PreRun(E)`/`PostRun(E)` hooks, by contrast, are **not** inherited — they fire only
for the exact command being run.

## Rationale

1. **Declare-once ergonomics.** Cross-cutting flags and setup live on the ancestor that owns them; deep
   subcommands get them for free, mirroring how users mentally scope `--verbose` to a whole tool.
2. **Override without opt-out plumbing.** Because the default is "nearest hook wins," a subcommand can
   replace a parent's `PersistentPreRun` simply by defining its own — no flag to disable the parent, no
   super-call. The `EnableTraverseRunHooks` escape hatch exists for programs that instead want *every*
   ancestor's setup to run.
3. **One type, uniform rules.** Since a group is just a `Command` with children, the same inheritance
   machinery serves both "namespace" nodes and leaf commands; there is no separate group-lifecycle code
   path to keep in sync.

## Consequences

- **Positive:** minimal boilerplate for global flags/behavior; predictable override semantics; flag
  groups (`flag_groups.go`) and required-flag validation compose naturally because they operate on the
  already-merged `Flags()` set.
- **Tradeoff / footgun:** the default "only the nearest persistent hook runs" surprises authors who
  expect ancestor `PersistentPreRun`s to *also* fire. A child that defines `PersistentPreRunE` silently
  suppresses the parent's unless it calls it explicitly or the program sets `EnableTraverseRunHooks`.
- **Constraint:** `EnableTraverseRunHooks` is a *global* (package-level) toggle, so the "run all vs. run
  nearest" choice is made per-program, not per-command.
- **Ordering:** positional-arg validation (`ValidateArgs`) runs *before* the pre-run hooks, while
  required-flag / flag-group validation runs *after* them (`command.go:1007`), so a persistent pre-run
  may legitimately populate a required flag.

## Related

- [Architecture overview](../overview.md) ·
  [Command tree & execution](../../specs/command-tree-and-execution.md) ·
  [Args & flags](../../specs/args-and-flags.md) ·
  [Invocation lifecycle](../diagrams/invocation-lifecycle.md)

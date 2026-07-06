# Example — [spf13/cobra](https://github.com/spf13/cobra) (Go)

The **code-grounded structured docs Doctyze generated for Cobra**, reverse-engineered from its source at
commit [`ad460ea`](https://github.com/spf13/cobra/tree/ad460ea8f249db69c943a365fb84f3a59042d54e). See
[PROVENANCE.md](./PROVENANCE.md) for exact source/version and scope.

Each doc is anchored to the `.go` files it describes, so a code change flags it stale (demonstrated in
PROVENANCE).

## What's in `docs/`

| Doc | Grounded in |
|---|---|
| [architecture/overview.md](docs/architecture/overview.md) | The `Command` tree, execution (`Execute`/`ExecuteC`), flags via pflag, and shell completion |
| [architecture/diagrams/object-model.md](docs/architecture/diagrams/object-model.md) | `Command` / args / flags / completion relationships (Mermaid) |
| [architecture/diagrams/invocation-lifecycle.md](docs/architecture/diagrams/invocation-lifecycle.md) | `os.Args` → `ExecuteC` → `Find`/`Traverse` → flag parse → hook chain → `RunE` (Mermaid) |
| [specs/command-tree-and-execution.md](docs/specs/command-tree-and-execution.md) | `Command`, `AddCommand`, `Execute`/`ExecuteC`, `Find`/`Traverse`, the `PersistentPreRun`→`Run`→`PostRun` hook chain |
| [specs/args-and-flags.md](docs/specs/args-and-flags.md) | The `Args` validators (`ExactArgs`, `MinimumNArgs`, …); local vs persistent flags via pflag; flag groups |
| [specs/shell-completion.md](docs/specs/shell-completion.md) | The completion engine: `ValidArgsFunction`, `__complete`, `ShellCompDirective`, bash/zsh/fish/powershell generators |
| [architecture/decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md](docs/architecture/decisions/0001-persistent-flags-and-hooks-inherit-down-the-tree.md) | Why persistent flags & hooks inherit down the command tree |

> Source-file references are by filename at the
> [pinned commit](https://github.com/spf13/cobra/tree/ad460ea8f249db69c943a365fb84f3a59042d54e).

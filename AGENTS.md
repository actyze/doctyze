# Doctyze — Agent context

This file follows the [AGENTS.md / AAIF standard](https://agents.md). It tells AI
coding agents working on this repo what they need to know that they cannot infer
from the code alone.

## What this project is

Doctyze is an open-source documentation scaffolder for any codebase — modern
or legacy. It scans a repository, detects the stack, and generates a canonical
documentation layer (ADRs, runbooks, diagrams, specs, AGENTS.md, skills),
then keeps that documentation current via a PR review GitHub Action.

Published by [Actyze](https://github.com/actyze) under Apache 2.0.

## Hard constraints

- **License is Apache 2.0**, with an explicit patent grant. All contributions
  must be compatible.
- **AAIF standard alignment**: any agent-facing file (AGENTS.md, SKILL.md,
  policy files) must follow the conventions documented at agents.md and
  Claude Code skills documentation. Do not invent parallel formats.
- **No telemetry by default.** The tool runs locally; it does not phone home.
  The optional `extraction.retain_source_locally: true` setting must be the
  default in any new feature touching source code.
- **Air-gapped mode is first-class.** Any feature that requires network
  access must have an offline / Ollama / local-LLM equivalent OR an explicit
  `--online-required` flag with a clear error message.
- **Confidence markers are load-bearing.** Every artifact Doctyze generates
  must be stamped 🟢 CONFIRMED / 🟡 INFERRED / 🔴 GAP. Skipping this is a
  bug, not a style issue.

## Code conventions

- **Python 3.11+** for the CLI. Type hints required for public APIs.
- **`ruff` + `black`** for linting and formatting. Settings in `pyproject.toml`.
- **`pytest`** for tests. Coverage target: 80% on new code.
- **Click** for CLI command structure. No alternative argument parsers.
- **PyYAML** for YAML I/O. No alternatives without prior ADR.

## Canonical-source-of-truth model (load-bearing)

Doctyze treats `docs/skills/*.md` and `docs/runbooks/*.md` as the
**canonical source of truth**. Vendor-specific files
(`.claude/skills/`, `.cursor/rules/`, `.github/copilot-instructions.md`,
`.windsurfrules`, `.holmes/runbooks/`) are **generated** by renderers in
`cli/src/doctyze/renderers/`.

When contributing:

- **Never edit a generated vendor file directly.** Edit the canonical
  markdown in `docs/skills/` or `docs/runbooks/`, then run
  `doctyze render`.
- **Adding support for a new AI tool** means adding a renderer subclass
  in `cli/src/doctyze/renderers/<vendor>.py` and registering it in
  `renderers/__init__.py:REGISTRY`. Do not add another canonical format.
- **The PR review GitHub Action runs `doctyze render --check`** to fail
  PRs where generated files have drifted from canonical sources.

## Cleanup rule (load-bearing — read this before every PR)

**Whenever something is changed, the corresponding now-redundant logic,
files, and folders must be removed in the same PR.** Same PR — not "later,"
not "after a deprecation window."

See [`docs/skills/cleanup-redundancy.md`](docs/skills/cleanup-redundancy.md)
for the full rule. Mandatory checklist before opening a PR:

- [ ] `find . -type d -empty -not -path './.git/*'` returns nothing
- [ ] No commented-out code blocks introduced
- [ ] No dead parameters, kwargs, or struct fields nothing reads
- [ ] No duplicate canonical sources (always one source → renderers)
- [ ] All `import` statements in changed modules are used
- [ ] README diagrams, AGENTS.md sections, `.doctyze.yaml` examples
      reflect the post-change layout
- [ ] `grep -r '<deleted-symbol-name>' .` returns zero hits

The cleanup-redundancy skill is propagated into every Doctyze-scaffolded
repo (modern + legacy templates) so the rule applies everywhere downstream
too.

## Repo layout

```
cli/                                  Python CLI (`doctyze`)
templates/                            canonical structures emitted by `doctyze init`
  modern/                             Java/Python/Node/React/Go
  legacy/                             COBOL/ABAP/IBM i/VB6/.NET Fx/PB/Delphi
extractors/                           language-specific content extractors
  modern/{java-spring,python,node-react,go}/
  legacy/{cobol,abap,ibm-i-rpg,vb6,dotnet-framework,powerbuilder,delphi}/
pr-review-action/                     GitHub Action for PR doc-enforcement
skills-library/                       canonical SKILL.md files per stack
examples/                             end-to-end demo repos
docs/                                 Doctyze's own documentation (dog-fooding)
```

## Build commands

```bash
pip install -e cli/                   # editable install of the CLI
pytest                                # run the test suite
ruff check . && black --check .       # lint + format check
doctyze init --stack=python ./test    # smoke test on a throwaway dir
```

## Gotchas worth knowing

- **Path with space**: the dev path on this machine is
  `/Users/rohitmangal/Documents/Actyze Content/doctyze/` — always quote in shell
  commands.
- **Stack detection is fragile by design**: false positives are worse than asking.
  When in doubt, the CLI should prompt the user, not guess.
- **Legacy template differs structurally from modern** (e.g., `docs/data/` is
  first-class in legacy, absent in modern). Don't try to unify them.
- **MADR format for ADRs** is the convention. Don't invent variants.
- **The PR review Action posts `suggestion:` blocks, not commit-direct edits.**
  Never give the bot push access; suggestions only.
- **`policy.authority` rules are never auto-suggested.** They are a human
  decision, always. The bot must include `# doctyze: human-required` markers
  on any authority-adjacent suggestion.

## Where decisions live

- Architectural Decision Records: [`docs/architecture/decisions/`](docs/architecture/decisions/)
- Open RFCs / proposals: [GitHub Issues with label `rfc`](https://github.com/actyze/doctyze/issues?q=label%3Arfc)
- Roadmap: see [README.md](README.md#roadmap)

## Quick links

- [README.md](README.md) — what Doctyze does
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [LICENSE](LICENSE) — Apache 2.0
- [templates/modern/](templates/modern/) — modern stack template
- [templates/legacy/](templates/legacy/) — legacy stack template
- [pr-review-action/](pr-review-action/) — the GitHub Action

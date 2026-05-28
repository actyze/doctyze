# Contributing to Doctyze

Doctyze is an open-source documentation scaffolder for any codebase, built
by [Actyze](https://github.com/actyze). The highest-leverage contributions
right now, in priority order:

## 1. Language extractors

The biggest impact you can have is contributing a language-specific
extractor — especially for legacy stacks where existing OSS tooling is
thin. See [`extractors/`](extractors/) for the plugin SDK.

Wanted (in rough priority by market demand):

- **COBOL** (~250B lines in production, banking/government/healthcare)
- **SAP ABAP** (S/4HANA 2030 migration deadlines)
- **Java EE / WebSphere** (85% of Jakarta EE estate on 3+ year-old code)
- **IBM i RPG** (acute talent crisis)
- **VB6** (Windows 10 EOL + compliance pressure)
- **.NET Framework** (Microsoft EOL push)
- **PowerBuilder, Delphi** (niche but high willingness-to-pay)

## 2. Skills library

Each stack ships with starter `SKILL.md` files in
[`skills-library/`](skills-library/). PRs adding new patterns are very
welcome — especially ones that capture real institutional practices
(error-handling style, ADR triggers, runbook conventions).

## 3. PR review rules

The [`pr-review-action/`](pr-review-action/) enforces doc-coupling rules
on every PR. Adding new rule patterns (when to require doc updates, when
to suggest, when to block) directly improves the experience.

## 4. Examples

End-to-end demo repos in [`examples/`](examples/) — `doctyze init` run
on real or representative codebases. Especially wanted: COBOL, ABAP,
RPG, Delphi examples that show the legacy template in action.

## 5. Documentation and Adoption

- Adoption stories — open a PR against `ADOPTERS.md`
- Conference talk recordings, blog posts — add to `docs/talks/`
- Translations of the README

## Development setup

```bash
git clone https://github.com/actyze/doctyze
cd doctyze
pip install -e cli/                                 # editable install
export ANTHROPIC_API_KEY=...                        # for LLM-driven tests
pytest                                              # run the test suite
```

## Pull request conventions

- One concern per PR. Big PRs are slow to review and slow to merge.
- All PRs require: tests for new code · doc updates if behavior changes ·
  CHANGELOG entry · green CI.
- Doctyze eats its own dog food: the PR review GitHub Action runs on every
  PR to this repo. If you change behavior the docs describe, the bot will
  ask you to update the docs in the same PR.

## Code of Conduct

By participating in this project, you agree to abide by the
[Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## Governance

Doctyze is currently maintained by Actyze. The intent is to donate the
project to the [Linux Foundation Agentic AI Foundation (AAIF)](https://aaif.io)
once adoption reaches sustained traction. Until then, decisions are made by
the Actyze core team with input from contributors via GitHub Issues and
Discussions.

## License

By contributing, you agree that your contributions will be licensed under
the [Apache License 2.0](LICENSE).

# Doctyze Doc Guard Action

**A documentation-coupling guard for pull requests. Runs alongside your
existing PR review agent — it does not replace it.**

The Doc Guard's narrow job is to make sure the canonical documentation
layer (ADRs, runbooks, specs, skills, OpenAPI, AGENTS.md) stays in sync
with code changes. When a PR changes code, this action checks whether
the corresponding docs were updated in the same PR — and if not, it
suggests the updates inline.

> This action is intentionally minimal. CodeRabbit, Greptile, Qodo, Bito,
> Copilot Code Review and similar tools already cover code correctness,
> security, style, and patterns. Doctyze covers the one thing none of
> them treat as a first-class concern: **does the documentation match the
> code after this PR?**

## How it differs from a full PR review agent

| Concern | Doctyze Doc Guard | Your PR review agent |
|---|:---:|:---:|
| Documentation drift (ADRs, runbooks, specs, OpenAPI) | ✅ | ❌ usually no |
| Code correctness | ❌ | ✅ |
| Security vulnerabilities | ❌ | ✅ (most do) |
| Style / lint | ❌ | ✅ |
| Test presence | ⚠️ (presence only, not quality) | ✅ |
| Pattern conformance against `docs/skills/` | ✅ | ❌ (no concept of skills) |
| ADR archaeology / intent preservation | ✅ | ❌ |

**Run both.** They cover different ground and don't interfere with each other.

## What the Doc Guard actually checks

Three things, in this order:

1. **Documentation impact** — does the PR's code diff require an update
   to `docs/` that wasn't included?
   - New public endpoint added → `docs/api/openapi.yaml` updated?
   - New external dependency → ADR added under `docs/architecture/decisions/`?
   - New `try/except` or error class → corresponding runbook entry?
   - Existing ADR contradicted → does the PR write a superseding ADR?
2. **Pattern conformance** — does the PR follow the patterns documented
   in `docs/skills/`? (e.g., the `add-new-endpoint` skill requires
   OpenAPI updates; the `check-and-update-adrs` skill requires ADR
   review.)
3. **Test presence** — are unit + integration tests for the changed
   behavior present? (Presence check only — the *quality* of tests is
   your PR review agent's domain.)

## Running it alongside the popular PR review agents

The Doc Guard does not interfere with any other GitHub Action. Drop it in
your workflow file alongside whatever else you already run:

### With CodeRabbit

```yaml
# .github/workflows/code-review.yml — your existing CodeRabbit workflow
# (no changes needed — CodeRabbit runs as a GitHub App)

# .github/workflows/doctyze-doc-guard.yml — NEW
name: Doctyze Doc Guard
on:
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  contents: read
  pull-requests: write
jobs:
  doc-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actyze/doctyze-doc-guard-action@v1
        with:
          mode: warn-only
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
```

CodeRabbit posts its review comments. The Doc Guard posts its own,
clearly labeled. Engineers see both. No conflicts.

### With Greptile, Qodo, Bito, Copilot Code Review

Same pattern. None of these tools intercept or modify the Doc Guard's
comments. The Doc Guard's comments are explicitly labeled with
`[doctyze:doc-guard]` so they're filterable in the GitHub UI.

### With internal copilots

If you've built your own internal PR review agent (very common at large
orgs), the Doc Guard is complementary. Your internal agent handles
correctness; the Doc Guard handles documentation drift. Two workflows,
zero overlap.

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `mode` | `warn-only` | `warn-only` posts review comments. `block-required` fails the action if required doc updates are missing. `block-all` fails on any warning. |
| `llm` | `claude` | LLM backend for the analysis: `claude` / `openai` / `ollama`. |
| `anthropic-api-key` | — | For `llm: claude`. |
| `openai-api-key` | — | For `llm: openai`. |
| `config` | `.doctyze.yaml` | Path to `.doctyze.yaml`. |
| `stack-profile` | auto-detect | Override stack: `modern` or `legacy`. |
| `exclude-paths` | — | Comma-separated globs to skip. |

## Outputs

| Output | Meaning |
|---|---|
| `doc-warnings-count` | Number of doc-drift warnings posted on the PR. |
| `required-doc-updates` | Number of required doc updates that block merge (when `mode != warn-only`). |

## Rejection rules (when `mode: block-required`)

Configurable in `.doctyze.yaml`:

| Trigger | Action |
|---|---|
| Public API changed without `docs/api/openapi.yaml` update | **Block** + suggest the OpenAPI diff |
| New external dependency added without an accompanying ADR | **Block** + propose ADR stub |
| New `try/except` or error class without runbook entry | **Block** + suggest runbook stub |
| Existing accepted ADR contradicted without a superseding ADR | **Block** + identify the contradicted ADR |
| ADR file deleted | **Block** unconditionally (ADRs are append-only) |
| Pure refactor (whitespace, rename, no behavior change) | **Pass silently** |

## Configuration

In `.doctyze.yaml`:

```yaml
doc_guard:
  mode: warn-only
  exclude_paths:
    - "vendor/**"
    - "**/*.generated.*"
    - "test/**"
  rules:
    require_adr_for_new_dependency: true
    require_runbook_for_new_error: true
    require_openapi_for_api_change: true
    check_skill_conformance: true
    check_test_presence: true
    require_superseding_adr_on_contradiction: true
```

## Safety guardrails

- **Suggestions only.** The action posts review comments with
  `suggestion:` blocks. The engineer chooses to accept. It never commits
  directly.
- **No code generation.** This is not a coding agent. It does not write
  code; it only flags documentation gaps.
- **Least-privilege permissions.** Only `pull-requests: write`. Cannot
  read secrets or push to branches.

## License

[Apache 2.0](../LICENSE).

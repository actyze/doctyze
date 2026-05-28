# Doctyze PR Review Action

A GitHub Action that runs on every PR and determines whether documentation
needs updating. Posts review comments with suggested doc diffs; can block
merge depending on enforcement mode.

## What it does

On each PR open/sync:

1. **Reads the diff** — files changed, lines added/removed
2. **Cross-references with docs** — which ADRs / runbooks / specs /
   diagrams reference these files?
3. **Classifies impact** — pure refactor, behavior change, public API
   change, new failure mode, new dependency, architectural change, data
   model change
4. **Calls the configured LLM** with structured prompts
5. **Posts suggestions** as PR review comments:
   - **HIGH confidence**: posted as `suggestion:` blocks (one-click accept)
   - **MEDIUM confidence**: posted as plain review comments
   - **LOW confidence**: skipped (would be noise)
6. **Optionally blocks merge** when mode is `block-required` or `block-all`

## Rejection rules (default-strict)

| Trigger | Action |
|---|---|
| Public API changed without `docs/api/openapi.yaml` update | Block + suggest diff |
| New `try/except` or error class added without runbook entry | Block + suggest runbook stub |
| New external dependency added without ADR | Block + propose ADR stub |
| New `failure_mode` signal added without `.holmes/runbooks/*.yaml` entry | Block + suggest the YAML stub |
| Existing failure_mode signal removed → runbook may be stale | Warn + suggest cleanup |
| ADR file deleted | **Block unconditionally** — ADRs are append-only |
| `policy.authority` rule changed | Block + require reviewer from `@security-team` |
| Pure refactor (whitespace, rename, no behavior change) | Pass silently |

Configurable in `.doctyze.yaml`:

```yaml
pr_review:
  mode: block-required   # warn-only | block-required | block-all
  llm: claude
  exclude_paths:
    - "vendor/**"
    - "test/**"
  custom_rules:
    - "any change to src/payments/** requires PR linked to a JIRA ticket"
```

## Usage

In `.github/workflows/doctyze-review.yml`:

```yaml
name: Doctyze PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  doctyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actyze/doctyze-pr-review-action@v1
        with:
          mode: warn-only
          llm: claude
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Safety guardrails

The bot operates under three load-bearing constraints:

1. **Suggestions only — never direct commits.** The bot posts review
   comments with `suggestion:` blocks. The engineer chooses to accept.
2. **Never auto-grants policy.authority rules.** Authority decisions
   are human-required, always. The bot includes a `# doctyze: human-required`
   marker on any authority-adjacent suggestion.
3. **Least-privilege permissions.** Only `pull-requests: write` —
   the bot cannot read secrets or push to branches.

## License

[Apache 2.0](../LICENSE).

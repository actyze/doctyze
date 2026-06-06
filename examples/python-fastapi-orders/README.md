# orders-api — a Doctyze worked example

This is a **deliberately-small reference repo** showing what `doctyze init` is
designed to produce for a modern Python service. The code itself (a small
FastAPI orders service) is incidental — what matters is the documentation
layer around it.

## What you're looking at

A complete canonical-source documentation layer + a tiny FastAPI service:

```
python-fastapi-orders/
├── README.md                          ← you are here
├── AGENTS.md                          ← canonical universal context
├── .doctyze.yaml                      ← project config (agent_targets, etc.)
│
├── docs/                              ← canonical source of truth
│   ├── index.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── workspace.dsl              ← Structurizr C4
│   │   ├── decisions/
│   │   │   ├── 0001-record-architecture-decisions.md
│   │   │   ├── 0002-use-postgres-not-mongo.md
│   │   │   └── 0003-fail-open-pricing.md
│   │   └── diagrams/system-context.mmd
│   ├── runbooks/high-error-rate.md   ← canonical markdown + frontmatter
│   ├── skills/                        ← canonical agent skills
│   │   ├── write-adr.md
│   │   └── add-new-endpoint.md
│   ├── specs/
│   ├── investigations/
│   └── api/openapi.yaml
│
├── .github/workflows/                 ← drift-check + auto-render + PR review
│
├── src/orders/                        ← the actual service
└── tests/
```

## How it was generated

```bash
# In an empty repo:
doctyze init --stack=python
# ↓
# - detects Python stack
# - emits docs/ canonical structure
# - renders .claude/skills/, .cursor/rules/, .github/copilot-instructions.md,
#   .windsurfrules, .holmes/runbooks/ from the canonical sources
# - installs the .github/workflows/ for drift-check and PR review

# After that, ongoing edits flow like this:
vim docs/skills/write-adr.md           # edit canonical source
doctyze render                          # regenerate vendor files
git commit -am "improve write-adr skill"
git push
# → GitHub Action runs `doctyze render --check` and confirms no drift
```

## What's interesting about this example

- **Three real ADRs** showing the MADR format in practice: one meta-decision
  (use ADRs), one technology choice (Postgres over Mongo), one operational
  intent (fail-open pricing — the kind of intent an AI agent can't infer
  from telemetry alone).
- **A runbook with frontmatter** that drives the Holmes YAML generation:
  see `docs/runbooks/high-error-rate.md`.
- **Two canonical skills** — `write-adr` and `add-new-endpoint` — that
  define how engineers (human + AI) should make those kinds of changes.
- **The generated vendor files** under `.claude/`, `.cursor/`, `.github/`,
  `.holmes/` are committed alongside the canonical sources so the repo
  works out-of-the-box with any AI tool.

## Try it

```bash
# Run the service
pip install -r requirements.txt
uvicorn orders.main:app --reload

# Test:
curl -X POST http://localhost:8000/orders -d '{"sku":"S1","qty":2}'
```

## Try a Doctyze workflow

```bash
# Edit a canonical skill
echo "## New section" >> docs/skills/write-adr.md

# See drift
doctyze render --check
# → ✗ vendor files out of sync

# Fix
doctyze render
# → ✓ regenerated

# Commit canonical + regenerated together
git add docs/ .claude/ .cursor/ .github/copilot-instructions.md
git commit -m "improve write-adr skill"
```

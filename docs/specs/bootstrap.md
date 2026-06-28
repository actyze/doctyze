---
doctyze:
  artifact: spec
  generated_by: write-spec
  affects: [doctyze/generate/**]
  last_verified: '2026-06-15'
---

# Spec: Bootstrap

**Purpose.** Scaffold the canonical `docs/` structure from code and hand the existing agent a manifest of what to generate.

**CLI.** `doctyze bootstrap [PATH]` — deterministic only; the prose generation is the agent's job.

## Behavior

1. **Scaffold** ([`scaffold.py`](../../doctyze/generate/scaffold.py)) — create `docs/{specs,architecture,architecture/diagrams,architecture/decisions,runbooks,observability}` and an anchored `index.md` in each (idempotent; never overwrites).
2. **Detect stack** ([`stack.py`](../../doctyze/generate/stack.py)) — from file signatures (`pom.xml`→java/maven, `package.json`→node, `go.mod`→go, `pyproject.toml`→python, …) plus CI (`.github/workflows`, `azure-pipelines.yml`) and deploy (`Dockerfile`, `*.tf`) signals.
3. **Diagrams** ([`architecture.py`](../../doctyze/generate/architecture.py)) — if a `codeboarding` binary is on PATH, run it into `docs/architecture/diagrams/`; otherwise return `None` and let the agent draw Mermaid itself.
4. **Manifest** ([`manifest.py`](../../doctyze/generate/manifest.py)) — write `.doctyze/bootstrap-manifest.md` listing which skill produces which artifact.

## Inputs / outputs
- **Input:** a repo path (default `.`).
- **Output:** canonical `docs/` skeleton (anchored), `.doctyze/bootstrap-manifest.md`.

## Edge cases
- Re-running creates no duplicate indexes (idempotent).
- Stack detection is best-effort and language-agnostic; unknown stacks still scaffold.
- CodeBoarding is optional — absence is reported, not an error.

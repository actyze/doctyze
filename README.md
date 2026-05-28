# Doctyze

**Open-source documentation scaffolder for any codebase — modern or legacy.**
Turn any repository into living documentation for humans and AI agents.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-supported-green)](https://agents.md)
[![Status](https://img.shields.io/badge/status-pre--alpha-orange)]()

> By [Actyze](https://github.com/actyze). Doctyze closes the OSS gap for
> comprehensive code-context generation — see
> [`docs/LANDSCAPE.md`](docs/LANDSCAPE.md) for the market argument.

## What Doctyze does

One command scans your repository, detects the stack, and produces:

- **`docs/architecture/`** — ADRs (MADR), Mermaid diagrams, Structurizr C4
- **`docs/runbooks/`** — operational guides
- **`docs/specs/`** — feature specifications (Spec Kit format)
- **`AGENTS.md`** — universal context for AI coding agents (AAIF standard)
- **`.claude/skills/`** + **`.cursor/rules/`** — per-feature procedural skills
- **`.holmes/runbooks/`** — machine-executable runbooks for AI SRE agents
- **`.github/workflows/doctyze-review.yml`** — PR-doc-coupling enforcement

Every artifact is stamped with a confidence marker:
**🟢 CONFIRMED** (extracted from code) ·
**🟡 INFERRED** (LLM-inferred, needs review) ·
**🔴 GAP** (cannot be extracted; flagged for senior-engineer interview).

## Why this exists

Proprietary tools (Mintlify, Kodesage, iBEAM IntDoc, Swimm) each cover ~30%
of the surface area. The OSS pieces exist (Reversa, adr-tools, log4brains,
Docusaurus, Claude Code skills, AGENTS.md, HolmesGPT) but no one has bundled
them. The legacy modernization market is **$19.9B** and growing 14.9%
annually — entirely served by proprietary consultancy platforms today.

**Doctyze is the bundle.**

## What gets generated — by stack

### Modern stack (Java/Spring, Python, Node, React, Go)

```
modern-service/
├── README.md
├── AGENTS.md                          ← universal agent context
├── CODEOWNERS
├── pyproject.toml | package.json | pom.xml | go.mod
│
├── docs/
│   ├── index.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── workspace.dsl              ← Structurizr C4
│   │   ├── diagrams/
│   │   │   ├── system-context.mmd     ← Mermaid (inline-renders on GitHub)
│   │   │   ├── container.mmd
│   │   │   └── sequence-*.mmd
│   │   └── decisions/                 ← ADRs (MADR)
│   │       └── 0001-*.md
│   ├── specs/
│   │   └── 001-feature/{spec,plan,tasks}.md
│   ├── runbooks/
│   ├── investigations/                ← postmortems
│   └── api/openapi.yaml
│
├── .claude/skills/                    ← Claude Code project skills
├── .cursor/rules/                     ← Cursor (mirror)
├── .github/workflows/doctyze-review.yml
├── .holmes/runbooks/                  ← machine-executable runbooks
│
├── src/
└── tests/
```

### Legacy stack (COBOL, SAP ABAP, IBM i RPG, VB6, .NET Framework, PowerBuilder, Delphi)

Different reality: legacy SCM, library-and-object models, single mega-repo
per application. The structure reflects how legacy code actually organizes.

```
legacy-app/
├── README.md
├── AGENTS.md
├── CODEOWNERS
├── DOCTYZE.yaml                       ← project metadata (stack, ingestion)
│
├── docs/
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── data-flow/                 ← legacy is data-centric
│   │   │   ├── batch-cycle.mmd
│   │   │   └── online-tx-flow.mmd
│   │   ├── diagrams/
│   │   │   ├── job-dependencies.mmd   ← JCL / SAP variants / IBM i jobs
│   │   │   ├── transaction-map.mmd    ← CICS / SAP t-codes / 5250
│   │   │   └── copybook-graph.mmd
│   │   └── decisions/                 ← ADRs
│   │
│   ├── data/                          ← first-class concern in legacy
│   │   ├── schemas/                   ← DB2/IMS DDL, SAP DDIC, IBM i DDS
│   │   ├── copybooks-catalog.md
│   │   └── lineage/
│   │
│   ├── programs/                      ← one md per significant program
│   ├── jobs/                          ← scheduled work
│   ├── interfaces/                    ← external boundaries
│   │   ├── inbound/
│   │   └── outbound/
│   ├── runbooks/
│   │   ├── batch-failure-recovery.md
│   │   └── abend-codes.md
│   ├── investigations/
│   │   └── adr-archaeology/           ← interview-augmented ADR capture
│   │       ├── INTERVIEW-001-*.md
│   │       └── pending-questions.md
│   └── modernization/                 ← bridge folder during migration
│
├── .claude/skills/
├── .github/workflows/doctyze-review.yml
│
├── src/
│   ├── cobol/ | abap/ | rpg/ | vb6/ | delphi/
│   ├── jcl/                           ← COBOL-specific
│   └── ddl/
│
└── tools/
    ├── ingest-from-endevor.sh         ← legacy-SCM bridges
    └── round-trip.sh
```

## Quick start

```bash
# Install (choose one)
pip install actyze-doctyze                        # Python/PyPI
npm install -g @actyze/doctyze                    # Node/npm
brew install actyze/tap/doctyze                   # macOS
docker pull ghcr.io/actyze/doctyze:latest         # any platform

# Configure your LLM
export ANTHROPIC_API_KEY=...                      # Claude (recommended)
# Or OPENAI_API_KEY, GOOGLE_API_KEY, AZURE_OPENAI_*, or local (Ollama)

# Scaffold any repo
cd ~/work/your-repo
doctyze init                                      # auto-detects stack
doctyze verify                                    # check for drift
doctyze pr-bot install                            # wire up PR enforcement
```

## Execution by stack

### Modern stack (already in git)

```bash
# Java/Spring (auto-detected from pom.xml or build.gradle)
doctyze init

# Python (auto-detected from pyproject.toml)
doctyze init

# Force the stack if auto-detect is wrong
doctyze init --stack=java-spring
```

### Legacy stack (depends on where the code lives)

```bash
# COBOL on mainframe (Endevor / ChangeMan / Librarian)
doctyze ingest endevor \
  --connection endevor://mainframe.corp:1610/CICSDEV \
  --subsystem PAYROLL \
  --output ./payroll-app
cd payroll-app && doctyze init --stack=cobol

# SAP ABAP (via abapGit)
abapgit pull ZPACKAGE_HR
cd ZPACKAGE_HR && doctyze init --stack=abap

# IBM i RPG (via ARCAD)
doctyze ingest ibm-i --connection arcad://ibmi.corp/INVENTORY --output ./inv
cd inv && doctyze init --stack=ibm-i-rpg

# Legacy already in git (VB6 / .NET Framework / PowerBuilder / Delphi)
doctyze init --stack=delphi
```

### Air-gapped / regulated enterprise mode

```yaml
# .doctyze.yaml
llm:
  provider: ollama
  endpoint: http://internal-llama.corp:11434
  model: llama-3.3-70b
  fallback: deny                                  # never send anything off-prem
extraction:
  retain_source_locally: true
  audit_log: /var/log/doctyze/
```

## The three pillars

| Pillar | What it does | When it runs |
|---|---|---|
| **Scaffolder** | Scans repo, detects stack, emits canonical structure with confidence markers | Once per repo (`doctyze init`); on demand |
| **PR Review Agent** | On each PR, determines whether docs need updating; comments inline; can block merge | Continuously (GitHub Action / GitLab CI / Bitbucket) |
| **Skills & Rules** | Authors machine-readable conventions (`AGENTS.md` + `SKILL.md`) so future AI agents understand your repo | Always-on context for Claude Code, Cursor, Codex, Copilot, Cline |

## PR review — what gets blocked

Default-strict rules (configurable via `.doctyze.yaml`):

| Trigger | Action |
|---|---|
| Public API changed without `docs/api/openapi.yaml` update | **Block** + suggest diff |
| New `try/except` or error class without runbook entry | **Block** + suggest runbook stub |
| New external dependency added without ADR | **Block** + propose ADR stub |
| ADR file deleted | **Block** unconditionally (ADRs are append-only) |
| Pure refactor (whitespace, rename, no behavior change) | **Pass silently** |

Enforcement levels: `warn-only` / `block-required` / `block-all`. Each
repo picks one in `.doctyze.yaml`.

## Project structure

```
doctyze/                               this repo
├── README.md                          ← you are here
├── LICENSE                            ← Apache 2.0
├── AGENTS.md                          ← agent context for contributors
├── CONTRIBUTING.md
│
├── cli/                               ← `doctyze` CLI (Python)
│   └── src/doctyze/
│
├── templates/                         ← canonical structures
│   ├── modern/                        ← Java/Python/Node/React/Go
│   └── legacy/                        ← COBOL/ABAP/IBM i/VB6/.NET Fx/PB/Delphi
│
├── extractors/                        ← language-specific content extractors
│   ├── modern/{java-spring,python,node-react,go}
│   └── legacy/{cobol,abap,ibm-i-rpg,vb6,dotnet-framework,powerbuilder,delphi}
│
├── pr-review-action/                  ← the GitHub Action
│
├── skills-library/                    ← canonical SKILL.md files shipped per stack
│   ├── modern/
│   └── legacy/
│
└── examples/                          ← end-to-end demo repos
```

## Roadmap

| Version | Scope |
|---|---|
| **v0.1** (8–12 weeks) | Modern: Java/Spring + Python · PR Review Action (warn-only) · 5 default skills per stack · 1 demo (Spring PetClinic) |
| **v0.2** (3–4 months) | Add Node/React, Go to modern · Add **COBOL** + **SAP ABAP** to legacy · PR Review in block-required mode · GitLab CI · Backstage TechDocs adapter |
| **v0.3** (5–6 months) | Add IBM i RPG, VB6, .NET Framework · Interview-augmented ADR archaeology · Bitbucket / Azure DevOps |
| **v1.0** | PowerBuilder, Delphi · plugin SDK · candidate for AAIF / CNCF Sandbox |

## Status

**Pre-alpha. Day-1 commit.** Scaffolder skeleton, templates, and PR review
GitHub Action are in place; LLM-driven extraction is the immediate next
milestone. Track progress in [GitHub Issues](https://github.com/actyze/doctyze/issues).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The highest-leverage contributions
right now are language extractors — especially for legacy stacks. PRs welcome.

## License

[Apache 2.0](LICENSE).

# Doctyze examples gallery

Real `docs/` trees Doctyze produced on well-known open-source repositories, across stacks.

**Why this exists.** The README says Doctyze is stack-agnostic. This gallery is the *evidence* — each
entry is a `docs/` tree Doctyze actually generated on a public repo, with provenance (source URL + commit
SHA) so anyone can reproduce it. It doubles as a before/after for the launch and as SEO surface.

> **Honesty note.** Until an entry appears in the table below with a committed `docs/` tree, it is **not**
> validated. Do not cite a repo/stack here that isn't listed as ✅. Today, end-to-end validation is limited
> (see [ADR-0003](../docs/architecture/decisions/0003-pivot-to-context-layer-generator.md)); this gallery is
> how we close that gap before making broad "any stack" claims.

## Status

| Example | Stack | Source repo | Status |
|---|---|---|---|
| [click](./click/) | Python | [pallets/click](https://github.com/pallets/click) @ `16fc00e` | ✅ structured layer (arch + 3 specs + ADR) |
| [hono](./hono/) | TypeScript | [honojs/hono](https://github.com/honojs/hono) @ `d6b1d32` | ✅ structured layer (arch + 3 specs + ADR) |
| [cobra](./cobra/) | Go | [spf13/cobra](https://github.com/spf13/cobra) @ `ad460ea` | ✅ structured layer (arch + 3 specs + ADR) |
| [petclinic](./petclinic/) | Java / Spring | [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic) @ `51045d1` | ✅ **full suite** (arch + 3 specs + ADR + 2 runbooks + observability + skills) |

<!-- As each example lands, add a row: | [name](./name/) | Python | owner/repo @sha | ✅ | -->

> **Scope note.** The **library** entries (click / hono / cobra) show Doctyze's generated **structured
> layer** (architecture, specs, ADR) — not a full docs replacement, since those repos already ship
> narrative docs and, as libraries, have no deployment/ops surface. The **service** entry (petclinic)
> is a *deployable* Spring app, so it shows the **complete suite** — including runbooks and observability
> grounded in the real Docker/k8s/CI/Actuator config. Where a repo lacks something, the docs say so
> rather than invent it.

### Candidate repos (planned, one per stack)

Pick small-to-medium, widely-recognized repos so the output is easy to skim:

- **Python** — a focused library (e.g. a CLI or HTTP lib)
- **TypeScript / React** — a web framework or app
- **Go** — a service or CLI framework
- **Rust** — a crate
- **Java / Spring** — the stack already exercised by the existing fixture
- **Doctyze itself** — dogfood; the strongest possible proof

## How each example is produced

Doctyze is **BYO-agent**: the deterministic CLI scaffolds and detects, but the prose is written by an IDE
agent. So producing an example is two steps — a scripted prep, then one agent pass:

```bash
# 1. Prep: clone the target and run the deterministic Doctyze setup
scripts/build-example.sh prep <name> <git-url> [ref]
#    → clones into examples/.work/<name> (gitignored), runs `doctyze init`,
#      writes examples/<name>/PROVENANCE.md

# 2. Generate: open examples/.work/<name> in your IDE and run  /doctyze
#    (this is the agent step — it reads the code and writes the docs)

# 3. Collect: copy the generated docs/ tree into the committed gallery
scripts/build-example.sh collect <name>
#    → copies examples/.work/<name>/docs → examples/<name>/docs
```

Then add the row to the Status table above with the resolved commit SHA from `PROVENANCE.md`, and run
`doctyze index` if you want the decisions/index refreshed.

## Layout

```
examples/
  README.md              # this file
  .gitignore             # ignores the .work/ clones
  <name>/
    PROVENANCE.md        # source URL, commit SHA, date, Doctyze version
    docs/                # the generated docs/ tree (the actual artifact)
```

# Doctyze examples gallery

Real `docs/` trees Doctyze produced on well-known open-source repositories, across stacks.

**Why this exists.** The README says Doctyze is stack-agnostic. This gallery is the *evidence* — each
entry is a `docs/` tree Doctyze actually generated on a public repo, with provenance (source URL + commit
SHA) so anyone can reproduce it. It doubles as a before/after for the launch and as SEO surface.

> **Honesty note.** The gallery now covers **Python, TypeScript, Go, and Java/Spring** — four distinct
> stacks. Still, only cite a repo/stack that appears in the table below as ✅; don't claim breadth beyond
> what's committed here. This gallery is what backs Doctyze's "stack-agnostic" claim (see
> [ADR-0003](../docs/architecture/decisions/0003-pivot-to-context-layer-generator.md)).

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

### Still to add (candidates)

Covered so far: **Python** (click), **TypeScript** (hono), **Go** (cobra), and **Java/Spring**
(petclinic — the full suite). Good next additions, if you want more breadth:

- **Rust** — a crate
- **Doctyze itself** — dogfood; the strongest possible proof
- **A second service** (Python/FastAPI, Node, or Go) — another full-suite entry to complement petclinic

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

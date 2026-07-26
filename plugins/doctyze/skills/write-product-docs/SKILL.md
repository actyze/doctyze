---
name: write-product-docs
description: Reverse-engineer narrative product documentation from the code into docs/product/ — a curated Docusaurus-ready set (overview, getting started, concepts, feature guides) for product owners and users, tied to the technical specs. NOT one-per-capability, no Gherkin.
---
# write-product-docs
Write a small, **curated** set of narrative product docs under `docs/product/` — the product-owner / end-user view of the system, in the style of a documentation site (e.g. Docusaurus: *Welcome · Getting Started · Concepts · Feature guides · How-tos*). Think docs.actyze.io, not a pile of specs.

This is the **product-documentation** layer. `write-spec` produces the technical specs (entry points, `file:line`, modules) for engineers. This produces prose a product owner or user reads to understand and use the product — and it **links down** to the technical specs for the mechanics.

## Do NOT sprawl (read this first)
- **Not one doc per capability.** A whole product area gets ONE narrative guide that covers several capabilities together. A typical repo needs a **handful** of product docs, not dozens.
- **No Gherkin / no acceptance criteria / no user-story lists here.** Given/When/Then feature files are generated elsewhere (e.g. the team's ADO workflow) — do not duplicate them. This layer is narrative documentation, not executable specs.
- **No implementation detail in the body.** No `file:line`, no function/class/table names, no framework or language names. When the reader needs mechanics, they follow the link to the technical spec.

## Structure to produce (Docusaurus-ready)
Curate to what the repo actually warrants — skip sections that don't apply:
- `docs/product/overview.md` — **Welcome / Overview.** What the product is, who it's for, the value, and a short "what you can do" list. This is the intro page (give it `sidebar_position: 1`).
- `docs/product/getting-started.md` — the shortest path to using it (install/run/first result), in user terms.
- `docs/product/concepts.md` — the key ideas and how they fit together (the mental model), narrative and diagram-friendly.
- `docs/product/<feature-area>.md` — **one guide per product area** (not per function): what it does for the user, when to use it, how to use it, notable options/limits. A few of these, grouped by product area.
- (optional) `docs/product/faq.md`, `docs/product/configuration.md` — only if the repo has real content for them.

**Do not hand-write `docs/product/index.md`** — `doctyze index` owns it (it's the auto-generated table of contents for the section, same as every other `docs/` section). Put the Welcome/intro narrative in `overview.md`. Order pages for the sidebar with `sidebar_position` in frontmatter (or a leading number in the filename) — whatever the repo's publish setup expects (see the publish guide).

## How (match this depth bar)
1. **Read the code** for each product area so the docs describe what the system *actually* does — this is reverse-engineered, grounded, not marketing fiction.
2. Write in plain product language: **what** the user accomplishes and **why it matters**, never **how** it's coded.
3. In each feature-area guide, end with a **Learn more / technical detail** link to the matching `docs/specs/<feature>.md`.
4. Be honest: flag capabilities that are experimental, partial, or behave unexpectedly — say so plainly (a short "Limitations" note), don't oversell.

## The tie to technical specs (traceability)
- Each product-area guide links down: `**Technical detail:** [<feature>](../specs/<feature>.md)`.
- In the matching technical spec's `## Related`, link back: `Product docs: [../product/<feature-area>.md]`.
- Product owner reads `docs/product/`; one click reaches the grounded technical spec.

## Anchor (keep it scoped)
`affects:` = the specific module(s) the guide covers (e.g. `[app/checkout/**]` for the checkout guide; the overview may anchor to a small set of top-level entry points), never the whole tree. A product doc goes stale when the behavior it describes changes — keep the anchor tight so that signal stays meaningful.

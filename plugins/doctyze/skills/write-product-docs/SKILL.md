---
name: write-product-docs
description: Reverse-engineer narrative product documentation from the code into docs/product/ — a curated but substantial Docusaurus-ready set (overview, concepts+glossary, rich feature guides with worked examples, use-cases) for product owners and users, tied to the technical specs. NOT one-per-capability, no Gherkin.
---
# write-product-docs
Write a **curated but substantial** set of narrative product docs under `docs/product/` — the product-owner / end-user view of the system, in the style of a real documentation site (e.g. Docusaurus: *Welcome · Concepts · Feature guides · Use cases*). Think docs.actyze.io. Curated in **number of files**, but **rich in depth** — each doc earns its place with real explanation and **worked examples**, not a thin paragraph.

This is the **product-documentation** layer. `write-spec` produces the technical specs (entry points, `file:line`, modules) for engineers. This produces prose a product owner reads to understand and use the product — and it **links down** to the technical specs for the mechanics.

## Two failure modes to avoid (read this first)
- **Too thin** (the common one): an overview plus one short paragraph-per-feature. A product owner learns nothing they couldn't guess from the feature name. **Fix: depth + worked examples** (below).
- **Too sprawling:** one doc per code capability, dozens of files. **Fix: one guide per product AREA**, covering several capabilities together.
- Also: **No Gherkin / user-story / Given-When-Then lists** (the team's ADO workflow owns those — don't duplicate), and **no implementation detail** in the body (no `file:line`, function/class names, framework/language names). When the reader needs mechanics, they follow the link to the technical spec.

## The file set (curated — aim for ~4–6 docs, scale to the repo)
- `docs/product/overview.md` — **Welcome.** What the product is, who it's for, the value, a "what you can do" list, and a short **how it fits** (where this sits relative to neighbouring services). `sidebar_position: 1`.
- `docs/product/concepts.md` — the **mental model** + a **glossary** of the business terms a PO must know (each term in one plain sentence). Embed a product-friendly diagram if one already exists in `docs/architecture/diagrams/` — reuse it, don't invent one.
- `docs/product/<feature-area>.md` — **one rich guide per product area** (not per function). Follow the depth bar below. Usually 1–3 of these.
- `docs/product/use-cases.md` — real scenarios: who uses it, the goal, and which features deliver it. The "so what".
- (optional) `docs/product/getting-started.md`, `faq.md`, `configuration.md` — only where the repo has real content.

**Do not hand-write `docs/product/index.md`** — `doctyze index` owns it (the auto-generated section TOC). Put the Welcome narrative in `overview.md`. Order pages for the sidebar with `sidebar_position` in frontmatter.

## Depth bar for each feature guide (this is where "too thin" gets fixed)
Every `<feature-area>.md` covers, in plain product language:
1. **What it does** — the capability and the value, a full paragraph, not one line.
2. **When to use it** — the situations/triggers a PO recognises.
3. **How it works** — the flow in plain steps (numbered), no code.
4. **Worked example(s)** — *the most important section.* At least one concrete, grounded walk-through with **real values**: a sample input and the resulting output/behaviour (e.g. a specific cart + promotion → the discount and final total; a specific sign-in journey step by step). Use a table when several cases illustrate a rule. Examples make product docs land — never skip them.
5. **Options & limits** — a table of the settings, thresholds, defaults, and boundaries that matter to a PO.
6. **Edge cases & limitations** — in plain terms: what it deliberately doesn't do, where it's partial/experimental, honestly.
7. **Technical detail** — link(s) down to the matching `docs/specs/<feature>.md`.

## Worked examples MUST be grounded (do not invent numbers)
Examples are the payoff, but a made-up number destroys trust. Every example's values must trace to real behaviour — read the code, the technical specs, and especially the **test fixtures** (tests are a goldmine of real input→output pairs) to source concrete values. If you can't ground a number, describe the behaviour qualitatively rather than fabricating a figure, and say what the real value depends on.

## How (procedure)
1. **Read the technical specs first** (if present) — they're already code-grounded; build the product docs on top and tie back to them. Where specs are missing, read the code (and tests) directly.
2. Write in plain product language: **what** the user accomplishes and **why**, never **how** it's coded.
3. Reuse existing diagrams from `docs/architecture/diagrams/`; don't redraw.
4. Be honest about stubs, partial, or surprising behaviour — a short, plain "Limitations" note beats overselling.

## The tie to technical specs (traceability)
- Each feature guide links down: `**Technical detail:** [<feature>](../specs/<feature>.md)`.
- In the matching technical spec's `## Related`, link back: `Product docs: [../product/<feature-area>.md]`.
- Product owner reads `docs/product/`; one click reaches the grounded technical spec.

## Anchor (keep it scoped)
`affects:` = the specific module(s) the guide covers (e.g. `[app/checkout/**]`), never the whole tree. A product doc goes stale when the behaviour it describes changes — keep the anchor tight so that signal stays meaningful.

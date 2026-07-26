---
name: write-product-docs
description: Reverse-engineer COMPREHENSIVE functional documentation from the code into docs/product/ — the functional spec of every capability, in product-owner language with no technical detail, mirroring the technical specs 1:1, plus an overview/concepts/use-cases wrapper. Narrative prose, not Gherkin.
---
# write-product-docs
Write **comprehensive functional documentation** under `docs/product/` — the product-owner / end-user view of the system. This is the **functional spec of the product**: it captures *every* capability and what it does for the user, in plain language, with **no technical detail**. Presented as a documentation site (Docusaurus-style: *Welcome · Concepts · one functional doc per capability · Use cases*), so it reads like docs.actyze.io.

`write-spec` produces the **technical** specs (entry points, `file:line`, modules) for engineers. This produces the **functional** counterpart for product owners: same capabilities, described by *what they do and why*, never *how they're built*. The two are a matched pair — every technical spec should have a functional doc, linked both ways.

## Cover everything (this is the core requirement)
- **Complete coverage, not a curated highlight reel.** Capture **every functionality**. If a capability exists in the code, it gets documented functionally. A product owner should be able to learn *everything the product does* from `docs/product/` alone.
- **Mirror the technical specs 1:1.** For **each** doc in `docs/specs/`, write a functional counterpart in `docs/product/`. Six technical specs → six functional docs (plus the wrapper pages below). Where specs are missing, enumerate the capabilities from the code and cover each.
- **Cover every sub-functionality inside a capability.** If a capability has variants (e.g. nine promotion types, five API operations, four message types), document **each one** — a table row per variant plus a plain description and example. Do not collapse them into "supports several types".

## What "functional, no technical detail" means
- **In:** what the user can do, when they'd use it, the business rules, the inputs/outputs in user terms, worked examples with real values, options, limits, edge cases.
- **Out:** `file:line`, function/class/module names, framework/language names, code, data-structure shapes. When a reader wants the mechanics, they follow the **Technical detail** link to the matching technical spec.
- **Not Gherkin.** Narrative prose, not Given/When/Then feature files or user-story lists — the team's ADO workflow owns those; don't duplicate them.

## The file set
Wrapper pages (navigation + shared understanding):
- `docs/product/overview.md` — **Welcome.** What the product is, who it's for, the value, a "what you can do" list, and a short **how it fits**. `sidebar_position: 1`.
- `docs/product/concepts.md` — the **mental model** + a **glossary** of every business term a PO must know (one plain sentence each). Reuse a diagram from `docs/architecture/diagrams/` if one exists; don't invent one.
- `docs/product/use-cases.md` — real end-to-end scenarios mapping goals to the capabilities that deliver them.

Then **one functional doc per capability** — the comprehensive part:
- `docs/product/<capability>.md` — one per technical spec / per distinct capability. Name them for the capability, mirroring the technical spec name where possible. This is where completeness lives — expect several of these, matching the breadth of the product.

**Do not hand-write `docs/product/index.md`** — `doctyze index` owns it (the auto-generated section TOC). Put the Welcome narrative in `overview.md`. Order pages with `sidebar_position` in frontmatter.

## Depth bar for each capability doc
Every `<capability>.md` covers, in plain product language:
1. **What it does** — the capability and its value, a full paragraph.
2. **When it's used** — the situations/triggers a PO recognises.
3. **How it works** — the flow in plain numbered steps, no code.
4. **The functionalities in detail** — enumerate **every** sub-function/variant/option of this capability (a table plus a short description of each). This is what makes coverage complete.
5. **Worked example(s)** — at least one concrete, **grounded** walk-through with real values (sample input → resulting behaviour/output). Use a table when several cases illustrate a rule. Never skip examples.
6. **Options & limits** — settings, thresholds, defaults, boundaries that matter to a PO.
7. **Edge cases & limitations** — plainly: what it deliberately doesn't do, where it's partial/experimental.
8. **Technical detail** — link down to the matching `docs/specs/<capability>.md`.

## Worked examples MUST be grounded (do not invent numbers)
A made-up number destroys trust. Every example's values must trace to real behaviour — read the code, the technical specs, and especially the **test fixtures** (a goldmine of real input→output pairs). If you can't ground a number, describe the behaviour qualitatively and say what the real value depends on, rather than fabricating a figure.

## How (procedure)
1. **Inventory the capabilities first.** List every doc in `docs/specs/` and every distinct capability in the code — that list is your coverage checklist; write a functional doc for each.
2. **Read the technical spec (or code) for each**, then restate it functionally: **what** the user accomplishes and **why**, never **how** it's coded.
3. Reuse existing diagrams from `docs/architecture/diagrams/`; don't redraw.
4. Be honest about stubs, partial, or surprising behaviour — a short, plain "Limitations" note beats overselling.

## The tie to technical specs (traceability)
- Each capability doc links down: `**Technical detail:** [<capability>](../specs/<capability>.md)`.
- In the matching technical spec's `## Related`, link back: `Product docs: [../product/<capability>.md]`.
- Product owner reads `docs/product/`; one click reaches the grounded technical spec.

## Anchor (keep it scoped)
`affects:` = the specific module(s) the capability doc covers (mirror the technical spec's anchor), never the whole tree. A functional doc goes stale when the behaviour it describes changes — keep the anchor tight so that signal stays meaningful.

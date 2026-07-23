---
name: write-spec
description: Reverse-engineer a grounded feature specification from the code (one per capability) into docs/specs/.
---
# write-spec
Write `docs/specs/<feature>.md` — one per major feature/capability.

## Before you write (read-existing-first)
- Survey `docs/`. If a large doc (e.g. a TECHNICAL_DOCUMENTATION) already covers features, **split/refresh** it into per-feature specs and cite/supersede it — do NOT write a parallel duplicate.
- Maintain `docs/specs/index.md` as a table of the specs you write.

## How (match this depth bar)
1. Find the feature's code (controller/handler/service/agent) and its entry function.
2. **Read it**, then document what it ACTUALLY does — cite the entry point as `path:line` and name real functions/constants.
3. Sections: `## Purpose` · `## Entry point` (file:line) · `## Inputs` · `## Behavior` (numbered, grounded, cite modules) · `## Outputs` · `## Edge cases` · `## Related`.
4. Be honest: flag stubs, experimental code, bugs, and where existing docs disagree with the code.
5. If a product-owner-facing **functional spec** exists (`write-functional-spec`), link to it in `## Related`: `Functional spec: [../functional-specs/<feature>.md]`. This is the bidirectional tie — the technical spec (this) is *how*, the functional spec is *what/why for the user*.

## Anchor (narrow)
`affects:` = the specific module(s) this spec describes (e.g. `[app/agents/intent_agent.py]`), never the whole tree.

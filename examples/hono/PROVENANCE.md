# Provenance — hono

- **Source:** https://github.com/honojs/hono
- **Commit:** `d6b1d32a697ef9ba9f5036753fe9bde1121c0ff9` (`d6b1d32`)
- **Generated with:** doctyze, version 0.3.4
- **Generated on:** 2026-07-05
- **Stack:** TypeScript

## Scope of this entry

Doctyze's **code-grounded structured layer** for Hono, reverse-engineered from its TypeScript source:
an architecture overview, two Mermaid diagrams, three capability specs, and one reverse-engineered ADR.
Hono's own docs/site are left untouched upstream and are **not** reproduced here.

Every generated doc carries a Doctyze freshness `affects:` anchor pointing at the real `src/*.ts` files
it describes. Source references in prose are by filename at the pinned commit; browse them at:
https://github.com/honojs/hono/tree/d6b1d32a697ef9ba9f5036753fe9bde1121c0ff9/src

## Freshness demo (verified 2026-07-05)

Editing `src/context.ts` in the clone and running `doctyze watch --base HEAD` flagged exactly the four
docs anchored to that file, and nothing else:

```
4 doc(s) may be stale:
  - docs/specs/middleware-and-context.md          (regenerate: write-spec)
  - docs/architecture/overview.md                 (regenerate: write-architecture)
  - docs/architecture/diagrams/object-model.md    (regenerate: write-architecture)
  - docs/architecture/diagrams/invocation-lifecycle.md  (regenerate: write-architecture)
```

## Reproduce

```bash
scripts/build-example.sh prep hono https://github.com/honojs/hono
# then run /doctyze in your IDE on examples/.work/hono (or generate the structured layer by hand)
scripts/build-example.sh collect hono
```

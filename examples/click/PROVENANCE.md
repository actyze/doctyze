# Provenance — click

- **Source:** https://github.com/pallets/click
- **Commit:** `16fc00e2f4a2717a521084f193709a6058afc693` (`16fc00e`, 2026-07-02)
- **Generated with:** doctyze, version 0.3.4
- **Generated on:** 2026-07-05
- **Stack:** Python

## Scope of this entry

Click already ships an extensive hand-written Sphinx docs set. Doctyze's contribution — and what is
committed here — is the **code-grounded structured layer click lacked**: an architecture overview, two
Mermaid diagrams, three capability specs, and one reverse-engineered ADR. Click's own narrative docs are
left untouched in the upstream repo and are **not** reproduced here.

Every generated doc carries a Doctyze freshness `affects:` anchor pointing at the real `src/click/*.py`
files it describes, so a change to that code flags the doc as stale.

Source links inside the docs are **repo-relative** (e.g. `../../../src/click/core.py`) — they resolve in
click's own tree. To follow them, browse the source at the pinned commit:
https://github.com/pallets/click/tree/16fc00e2f4a2717a521084f193709a6058afc693/src/click

## Freshness demo (verified 2026-07-05)

Editing `src/click/types.py` in the clone and running `doctyze watch --base HEAD` flagged exactly the
three docs anchored to that file, and nothing else:

```
3 doc(s) may be stale:
  - docs/specs/parameter-types.md                       (regenerate: write-spec)
  - docs/architecture/overview.md                       (regenerate: write-architecture)
  - docs/architecture/diagrams/invocation-lifecycle.md  (regenerate: write-architecture)
```

## Reproduce

```bash
scripts/build-example.sh prep click https://github.com/pallets/click
# then run /doctyze in your IDE on examples/.work/click (or generate the structured layer by hand)
scripts/build-example.sh collect click
```

# Provenance — cobra

- **Source:** https://github.com/spf13/cobra
- **Commit:** `ad460ea8f249db69c943a365fb84f3a59042d54e` (`ad460ea`)
- **Generated with:** doctyze, version 0.3.4
- **Generated on:** 2026-07-05
- **Stack:** Go

## Scope of this entry

Doctyze's **code-grounded structured layer** for Cobra, reverse-engineered from its Go source: an
architecture overview, two Mermaid diagrams, three capability specs, and one reverse-engineered ADR.
Cobra's own docs (`site/`) are left untouched upstream and are **not** reproduced here.

Every generated doc carries a Doctyze freshness `affects:` anchor pointing at the real `.go` files it
describes (repo-root: `command.go`, `args.go`, `completions.go`, …). Source references in prose are by
filename at the pinned commit; browse them at:
https://github.com/spf13/cobra/tree/ad460ea8f249db69c943a365fb84f3a59042d54e

## Freshness demo (verified 2026-07-05)

Editing `completions.go` in the clone and running `doctyze watch --base HEAD` flagged exactly the three
docs anchored to that file, and nothing else:

```
3 doc(s) may be stale:
  - docs/specs/shell-completion.md              (regenerate: write-spec)
  - docs/architecture/overview.md               (regenerate: write-architecture)
  - docs/architecture/diagrams/object-model.md  (regenerate: write-architecture)
```

## Reproduce

```bash
scripts/build-example.sh prep cobra https://github.com/spf13/cobra
# then run /doctyze in your IDE on examples/.work/cobra (or generate the structured layer by hand)
scripts/build-example.sh collect cobra
```

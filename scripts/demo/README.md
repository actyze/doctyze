# Demo — the affected-docs loop (README hero GIF)

A self-contained, offline demo of Doctyze's core wedge: change code → see exactly which docs it made
stale. This is the 20-second loop meant for the top of the README.

## Record it

```bash
brew install vhs          # one-time (https://github.com/charmbracelet/vhs)
./scripts/demo/record.sh  # → scripts/demo/freshness-loop.gif
```

Then reference it under the README H1:

```markdown
![Doctyze flags exactly which docs a code change made stale](scripts/demo/freshness-loop.gif)
```

## What it shows (the four beats)

Outcome-first, no anchor YAML or `sed` on screen:

1. **Generate** — the `docs/` tree the IDE agent wrote from the code (`find docs`), and the refund
   spec it produced (which documents the limit as `100.00`). Doctyze scaffolds + detects; **the
   agent writes the prose** — so the tape shows the artifact, not a faked generation command.
2. **Change** — the code edit is applied off-camera (`Hide`) and revealed as a real `git diff`
   (`MAX_AUTO_REFUND` `100.00 → 500.00`), the way a developer actually changes code.
3. **Catch** — `doctyze watch` flags **only** `refunds.md`; `money.md` and the ADR (both anchored
   to `money.py`) stay fresh. The precision — *the exact doc, not "your docs are out of date"* — is
   the point.
4. **Fix** — a caption hands off to the IDE agent (`/doctyze`) to regenerate just that one doc
   (your model, no API key).

The fixture is anchored so the change hits exactly one doc:
- `docs/specs/refunds.md` → `affects: [src/payments/refund.py]`  ← the one that goes stale
- `docs/specs/money.md`   → `affects: [src/payments/money.py]`
- `docs/architecture/decisions/0001-money-as-decimal.md` → `affects: [src/payments/money.py]`

## How it works

- [`sample/`](sample/) is a tiny throwaway repo (a payments module + two anchored specs). It ships as
  plain files; [`freshness-loop.tape`](freshness-loop.tape) copies it into a temp git repo at record
  time, so the demo is deterministic and needs no network.
- The GIF (`freshness-loop.gif`) **is committed** — a README hero image must be in the repo to render
  on GitHub/PyPI. When the loop changes, re-run `record.sh` and commit the regenerated GIF so it never
  drifts from reality. (The `sample/` fixture and the tape are the source of truth; the GIF is derived.)

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

## What it shows

Two specs, each anchored to the code it documents:
- `docs/specs/refunds.md` → `affects: [src/payments/refund.py]`
- `docs/specs/money.md`   → `affects: [src/payments/money.py]`

Editing `src/payments/refund.py` and running `doctyze watch` flags **only** `refunds.md` — not
`money.md`. That precision (the specific stale docs, not "your docs are out of date") is the product.

## How it works

- [`sample/`](sample/) is a tiny throwaway repo (a payments module + two anchored specs). It ships as
  plain files; [`freshness-loop.tape`](freshness-loop.tape) copies it into a temp git repo at record
  time, so the demo is deterministic and needs no network.
- The GIF (`freshness-loop.gif`) **is committed** — a README hero image must be in the repo to render
  on GitHub/PyPI. When the loop changes, re-run `record.sh` and commit the regenerated GIF so it never
  drifts from reality. (The `sample/` fixture and the tape are the source of truth; the GIF is derived.)

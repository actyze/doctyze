---
doctyze:
  artifact: guide
  generated_by: doctyze
  affects:
    - doctyze/freshness/detect.py
    - doctyze/cli.py
    - action.yml
  last_verified: 2026-07-05
---

# Guide — Checking Documentation Drift

Doctyze checks drift in **two layers**. Use both: the deterministic layer is the always-on
backstop; the model-assisted layer is what you reach for when an agent is already in the loop
(e.g. an AI-assisted code review).

| | **Deterministic** (default) | **Model-assisted** (when an agent is wired) |
|---|---|---|
| Answers | *Which anchored docs changed under this diff? What changed but is documented by nothing?* | *Does the changed functionality exist in the docs? Is it net-new? Has an existing doc drifted?* |
| Needs a model? | No | Yes (your IDE/CI agent) |
| Cost / speed | Free, milliseconds, reproducible | A few cents, seconds, non-deterministic |
| Where | pre-commit hook, CI/PR check, any pipeline | in an IDE session, or headless (`claude -p`, Ollama, …) |

**Rule of thumb:** deterministic everywhere as the backstop; run the model-assisted check
**during code review** (interactively or in a CI agent) — never inside the local pre-commit
hook (an LLM per commit is slow, and hooks over ~5s get bypassed). See
[ADR-0006](../architecture/decisions/0006-opt-in-ci-freshness-gate.md).

---

## Layer 1 — Deterministic (recap)

This is the built-in `doctyze watch` check. It matches changed files against each doc's
`affects:` anchor.

```bash
# local (uncommitted changes)
doctyze watch

# CI / PR — MUST pass --base so committed changes are seen (fetch full history)
doctyze watch --base "origin/$TARGET_BRANCH"              # warn-only (report)
doctyze watch --base "origin/$TARGET_BRANCH" --exit-code  # gate the merge
```

It tells you *which docs to re-examine*. It does **not** judge whether a doc is actually
correct/complete — that's Layer 2.

---

## Layer 2 — Model-assisted drift check (when an agent is wired)

The model answers the three questions the deterministic layer can't. Feed it **only the
changed files + the affected docs** (scope it with Layer 1 first) so it stays cheap.

### A. Inside an IDE agent (Claude Code, Cursor, …)

1. Scope it: `doctyze watch --base "origin/$TARGET_BRANCH"` → note the flagged docs.
2. Either:
   - **Regenerate directly** — invoke `/doctyze` (it re-reads the current code and rewrites
     the flagged docs), **or**
   - **Just audit drift** — paste the [reference prompt](#reference-prompt) with your diff and
     the flagged docs, and let the agent report before you regenerate.

### B. Headless (a git hook or CI step, using the agent you already have)

Claude Code's non-interactive mode uses your **existing login** (no separate API key needed
outside `--bare`), and user-invoked skills work in `-p` mode:

```bash
# report drift over a PR, as JSON your script can gate on
git diff "origin/$TARGET_BRANCH"... | \
  claude -p "$(cat drift-prompt.txt)" --output-format json
```

Prefer a **local, no-key** model? Send the staged/PR diff to Ollama (e.g. a small `qwen`
model) instead — same prompt, `ollama run <model>`.

> Keep this **opt-in and out of the local pre-commit hook.** Put it in code review or a CI
> job. The deterministic Layer 1 stays the fast default.

### Reference prompt

Copy this, fill in the diff and the docs, and hand it to your agent (`/doctyze` context,
`claude -p`, or a local model):

```text
You are auditing documentation drift for a code change.

INPUTS
- CHANGED CODE: <the diff, or the list of changed files + their current contents>
- CANDIDATE DOCS: <the docs flagged by `doctyze watch`, with their contents>

For the functionality touched by this change, classify into exactly these buckets and cite
file:line:

1. DOCUMENTED & ACCURATE   — behavior is covered and still correct. (no action)
2. DOCUMENTED BUT DRIFTED  — a doc describes this area but no longer matches the code.
                             → name the doc(s) to regenerate.
3. NET-NEW & UNDOCUMENTED  — new behavior no doc covers.
                             → name where a spec/section should be added.

Be specific and grounded in the code; do not invent behavior. Output the three lists only.
```

The agent's output tells you what to do; **regeneration is still a generation step** — run
`/doctyze` (or the relevant `write-*` skill) to rewrite the drifted docs and add the missing
ones. Neither layer edits prose on its own.

---

## Guidelines (summary)

- **Always** run Layer 1 (deterministic) — locally (warn-only hook) and in CI/PR. It's the
  free, reproducible backstop and it scopes Layer 2.
- **Run Layer 2 during model-based review**, not on every local commit. In an IDE, `/doctyze`
  or the reference prompt; headless, `claude -p` (existing login) or a local Ollama model.
- **Feed the model only what changed + the flagged docs** — cheap and focused.
- **Fix by regenerating** with `/doctyze`; the checks flag, the model writes.
- Keep `affects:` anchors **narrow**, or Layer 1 gets noisy and Layer 2 gets over-scoped.

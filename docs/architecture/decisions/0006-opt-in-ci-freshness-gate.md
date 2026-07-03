# ADR-0006: Freshness Enforcement Is Opt-In in CI; Local Stays Warn-First

**Status:** 🟢 ACCEPTED
**Date:** 2026-07-03
**Deciders:** Rohit Mangal
**Amends:** [ADR-0004](./0004-warn-first-not-enforced.md)

## Context

[ADR-0004](./0004-warn-first-not-enforced.md) established that Doctyze is **warn-first** and
never blocks. In practice that made Doctyze warn-only *everywhere*, including its GitHub
Action ([`action.yml`](../../../action.yml)), which ran `doctyze watch` — a command that
always exits 0. So a team that *wanted* to treat stale docs as a merge gate had no supported
way to do it: they'd have to grep the tool's output and `exit 1` themselves, outside
Doctyze's surface.

At the same time, staleness is the single biggest risk to Doctyze's value: a stale doc
silently feeds an agent (or human) wrong context, which is worse than no doc. A pure
warn-only posture *reports* drift but gives it no teeth, so drift accumulates if the team
ignores the warning.

The question: should Doctyze support *blocking* on stale docs, and if so, where?

## Decision

**Enforcement is opt-in and lives in CI, never in the local commit.**

- **Local pre-commit hook stays warn-only** (unchanged from ADR-0004). The hook still runs
  `doctyze watch --staged || true; exit 0` and does **not** pass `--exit-code`.
- **`doctyze watch` gains an opt-in `--exit-code` flag** that exits non-zero when docs are
  stale. Default remains exit 0 (warn-first).
- **The gate is a CLI primitive, so it is CI-agnostic.** `doctyze watch --exit-code` runs in
  any CI (GitHub, GitLab, Jenkins, CircleCI, Azure…). The **GitHub Action is only a
  convenience wrapper** — it does not make the feature GitHub-only. Non-GitHub CIs call the
  CLI directly.
- **`watch` gains a `--base <ref>` option, required for CI correctness.** A CI checkout is
  clean (the change is already committed), so the default working-tree diff sees nothing and
  the check would silently pass. `--base origin/<target-branch>` diffs the PR against its base
  so committed changes are detected. This needs full git history (e.g. `fetch-depth: 0`). The
  GitHub Action exposes `base` and `fail-on-stale` inputs; the team owns branch protection,
  Doctyze owns the failing exit.

## Rationale

1. **A pre-commit hook cannot regenerate a doc.** Regeneration needs the model (BYO-agent),
   which a deterministic hook can't invoke. Blocking the local commit therefore strands the
   developer with no in-context fix, and the real-world result is habitual `--no-verify` —
   training people to bypass *every* hook. Blocking locally produces bypasses, not fresh docs.
2. **The merge is the right thing to gate.** A CI check blocks the *shared artifact* (what
   lands on the main branch), not a private commit. It doesn't interrupt anyone mid-thought,
   it's reviewable, and a human can dismiss a false positive. This is exactly the "opt-in,
   wire into your own CI" path ADR-0004 anticipated.
3. **Opt-in preserves the default.** Warn-first stays the default at every layer; teams that
   want a gate choose it explicitly. No behavior changes for anyone who doesn't opt in.

## Consequences

- **Positive:** teams can now make freshness a merge requirement *through Doctyze* (no
  bespoke scripting); the local developer experience is untouched; the default honors ADR-0004.
- **Tradeoff — depends on anchor discipline.** A CI gate is only tolerable if `affects:`
  anchors are **narrow** (the exact files a doc describes). Broad anchors make every PR
  "stale," the check screams constantly, and someone disables it. So the gate is recommended
  *only* for repos that keep anchors tight. This is documented as best practice, not forced.

## Best Practice (documented for users)

- **Default / most repos:** warn-first everywhere — local hook + CI reporting with
  `--base` but no `--exit-code`. Treat the warning as a prompt to run `/doctyze` and
  regenerate the flagged docs.
- **Teams that treat docs as a contract:** add `--exit-code` (Action: `fail-on-stale: true`)
  and mark the check required — *after* confirming anchors are narrow. Keep the local hook
  warn-only.
- **Always set `--base` and fetch full history in CI**, or the check silently passes (a
  clean checkout has no working-tree diff). This is the most common misconfiguration.
- Never make the **local** commit blocking; it can't regenerate and it trains bypasses.

## Related ADRs

- [ADR-0004: Warn-First — Doctyze Does Not Enforce Doc Writes](./0004-warn-first-not-enforced.md)
  — this ADR amends it: local stays warn-first, but CI enforcement is now an explicit opt-in.
- [ADR-0003: Pivot to a Repo Context-Layer Generator](./0003-pivot-to-context-layer-generator.md)
  — the BYO-agent model that makes "a hook can't regenerate" true.

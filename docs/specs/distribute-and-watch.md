---
doctyze:
  artifact: spec
  generated_by: write-spec
  source: [doctyze/distribute/, doctyze/freshness/]
  affects: [doctyze/distribute/**, doctyze/freshness/**]
  last_verified: '2026-06-15'
---

# Spec: Distribute & Watch (freshness)

## Distribute

**Purpose.** Make the canonical Doctyze skills available to whatever agent the developer uses.

**CLI.** `doctyze distribute [PATH]`.

**Behavior** ([`fanout.py`](../../doctyze/distribute/fanout.py)) — read the canonical skills from `doctyze/skills/<name>/SKILL.md` and write each to `.claude/skills/<name>/SKILL.md` and `.cursor/rules/<name>.md`, then maintain a `<!-- doctyze:start -->…<!-- doctyze:end -->` block in `AGENTS.md`. Idempotent (the AGENTS.md block is replaced, never duplicated). `ruler` may be used instead when present; the built-in fan-out is the default.

## Watch (the affected-docs detector)

**Purpose.** When code changes, flag the docs it makes stale. This is Doctyze's core primitive.

**CLI.** `doctyze watch [--install] [--staged] [PATH]` — warn-first; never blocks.

**Behavior** ([`detect.py`](../../doctyze/freshness/detect.py)):
1. `changed_files` — `git diff --name-only` (vs `HEAD`, or `--cached` for the hook).
2. `find_stale` — for every doc carrying a `doctyze:` anchor, match its `affects` globs (supporting `**`) against the changed files; matches are stale.
3. `write_refresh_manifest` ([`regenerate.py`](../../doctyze/freshness/regenerate.py)) — record each stale doc + the skill that regenerates it in `.doctyze/refresh-needed.md`. The agent does the actual rewriting.
4. `--install` ([`hook.py`](../../doctyze/freshness/hook.py)) — write a warn-first `.git/hooks/pre-commit` that runs `doctyze watch --staged`.

## Edge cases
- A non-git repo → `changed_files` returns empty; `--install` reports "not a git repo".
- Docs without an anchor (or with empty `affects`) are never flagged.
- Glob matching: `**` crosses directories, `*` does not.

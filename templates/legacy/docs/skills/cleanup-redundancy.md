---
name: cleanup-redundancy
description: Apply on every change that touches a file, function, folder, or path. Whenever something is added, replaced, or refactored, the corresponding now-redundant logic, files, and folders must be removed in the same change. Never leave commented-out code or empty placeholder directories behind.
---

# Always clean up redundant logic, files, and folders

## When to apply

Any change that:

- Replaces a function, module, or class with a new implementation
- Refactors a directory layout (canonical-source-of-truth move,
  monorepo split, etc.)
- Removes a vendor target, feature flag, or configuration option
- Renames a file, folder, or symbol
- Supersedes a pattern (e.g., a v2 of an extractor replacing v1)

If the change introduces a new way of doing something, the old way must go
in the same PR. Not "later." Not "after a deprecation window." Same PR.

## What "clean up" includes

1. **Delete dead code.** Functions, parameters, branches, and imports that
   the new code path no longer reaches.
2. **Delete redundant files.** Old implementations, prior-format templates,
   superseded migrations, duplicate canonical sources.
3. **Delete empty placeholder directories.** If a directory exists for
   "future" content, either populate it in this PR or delete it. Git does
   not track empty directories, and they signal "abandoned" to every reader.
4. **Delete commented-out code.** Git remembers; the file does not need to.
5. **Update every place that referenced the deleted thing.** README diagrams,
   AGENTS.md, other modules' imports, configuration examples, blog post links,
   external docs site. If a name appears in the codebase, it must still exist
   after this PR.
6. **Remove unused dependencies.** If you removed the only consumer of a
   package, drop it from `pyproject.toml` / `package.json` / `requirements.txt`.

## What clean up is NOT

- **Not "let's keep it for reference."** Reference lives in git history.
- **Not "what if someone still uses it."** If it's in this repo, you're the
  someone. If it's not used here, delete it; downstream consumers should pin
  versions, not rely on an unused file remaining.
- **Not "deprecate first."** Deprecations matter for *public APIs across
  release boundaries*. Internal refactors do not need deprecation cycles.

## Concrete checklist before opening the PR

- [ ] No commented-out code blocks introduced or left behind
- [ ] No empty directories anywhere under the project root
  (verify: `find . -type d -empty -not -path './.git/*'`)
- [ ] No dead parameters, kwargs, or struct fields that nothing reads
- [ ] No duplicated content (two files saying the same thing in two formats
  — pick the canonical, generate the rest, see also `write-adr` for when a
  duplicate is intentional and how it should be documented)
- [ ] All `import` statements in changed modules are used by at least one
  line in that module
- [ ] All README diagrams, AGENTS.md sections, and `.doctyze.yaml` examples
  reflect the post-change layout
- [ ] `grep -r '<deleted-symbol-name>' .` returns zero hits

## Why this is enforced

Cruft compounds. A repository with empty directories, dead parameters, and
two ways to do the same thing teaches readers — human and AI — that the
codebase doesn't have one correct path. AI coding agents in particular
will *find* dead code, assume it's authoritative, and "fix" or extend it.
Every line of redundancy is a future incident waiting to happen.

The Doctyze PR review GitHub Action will flag suspected cruft:

- Empty directories introduced in a diff
- Parameters added but never referenced inside the function body
- Imports introduced but unused
- Content that was duplicated rather than rendered from canonical sources

These are warnings by default. Set `pr_review.mode: block-required` in
`.doctyze.yaml` to enforce them as merge gates.

## Anti-patterns

- **"We'll clean it up in the next sprint."** It will not get cleaned up.
  Plan for the cleanup as part of the change.
- **"It's behind a feature flag."** Feature flags are for the *new* code,
  not for keeping the old code alive forever. When the flag flips on
  permanently, delete the old branch.
- **"Tests still reference the old API."** Then update the tests in the
  same PR. The change is not done until the tests reflect reality.
- **"I'm not sure what else uses it."** That's what grep is for. Run it
  before deleting; run it after to confirm no straggler references remain.

## For AI coding agents

If you're modifying this repo, the cleanup rule applies to your work too.
After making any non-trivial change:

1. Run `find . -type d -empty -not -path './.git/*'` and delete any
   empty directories your change introduced.
2. Grep for references to anything you removed; remove the stragglers.
3. Confirm imports in modified files are all live.
4. Update the README, AGENTS.md, and any `.doctyze.yaml` examples that
   mentioned the now-removed thing.

Do not commit a change that leaves the repo in a "two ways to do this"
state. Pick one. Document the choice if it's non-obvious (write an ADR).
Delete the other.

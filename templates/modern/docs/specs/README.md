# Specifications

Feature specifications in [GitHub Spec Kit](https://github.com/github/spec-kit)
format. One directory per feature, numbered sequentially.

Each spec has three files:

- **`spec.md`** — *what* and *why* (the requirement)
- **`plan.md`** — *how* (the architectural approach)
- **`tasks.md`** — *breakdown* (the work items)

## Active specs

🔴 GAP — no specs authored yet. Add the first one when you implement
the next feature: `mkdir 001-<feature-slug>` then `doctyze spec init`.

## Conventions

- Folder name pattern: `NNN-<kebab-case-slug>/` where NNN is a
  zero-padded sequence number.
- `spec.md` must include a `## Requirements` section listing
  `REQ-NNN` identifiers — these are referenced from ADRs and runbooks
  for traceability.
- A spec moves from `proposed → in-progress → completed`. State is
  documented in the spec's frontmatter.

## How specs interact with Doctyze

The PR review GitHub Action checks that any PR touching code described
by an active spec also updates the spec's `tasks.md` to reflect what
was actually done. This prevents specs from drifting into fiction.

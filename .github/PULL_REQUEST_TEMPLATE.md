<!-- Thanks for the PR! A few quick checks help us merge faster. -->

## What does this PR do?

<!-- One or two sentences. Link the issue it closes: "Closes #NNN" -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] New renderer (for an AI tool)
- [ ] Refactor / cleanup
- [ ] Test / CI
- [ ] Other:

## Doctyze contributor checklist

The cleanup rule applies (see [`docs/skills/cleanup-redundancy.md`](../docs/skills/cleanup-redundancy.md)).
Before requesting review:

- [ ] `find . -type d -empty -not -path './.git/*'` returns nothing
- [ ] No commented-out code introduced
- [ ] No dead parameters / unused imports
- [ ] No duplicate canonical sources (canonical lives once → renderers emit vendor variants)
- [ ] If I added/changed behavior the docs describe, I updated the docs in the same PR
- [ ] If I made an architectural choice, I wrote an ADR (see [`docs/skills/check-and-update-adrs.md`](../docs/skills/check-and-update-adrs.md))
- [ ] `pytest` passes locally
- [ ] `doctyze render --check` passes on the worked example
- [ ] The CI badge will be green when this merges

## Anything else?

<!-- Screenshots, related discussion links, reviewer hints, follow-up issues you'd open after this merges. -->

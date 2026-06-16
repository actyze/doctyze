<!-- Thanks for the PR! A few quick checks help us merge faster. -->

## What does this PR do?

<!-- One or two sentences. Link the issue it closes: "Closes #NNN" -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] New / updated skill
- [ ] Documentation
- [ ] Refactor / cleanup
- [ ] Test / CI
- [ ] Other:

## Doctyze contributor checklist

The cleanup rule applies (see `CONTRIBUTING.md`). Before requesting review:

- [ ] `find . -type d -empty -not -path './.git/*'` returns nothing
- [ ] No commented-out code introduced
- [ ] No dead parameters / unused imports
- [ ] No duplicated content (a fact/taxonomy lives in one place; derive the rest)
- [ ] If I changed a skill, I ran `scripts/sync-plugin-skills.sh`
- [ ] If I changed behavior the docs describe, I updated the docs in the same PR
- [ ] If I made an architectural choice, I added an ADR under `docs/architecture/decisions/`
- [ ] `pytest` passes locally
- [ ] **No LLM SDK dependency added** (Doctyze is BYO-agent)

## Anything else?

<!-- Screenshots, related discussion links, reviewer hints, follow-up issues. -->

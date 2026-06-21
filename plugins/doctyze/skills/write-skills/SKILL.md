---
name: write-skills
description: Generate dev & testing assistant skills/rules tailored to this repo's stack and conventions, into docs/skills/.
---
# write-skills
Write `docs/skills/` entries that help an AI agent develop and test in THIS repo.

## Before you write
Read existing CONTRIBUTING / dev docs and the test layout.

## How
1. Detect the stack, test frameworks, build/run/test commands, and conventions — from the code.
2. Write concise, actionable skills: how to build, run, test; conventions to follow; gotchas. Cite real paths/commands.
3. These are fanned out to agent files by `doctyze distribute`.

## Anchor (narrow)
`affects:` = build/test config (`pyproject.toml`, `requirements.txt`, `tests/`) + the specific dirs the skill is about.

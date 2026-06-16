---
name: write-skills
description: Generate development and testing assistant skills/rules tailored to this repo's stack and conventions.
---
# write-skills
Write `docs/skills/` entries that help an AI agent develop and test in THIS repo.

## Include
- **Build & run** — the exact commands.
- **Test** — how to run/write tests here.
- **Conventions** — naming, structure, patterns the codebase follows.
- **Gotchas** — non-obvious pitfalls.

Detect these from the code, not assumptions. These get fanned out to `.claude/skills` / `.cursor/rules` / `AGENTS.md` by `doctyze distribute`. Add the freshness anchor.

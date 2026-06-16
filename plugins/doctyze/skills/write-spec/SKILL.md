---
name: write-spec
description: Reverse-engineer a feature/capability specification from the code, one file per capability, into docs/specs/.
---
# write-spec
Write `docs/specs/<capability>.md` — one file per major capability.

## Sections (use these)
- **Purpose** — what the capability does, in one or two lines.
- **Interface** — the CLI/API/entry points (commands, endpoints, functions).
- **Behavior** — the real steps/logic, **citing source paths** (link to the files).
- **Inputs / Outputs** — what it consumes and produces.
- **Edge cases** — error handling, empty/idempotent/limits, known limitations.

## Rules
- Ground every statement in code that exists. Do NOT describe intended-but-absent behavior. Link to source files.
- One capability per file; keep it verifiable, not marketing.

## Anchor (required) — scope `affects` to THIS capability's code
```yaml
---
doctyze:
  artifact: spec
  generated_by: write-spec
  source: [src/<area>/]
  affects: [src/<area>/**]   # globs for the exact code this spec describes — precise = good freshness
  last_verified: <YYYY-MM-DD>
---
```

# Investigations

Postmortems, root-cause analyses, and deep-dive engineering investigations.

## Conventions

- One file per investigation.
- Filename: `YYYY-MM-DD-<kebab-case-slug>.md`.
- Each investigation must end with a **Triage updates required** section.
  If the investigation reveals a missing runbook, missing ADR, or stale
  doc, that update lands in the same PR as the investigation.

## Template

```markdown
# YYYY-MM-DD — <title>

- Severity: sev0 | sev1 | sev2 | sev3
- Duration:
- Customer impact:
- Linked requirement(s): REQ-NNN
- Linked ADR(s): ADR-NNNN

## What happened
## Timeline
## Root cause
## Contributing factors
## What went well
## What didn't
## Action items
## Triage updates required (mandatory before close)
- [ ] Runbook updated / new runbook added
- [ ] ADR added / superseded
- [ ] Skill added or updated in .claude/skills/
- [ ] PR link:
```

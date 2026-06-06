---
name: interview-prep-adr
description: Use when preparing for a senior-engineer interview to capture rationale on a legacy decision marked 🔴 GAP. Turns Doctyze-detected gaps into structured interview questions and stores the resulting answers as ADRs.
---

# Interview-augmented ADR archaeology (legacy stack)

## When to apply

Activate this skill when:

- A 🔴 GAP marker exists somewhere in `docs/` (Doctyze couldn't extract the rationale from code)
- A senior engineer who knew the system is available for an interview
- The system is in `migrating` or `eol` lifecycle phase (time-bounded urgency)

This is the **load-bearing skill for legacy stack adoption**. Code archaeology
recovers ~60% of intent; the remaining 40% requires interviews.

## Workflow

### 1. Identify gaps to address in this interview

Open `docs/investigations/adr-archaeology/pending-questions.md`. Pick the
top 3–5 questions for a single 60-minute session. Don't try to cover
everything in one sitting — schedule follow-ups.

Prioritize:
1. Questions about decisions that are blocking modernization plans
2. Questions where the senior engineer is closest to retirement
3. Questions about systems no other team member knows

### 2. Prepare context for the engineer

Before the meeting, share:
- The relevant files / programs the question is about
- Any patterns Doctyze observed (so they can confirm/correct)
- A 1–2 sentence framing of why this matters

### 3. Conduct the interview

Use open-ended questions, in this order:

1. **What problem were you solving?** (context)
2. **What did you choose, and what other options were on the table?** (decision + alternatives)
3. **Why this over the others?** (rationale — the load-bearing answer)
4. **What was the consequence — good and bad?** (what followed)
5. **What would you do differently today?** (modernization input)

Record the session (with permission). Verbatim notes are gold.

### 4. Capture as an ADR

Create `docs/investigations/adr-archaeology/INTERVIEW-NNN-<topic>.md`
with the raw notes. Then derive a formal ADR at
`docs/architecture/decisions/NNNN-<topic>.md` using the standard MADR
format.

Flip the original 🔴 GAP marker to 🟢 CONFIRMED in the file it was in.

## Anti-patterns

- ❌ **Asking the engineer to write the ADR themselves.** They won't.
  You take the notes and draft; they review and correct.
- ❌ **Leading questions.** "You used Oracle because of strong consistency, right?"
  is worse than silence. Let them tell you why.
- ❌ **Treating one interview as authoritative.** Cross-check with at least
  one other source (commit history, ticket archives, other senior eng).
- ❌ **Skipping the "what would you do differently" question.** This is
  the most valuable modernization input you'll get.

## Doctyze enforcement

When a PR moves a 🔴 GAP marker to 🟢 CONFIRMED, the bot:
- Verifies a corresponding `INTERVIEW-NNN-*.md` file exists
- Verifies the formal ADR was created
- Confirms the citation matches (so a future reader can find the source)

If you mark a GAP as confirmed without doing the interview, the bot
blocks the PR with a `# doctyze: confirmation-requires-source` comment.

## Time-bounded note

Every engineer who retires takes ADRs you'll never recover with them.
If you have anyone with >15 years on a legacy system, prioritize their
interview slots. This skill exists to make those sessions productive.

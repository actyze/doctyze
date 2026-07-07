# Why Doctyze

The short version: **documentation is the one artifact every team agrees it needs and almost none keep
accurate — because nothing tells you when it goes wrong.** Doctyze generates the docs a repo is missing
and makes staleness a signal you can act on, using the AI already in your editor. This page makes the
full case.

---

## The problem: missing, stale, or scattered — usually all three

Open a random repository and its documentation is in one of three states, often simultaneously:

- **Missing.** The code works; the *why* lives in three people's heads and a closed Slack thread. There's
  a README, maybe, and nothing that explains the architecture, the decisions, the operational reality.
- **Stale.** Docs existed once. Then the code moved and the docs didn't. The spec describes last quarter's
  behavior; an ADR's assumptions no longer hold; the runbook points at a service that was renamed. Nobody
  *decided* to let them drift — it just happened.
- **Scattered.** What does exist is spread across a wiki, a `docs/` folder, design files, and PR
  descriptions, with no canonical source and three contradictory answers to the same question.

None of this is a discipline problem. Teams that care deeply still end up here, because the forces are
structural: writing docs is work that ships no feature, and keeping them current is work with **no
feedback loop.** Which brings us to the real reason.

## Why it never gets fixed: docs rot *silently*

Every other kind of quality problem announces itself. A failing test goes red. A type error blocks the
build. A broken endpoint pages someone. Stale documentation makes **no sound at all.** You change
a function, the doc that described it is now wrong, and nothing — not CI, not the reviewer, not the next
reader — knows it happened. The doc and the code diverge in silence, and the gap only surfaces when someone is
already burned by it.

So teams land on one of two losing strategies: audit the docs **never** (and accept that they're
untrustworthy), or audit them **all at once** in a doc-sprint that's obsolete the day it ends. Neither
works, because both fight entropy with willpower.

## Where the cost actually lands

Silent doc-rot doesn't hurt evenly — it hits at the highest-leverage, worst-possible moments:

- **Onboarding.** A new hire or contractor reads a confident, wrong spec and builds a mental model that
  takes weeks to correct. The docs actively *mislead* — worse than having none.
- **Incidents.** The runbook is the one doc you cannot afford to be stale, and it's often the stalest,
  because ops config changes constantly and nobody re-reads the runbook until 3 a.m.
- **Code review.** A reviewer can't tell whether a change matches intent, because the doc of record for
  that intent is out of date. Review degrades to "does it compile and look plausible."
- **Every future change.** The longer docs and code diverge, the more expensive reconciliation becomes —
  classic compounding debt.

And now there's a fourth victim, and it's the one changing the stakes.

## Why it matters more now: the AI-agent era

Your IDE's AI agent — Cursor, Claude Code, Copilot — is only as good as the context it's given. Point it
at a task and it does exactly what a new hire does: it reads the repo to infer intent. If the docs are
missing, it infers from code alone and misses the *why*, the constraints, and the decisions that aren't
visible in any single file. If the docs are **stale**, it does something worse — it reads them, trusts
them, and produces confidently wrong code, at machine speed, across your whole codebase.

The industry's answer is a **context layer**: `AGENTS.md`, editor rules, MCP servers — a maintained,
agent-readable description of the repo. But that just relocates the original problem. *Someone has to
write that context, and keep it current.* A hand-written `AGENTS.md` rots exactly like every other doc —
now with the added failure mode that a machine acts on it.

This is the shift: documentation used to be a human convenience. In an agent-driven workflow it's
**load-bearing infrastructure** — the difference between an agent that understands your system and one
that guesses. Grounded, maintained context in means better code out. Stale context in means
plausible-but-wrong out. Doctyze exists to make that context layer real *and* keep it honest.

## What Doctyze does about it

Doctyze attacks the root cause — the missing feedback loop — with one primitive and one principle.

**The primitive: every doc declares the code it covers.** Each generated doc carries a small frontmatter
anchor:

```yaml
doctyze:
  affects: [src/payments/refund.py]
```

Now staleness is *computable*. A plain `git diff` against those anchors names the **exact** docs a change
invalidated — deterministically, with no model and no guesswork. Doc-rot stops being silent; it becomes a
signal, like a failing test. You regenerate the specific docs a change touched, not the whole tree, and
you always know whether a given doc is current.

**The principle: bring your own agent.** Doctyze never calls an LLM itself and never asks for a key. The
prose is written by the model *already in your IDE*; the Python engine only does the deterministic
mechanics (scaffolding, consolidation, and the `git diff` freshness check). No API key, no vendor model,
no hosted service, no code leaving your machine.

Put together, one command generates the docs a repo never had — feature specs, architecture + Mermaid
diagrams, ADRs, runbooks, observability, dev/testing skills — straight into `docs/`, and fans them out to
`AGENTS.md` / Cursor rules / Claude Code skills so both people and agents inherit them.

## What you get

- **Docs that exist** — for the repos that never had them, generated from the actual code in one pass.
- **Docs you can trust** — because a `git diff` tells you which are stale, "are these even accurate?" stops
  being a question. Freshness is verified, not hoped for.
- **Surgical maintenance** — regenerate only the docs a change actually touched, instead of never or
  all-at-once.
- **An agent that stops guessing** — the same docs become the context layer your IDE agent reads, so it
  works from a maintained map of the repo instead of inferring intent from code.
- **Faster, safer onboarding** — new people (and reviewers) get accurate specs, architecture, and runbooks
  instead of tribal knowledge.
- **No new dependency or cost** — Apache-2.0, BYO-agent, plain Markdown in your repo. Nothing to buy,
  nothing to host, nothing to leak.

## Who it's for

- **The team with no docs and no time** — get a real `docs/` tree from one command instead of a doc-sprint
  that never happens.
- **The team drowning in doc-rot** — docs exist but nobody trusts them; the freshness anchors make trust
  computable again.
- **Anyone adopting AI coding agents** — you need a context layer; Doctyze generates and *maintains* one
  instead of leaving you a hand-written `AGENTS.md` to rot.
- **Whoever inherited the legacy service** — point Doctyze at an undocumented Spring/Rails/whatever service
  and get the full operational + architectural picture. (See the
  [Spring PetClinic full-suite example](../examples/petclinic/).)
- **OSS maintainers** — give contributors and their agents grounded docs, reproducibly, with provenance.

## Why this approach specifically

- **Deterministic where it counts.** The freshness check is a `git diff`, not an LLM judgment — reproducible,
  CI-safe, and free of the flakiness that makes model-based drift detection untrustworthy as a gate.
- **In-repo, not hosted.** The docs are plain Markdown committed alongside the code, versioned with it,
  diffable in review — not a separate website or wiki that drifts on its own timeline.
- **No lock-in.** BYO-agent means no key, no vendor model, no data egress; drop Doctyze and you keep every
  doc it wrote.

## What Doctyze is *not*

Being honest about the boundary is part of why you can trust the rest:

- **Not a hosted docs website** (that's Mintlify) — it writes in-repo Markdown, not a customer-facing site.
- **Not a browsable wiki + Q&A** (that's DeepWiki) — it produces a canonical `docs/` tree with a freshness
  loop, not a read-only index.
- **Not a source of external-library docs** (that's Context7) — it documents *your* repo, not your
  dependencies.
- **Not a paid CI bot** running its own model on every PR (that's Dosu / DeepDocs) — it defers generation
  to the agent you already have.
- **Not magic.** Output quality rides on the model in your IDE, and the freshness anchors are only as tight
  as they're written. It removes the *silence* from doc-rot; it doesn't remove the need to care.

See the [comparison table](../README.md#how-doctyze-compares) for where Doctyze sits in the landscape, and
the [examples gallery](../examples/) for real `docs/` trees it generated on click, cobra, hono, and a
full-suite Spring service.

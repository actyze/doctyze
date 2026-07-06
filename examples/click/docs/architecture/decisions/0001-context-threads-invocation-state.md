---
doctyze:
  artifact: adr
  generated_by: write-adr
  affects: [src/click/core.py, src/click/globals.py, src/click/decorators.py]
  last_verified: 2026-07-05
---
# ADR-0001: A per-command Context object threads invocation state through nested commands

**Status:** 🟢 ACCEPTED (reverse-engineered from the code — describes Click's existing design)
**Date:** 2026-07-05
**Deciders:** Click maintainers (inferred)

> Reverse-engineered by Doctyze from the code as a demonstration of the `write-adr` skill. It documents
> a decision Click already embodies; it is not a proposal to change Click.

## Context

A CLI built with Click is a tree of commands (`app db migrate`). Deeply nested subcommands routinely need
shared, invocation-scoped state: an opened config, a DB connection, a `--verbose` flag set on the root
group, resources that must be cleaned up when the program exits. The design question: **how does a
subcommand's callback reach state established by an ancestor command, without threading it through every
function signature by hand?**

## Decision

Click gives **each invoked command its own `Context`** ([`core.py:204`](../../../src/click/core.py)),
linked to its parent by `Context.parent`. The `Context`:

- carries the parsed `params`, a user-controlled `obj`, and a free-form `meta` dict;
- forms a linked list from the current command up to the root, so an ancestor's `obj`/`meta` is reachable
  from any descendant;
- is exposed to callbacks explicitly via `@pass_context` / `@pass_obj` / `make_pass_decorator`
  ([`decorators.py:28`](../../../src/click/decorators.py)), and implicitly via the thread-local
  `get_current_context()` ([`globals.py`](../../../src/click/globals.py));
- acts as a resource scope — e.g. `File` handles opened during conversion are closed on teardown.

## Rationale

1. **Explicit over global.** State lives on an object passed (or fetched) deliberately, not in module
   globals — subcommands stay testable and reentrant.
2. **Composition.** Because `Context.parent` is a simple link, arbitrarily deep command trees share state
   with no per-level plumbing; a group sets `ctx.obj` once and every child sees it.
3. **Lifecycle.** Tying resource cleanup to `Context` teardown means the same object that *holds* state
   also *bounds* it, so files/handles don't leak across a multi-command (`chain`) run.

## Consequences

- **Positive:** clean nested-state sharing (`ensure_object`, `obj`, `meta`), deterministic cleanup, and
  a testing seam (`CliRunner` can inspect the context tree).
- **Tradeoff:** two ways to obtain the context (explicit `@pass_context` vs. the `get_current_context()`
  thread-local) — flexible, but the thread-local path is easy to overuse and couples code to "being
  inside a Click invocation."
- **Constraint:** the thread-local assumes one active invocation per thread; concurrent invocations must
  not share a thread.

## Related
- [Architecture overview](../overview.md) · [Command & group model](../../specs/command-and-group-model.md)

# ADR-0007: Use Graphify's Code-AST Graph for Transitive Affected-Docs; Semantic Doc-Links Stay Advisory

**Status:** 🟡 PROPOSED
**Date:** 2026-07-05
**Deciders:** Rohit Mangal
**Relates to:** [ADR-0003](./0003-pivot-to-context-layer-generator.md), [ADR-0004](./0004-warn-first-not-enforced.md), [ADR-0006](./0006-opt-in-ci-freshness-gate.md)

## Context

Doctyze's affected-docs primitive is the wedge: given a code change, flag the *specific* docs it made
stale. Today ([`doctyze/freshness/detect.py`](../../../doctyze/freshness/anchors.py),
[`anchors.py`](../../../doctyze/freshness/anchors.py)) each generated doc declares, in YAML frontmatter,
a hand-written `affects:` glob list; `find_stale()` runs `git diff --name-only` and does a literal
glob-vs-changed-path match. A changed path that matches a glob marks the doc stale.

This is deterministic, free, and needs no LLM — its virtues. But it has one structural hole:

- **Manual.** Someone authors and maintains the globs; they rot silently when a module moves or is renamed.
- **Coarse.** Granularity is a path glob (`src/payments/**`); it can't say "only `refund()` matters."
- **No transitive reachability (the real gap).** If `src/payments/x.py` imports `src/core/money.py` and you
  change `money.py`, **no payments doc is flagged** unless a doc happened to also declare `affects: [src/core/**]`.
  There is no dependency graph — only string matching on the *directly* changed paths.

[Graphify](https://github.com/Graphify-Labs/graphify) builds exactly the graph we lack: a deterministic,
multi-language (tree-sitter, 36 grammars) code-AST graph with structural edges (`imports`, `calls`,
`inherits`, …), plus doc/concept nodes and — verified against a shipped fixture — LLM-inferred cross-edges
from doc nodes to the code they describe (`implements` / `references`). It even ships a `graphify affected`
command (reverse-BFS impact over the code graph). The question: should Doctyze consume Graphify's
`graph.json` to close the transitivity gap, and if so, how far do we trust it?

## Decision

**Consume Graphify's deterministic code-AST subgraph for transitive reachability. Treat its LLM-inferred
doc↔code cross-links as advisory suggestions only — never as the CI freshness gate.**

1. **The deterministic backbone is the code AST graph, traversed in the impact (reverse) direction.**
   Impact analysis is *reverse-reachability*: dependents point *into* the changed node. To find what a
   change to `money.py` affects, walk `in_edges` over the code-dependency relations
   (`imports`, `imports_from`, `re_exports`, `calls`, `indirect_call`, `inherits`, `extends`, `implements`,
   `uses`, …) to build the "blast radius," then map those nodes back to docs. A *forward* (out-edge)
   closure would find `money.py`'s own dependencies instead — the opposite of what we need, and it would
   miss exactly the gap-#3 case. This slice is free, local, zero-LLM, and directly kills the transitivity gap.

2. **The semantic doc↔code cross-links are a probabilistic bonus layer, gated by confidence, never the gate.**
   Those edges are LLM-inferred (`INFERRED`/`AMBIGUOUS`, bimodal and un-thresholdable), exist only if the docs
   were graphified, and carry no guaranteed orientation — so they must be traversed *undirected* and surfaced
   only as ranked *suggestions* (or to auto-suggest `affects:` globs for human review). They augment
   `find_stale`; they do not replace it.

3. **The existing deterministic glob+diff match remains the source of truth for the CI gate** (ADR-0006).
   Graph-derived candidates are additive and advisory.

4. **Consume `graph.json` directly, not the `graphify affected` CLI.** `affected` does the reverse code walk
   correctly but never makes the doc hop (the cross-edges point code→doc, and it omits the pure doc-semantic
   relations). We own the traversal: reverse-BFS over code edges, then an undirected confidence-scored hop to
   `document`/`concept` nodes, mapping `source_file` (+ `§section`) back to the `.md`.

## Rationale

1. **It fills the one real hole without weakening the wedge.** The transitivity gap is the only structural
   weakness of the current mechanism, and Graphify's *deterministic* code graph fills it deterministically —
   no new LLM dependency in the load-bearing path.
2. **For a freshness tool, the fatal failure is a stale doc *not* flagged.** LLM-inferred recall can't be
   thresholded cleanly, so it can never be the sole staleness signal. Keeping it advisory preserves the
   guarantee that the gate is deterministic and reproducible (ADR-0006).
3. **Non-duplication (ADR-0003).** Doctyze does not build a graph; it borrows one. Graphify does not author
   docs; it borrows ours. Consuming `graph.json` is the "adopt-and-enhance" posture, not a rebuild.

## Consequences

- **Positive:** transitive affected-docs (the top requested capability) becomes possible; a Mode-B path can
  auto-suggest narrow `affects:` anchors (which ADR-0006 requires for the gate to be usable); optional richer
  discovery from the semantic layer.
- **Tradeoff — a new optional dependency and format coupling.** Graphify publishes no JSON Schema; we'd pin its
  NetworkX `node_link_data` shape (+ attached `hyperedges`) and budget for churn. This stays **optional** — the
  glob+diff path works with zero Graphify installed.
- **Cost/reproducibility.** Re-extracting the doc semantic pass costs LLM tokens per refresh and isn't stable
  run-to-run — so it must be cached and kept out of the gate, or the check flaps.

## Honest risks & open questions

- **False negatives are the killer** — hence the semantic layer is advisory-only.
- **Docs must be in the corpus.** A pure-code Graphify run yields zero doc edges; greenfield/unwritten docs are invisible.
- **Silent ghost nodes.** An ID-scheme mismatch produces an orphan duplicate with no cross-edge and no error.
- **Polyglot blind spots.** Graphify intentionally drops cross-language `calls` edges, so the deterministic
  blast radius under-reports across language boundaries.
- **Coarse line mapping.** `source_location` is a single declaration-line anchor, not a span; method-level
  staleness is a heuristic — fall back to file-level when unsure.

## Prototype (2026-07-05)

An experimental, **opt-in, additive** prototype of the deterministic backbone lives in
[`doctyze/graph/affected.py`](../../../doctyze/graph/affected.py) (stdlib-only, no networkx):
`load_graph()` normalizes Graphify's `node_link_data`; `code_blast_radius()` does the reverse-BFS over
code in-edges; `affected_docs()` adds the advisory, confidence-scored, undirected doc hop. It imports
nothing from the default freshness path and does **not** change the glob+diff gate. Covered by
[`tests/test_graph_affected.py`](../../../tests/test_graph_affected.py) (reverse reachability, the doc
hop, the direction-correctness case, and loader normalization) against
[`tests/fixtures/graphify_graph.json`](../../../tests/fixtures/graphify_graph.json). Wiring it into
`find_stale` (Mode A/B) remains future work, gated on this ADR being accepted.

## Related ADRs

- [ADR-0003: Pivot to a Repo Context-Layer Generator](./0003-pivot-to-context-layer-generator.md) — the adopt-and-enhance posture this applies.
- [ADR-0004: Warn-First](./0004-warn-first-not-enforced.md) & [ADR-0006: Opt-In CI Freshness Gate](./0006-opt-in-ci-freshness-gate.md) — why the deterministic match must remain the gate.

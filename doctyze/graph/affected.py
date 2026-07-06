"""Affected-docs via REVERSE code reachability over a Graphify ``graph.json``.

EXPERIMENTAL — this is the ADR-0007 prototype. It is **opt-in** and **additive**:
it is not wired into any command, nothing in the default freshness path imports
it, and it does **not** change the deterministic glob+diff staleness gate
(``doctyze/freshness/detect.py``). It exists to explore closing the transitive
reachability gap: if ``payments/x.py`` imports ``money.py`` and you change
``money.py``, the glob gate flags no payments doc; this walks the code graph to
find that ``payments/x.py`` (a *dependent* of ``money.py``) is affected, then hops
to the docs that describe it.

Pure Python, stdlib only (``json`` + our own BFS). No networkx dependency.

Direction is the whole point
----------------------------
Impact analysis is **reverse** reachability. Graphify's code edges are oriented
caller->callee / importer->imported (an edge ``A --imports--> B`` means A depends
on B). To find what a change to ``B`` *affects*, we must walk B's **in-edges** to
reach its dependents (A, and A's dependents, transitively). A *forward* (out-edge)
closure would instead find B's own dependencies — the WRONG answer.

Code->doc cross-edges are emitted with the code node as ``source`` and the doc
node as ``target``, so the doc hop is treated as **UNDIRECTED** (we look at both
in- and out-edges of a blast-radius node).
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Iterable, Iterator

# Deterministic code-dependency relations (edges: caller->callee / importer->imported).
# Reverse-BFS over these builds the code "blast radius".
CODE_RELATIONS = frozenset({
    "contains", "method", "imports", "imports_from", "re_exports",
    "calls", "indirect_call", "inherits", "extends", "implements",
    "uses", "mixes_in", "embeds", "references",
})

# LLM-inferred doc<->code semantic relations. ADVISORY ONLY — traversed undirected,
# surfaced as ranked suggestions, and never used as a gate (ADR-0007 §2).
DOC_RELATIONS = frozenset({
    "implements", "references", "cites", "conceptually_related_to",
    "shares_data_with", "semantically_similar_to", "rationale_for",
})

# Node file_types that count as documentation targets for the semantic hop.
DOC_FILE_TYPES = frozenset({"document", "paper", "concept", "rationale"})

CODE_FILE_TYPE = "code"


def _norm(path: object) -> str:
    """Normalize a path to forward slashes (matches freshness/detect.py)."""
    s = str(path).replace("\\", "/")
    if s.startswith("./"):
        s = s[2:]
    return s


def _confidence(edge: dict) -> float:
    """Edge ``confidence_score`` as a float; deterministic default 1.0 when absent."""
    v = edge.get("confidence_score")
    if v is None:
        return 1.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 1.0


def load_graph(path_or_dict: str | Path | dict) -> dict:
    """Parse a Graphify NetworkX ``node_link_data`` graph into indexed form.

    Accepts a path to a ``graph.json`` or an already-parsed dict. Normalizes the
    raw ``"edges"`` key to NetworkX's default ``"links"``, forces directed
    handling (impact analysis needs orientation), tolerates ``multigraph``, and
    indexes nodes both by ``id`` and by ``source_file`` — one file maps to MANY
    node ids (module/class/method nodes all share a ``source_file``).
    """
    if isinstance(path_or_dict, dict):
        data = path_or_dict
    elif isinstance(path_or_dict, (str, Path)):
        with open(path_or_dict, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    else:  # pragma: no cover - defensive
        raise TypeError(f"load_graph expects a path or dict, got {type(path_or_dict)!r}")

    nodes = list(data.get("nodes", []))
    # Normalize edges -> links: NetworkX default is "links"; raw Graphify may use "edges".
    raw_links = data.get("links")
    if raw_links is None:
        raw_links = data.get("edges", [])
    links = list(raw_links)

    graph: dict = {
        "directed": True,  # impact analysis is inherently directed; force it on
        "multigraph": bool(data.get("multigraph", False)),
        "graph": data.get("graph", {}),
        "nodes": nodes,
        "links": links,
        "nodes_by_id": {},
        "ids_by_source_file": {},
        "in_edges": {},
        "out_edges": {},
    }

    for node in nodes:
        nid = node.get("id")
        if nid is None:
            continue
        graph["nodes_by_id"][nid] = node
        source_file = node.get("source_file")
        if source_file:
            graph["ids_by_source_file"].setdefault(_norm(source_file), []).append(nid)

    for edge in links:
        src, tgt = edge.get("source"), edge.get("target")
        if src is None or tgt is None:
            continue
        graph["out_edges"].setdefault(src, []).append(edge)
        graph["in_edges"].setdefault(tgt, []).append(edge)

    return graph


def _seed_ids(graph: dict, changed_files: Iterable[str]) -> list:
    """Resolve changed file paths to CODE node ids via ``source_file``."""
    seeds: list = []
    seen: set = set()
    for changed in changed_files:
        for nid in graph["ids_by_source_file"].get(_norm(changed), ()):  # noqa: SIM118
            node = graph["nodes_by_id"].get(nid, {})
            if node.get("file_type") == CODE_FILE_TYPE and nid not in seen:
                seen.add(nid)
                seeds.append(nid)
    return seeds


def _reverse_reach(graph: dict, changed_files: Iterable[str]) -> dict:
    """Reverse-BFS over code in-edges. Returns ``{node_id: {hops, min_confidence}}``.

    Seeds are the changed code nodes (hops 0). Each step follows an *in-edge*
    whose relation is a code-dependency relation, moving to that edge's ``source``
    (the dependent). ``min_confidence`` is the minimum edge confidence along the
    discovered path (deterministic code edges default to 1.0).
    """
    reach: dict = {}
    queue: deque = deque()
    for seed in _seed_ids(graph, changed_files):
        if seed not in reach:
            reach[seed] = {"hops": 0, "min_confidence": 1.0}
            queue.append(seed)

    while queue:
        node_id = queue.popleft()
        current = reach[node_id]
        for edge in graph["in_edges"].get(node_id, ()):  # edges pointing INTO node_id
            if edge.get("relation") not in CODE_RELATIONS:
                continue
            dependent = edge.get("source")  # the node that DEPENDS on node_id
            if dependent is None or dependent not in graph["nodes_by_id"]:
                continue
            if dependent in reach:
                continue
            reach[dependent] = {
                "hops": current["hops"] + 1,
                "min_confidence": min(current["min_confidence"], _confidence(edge)),
            }
            queue.append(dependent)
    return reach


def code_blast_radius(graph: dict, changed_files: list[str]) -> set:
    """Node ids affected by a code change: the changed nodes + all transitive DEPENDENTS.

    Deterministic. Reverse-reachability over the code-dependency relations only —
    walking in-edges so we collect dependents, never dependencies.
    """
    return set(_reverse_reach(graph, changed_files).keys())


def _undirected_doc_edges(graph: dict, node_id) -> Iterator[tuple[dict, object]]:
    """Yield ``(edge, other_endpoint_id)`` for doc-semantic edges touching ``node_id``.

    Undirected: code->doc cross-edges have the code node as ``source``, so we must
    inspect both out- and in-edges to reach the doc on the other side.
    """
    for edge in graph["out_edges"].get(node_id, ()):
        if edge.get("relation") in DOC_RELATIONS:
            yield edge, edge.get("target")
    for edge in graph["in_edges"].get(node_id, ()):
        if edge.get("relation") in DOC_RELATIONS:
            yield edge, edge.get("source")


def affected_docs(graph: dict, changed_files: list[str]) -> list[dict]:
    """Docs plausibly made stale by a code change — ADVISORY suggestions, never a gate.

    Two layers with very different trust levels:

    1. Deterministic code blast radius (reverse reachability) — trustworthy.
    2. A single UNDIRECTED hop from any blast-radius node over the doc-semantic
       relations to a ``document``/``paper``/``concept``/``rationale`` node. These
       cross-links are **LLM-inferred and advisory** (ADR-0007 §2): surface them
       as ranked suggestions only. They MUST NOT be used as the freshness gate;
       the deterministic glob+diff match in ``freshness/detect.py`` stays the
       source of truth.

    Returns ``[{doc, min_confidence, hops}]`` deduped by ``doc`` (keeping the
    highest-confidence / shortest path) and ranked by (min_confidence desc,
    hops asc). ``doc`` is the node's ``source_file``; ``hops`` counts code hops to
    the dependent plus the one semantic hop to the doc.
    """
    reach = _reverse_reach(graph, changed_files)
    best: dict[str, dict] = {}

    for node_id, info in reach.items():
        for edge, other_id in _undirected_doc_edges(graph, node_id):
            other = graph["nodes_by_id"].get(other_id)
            if not other or other.get("file_type") not in DOC_FILE_TYPES:
                continue
            doc = _norm(other.get("source_file") or other_id)
            candidate = {
                "doc": doc,
                "min_confidence": min(info["min_confidence"], _confidence(edge)),
                "hops": info["hops"] + 1,
            }
            prev = best.get(doc)
            # Keep the best path per doc: higher confidence wins, then fewer hops.
            if prev is None or (candidate["min_confidence"], -candidate["hops"]) > (
                prev["min_confidence"], -prev["hops"]
            ):
                best[doc] = candidate

    return sorted(
        best.values(),
        key=lambda d: (-d["min_confidence"], d["hops"], d["doc"]),
    )

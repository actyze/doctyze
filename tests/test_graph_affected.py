"""Tests for the ADR-0007 prototype: affected docs via REVERSE code reachability.

These exercise the additive, opt-in graph module only. They must NOT depend on
(or affect) the deterministic glob+diff freshness gate.
"""
from __future__ import annotations

import json
from pathlib import Path

from doctyze.graph.affected import affected_docs, code_blast_radius, load_graph

FIXTURE = Path(__file__).parent / "fixtures" / "graphify_graph.json"


def _graph() -> dict:
    return load_graph(FIXTURE)


def test_blast_radius_includes_transitive_dependent():
    # (a) money.py's blast radius must include payments_x, because payments/x.py
    # imports money.py and is therefore a DEPENDENT (reverse reachability).
    radius = code_blast_radius(_graph(), ["money.py"])
    assert "money" in radius
    assert "payments_x" in radius


def test_affected_docs_includes_transitive_doc():
    # (b) Changing money.py should surface docs/specs/payments.md, reached via the
    # dependent payments_x and its advisory code->doc reference edge.
    docs = affected_docs(_graph(), ["money.py"])
    by_path = {d["doc"]: d for d in docs}
    assert "docs/specs/payments.md" in by_path
    entry = by_path["docs/specs/payments.md"]
    assert entry["min_confidence"] == 0.85  # min(imports 1.0, references 0.85)
    assert entry["hops"] == 2               # money -> payments_x -> spec_payments


def test_affected_docs_excludes_unrelated_doc():
    # (c) docs/specs/other.md hangs off `other`, which is not in money.py's
    # blast radius, so it must NOT be surfaced.
    docs = affected_docs(_graph(), ["money.py"])
    assert "docs/specs/other.md" not in {d["doc"] for d in docs}


def test_direction_dependency_is_not_a_dependent():
    # (d) DIRECTION guard: payments/x.py's blast radius must NOT include money.
    # money is x's dependency (x imports money), not its dependent. A forward
    # (out-edge) closure — the WRONG answer — would wrongly include it.
    radius = code_blast_radius(_graph(), ["payments/x.py"])
    assert "payments_x" in radius
    assert "money" not in radius


def test_load_graph_normalizes_edges_key_and_forces_directed():
    # (e) The fixture uses the raw "edges" key (not NetworkX's default "links").
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert "edges" in raw and "links" not in raw

    graph = load_graph(FIXTURE)
    assert graph["directed"] is True
    assert len(graph["links"]) == len(raw["edges"])  # edges normalized into links
    # A file maps to potentially many node ids; index is keyed by source_file.
    assert graph["ids_by_source_file"]["money.py"] == ["money"]

    # Also accepts an already-parsed dict and normalizes the same way.
    assert load_graph(raw)["directed"] is True

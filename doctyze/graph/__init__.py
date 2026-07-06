"""Experimental graph-based affected-docs (ADR-0007 prototype).

Opt-in, additive, and standalone. Nothing here is imported by the default
freshness path (``doctyze/freshness/detect.py``); the deterministic glob+diff
gate is untouched. See ``doctyze.graph.affected`` for details.
"""
from .affected import affected_docs, code_blast_radius, load_graph

__all__ = ["load_graph", "code_blast_radius", "affected_docs"]

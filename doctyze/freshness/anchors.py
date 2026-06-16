"""Read/write the Doctyze freshness anchor in a doc's YAML frontmatter.

A generated doc carries, in its frontmatter, a `doctyze:` block declaring which
code makes it stale:

    ---
    doctyze:
      artifact: spec
      generated_by: write-spec
      source: [src/payments/]
      affects: [src/payments/**, pom.xml]
      last_verified: 2026-06-14
    ---

This module is pure and deterministic (no LLM). It's the contract `detect` uses
to decide which docs a code change invalidates.
"""
from __future__ import annotations

import yaml

from ..model import Anchor, ArtifactKind

_FENCE = "---"


def _split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter_dict_or_None, body). Tolerant of missing/blank frontmatter."""
    if not text.startswith(_FENCE):
        return None, text
    parts = text.split(_FENCE, 2)
    if len(parts) < 3:
        return None, text
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(data, dict):
        return None, text
    return data, parts[2].lstrip("\n")


def parse_anchor(text: str) -> Anchor | None:
    """Extract the Doctyze anchor from a markdown doc, or None if absent."""
    front, _ = _split_frontmatter(text)
    if not front:
        return None
    block = front.get("doctyze")
    if not isinstance(block, dict):
        return None
    kind_raw = str(block.get("artifact", ArtifactKind.UNKNOWN.value))
    try:
        kind = ArtifactKind(kind_raw)
    except ValueError:
        kind = ArtifactKind.UNKNOWN
    return Anchor(
        artifact=kind,
        affects=list(block.get("affects", []) or []),
        source=list(block.get("source", []) or []),
        generated_by=block.get("generated_by"),
        last_verified=block.get("last_verified"),
    )


def render_frontmatter(anchor: Anchor) -> str:
    """Render an Anchor as a YAML frontmatter block (including fences)."""
    block: dict = {"artifact": anchor.artifact.value}
    if anchor.generated_by:
        block["generated_by"] = anchor.generated_by
    if anchor.source:
        block["source"] = anchor.source
    if anchor.affects:
        block["affects"] = anchor.affects
    if anchor.last_verified:
        block["last_verified"] = anchor.last_verified
    body = yaml.safe_dump({"doctyze": block}, sort_keys=False, default_flow_style=False)
    return f"{_FENCE}\n{body}{_FENCE}\n"

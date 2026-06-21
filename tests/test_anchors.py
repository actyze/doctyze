"""Tests for the freshness anchor parser/serializer (the one real M0 unit)."""
from __future__ import annotations

from doctyze.freshness.anchors import parse_anchor, render_frontmatter
from doctyze.model import Anchor, ArtifactKind


def test_roundtrip():
    anchor = Anchor(
        artifact=ArtifactKind.SPEC,
        affects=["src/payments/**", "pom.xml"],
        generated_by="write-spec",
        last_verified="2026-06-14",
    )
    doc = render_frontmatter(anchor) + "\n# Payments spec\n"
    parsed = parse_anchor(doc)
    assert parsed is not None
    assert parsed.artifact is ArtifactKind.SPEC
    assert parsed.affects == ["src/payments/**", "pom.xml"]
    assert parsed.generated_by == "write-spec"
    assert parsed.last_verified == "2026-06-14"


def test_no_frontmatter_returns_none():
    assert parse_anchor("# Just a heading\n\nno frontmatter here") is None


def test_frontmatter_without_doctyze_block_returns_none():
    doc = "---\ntitle: Something\n---\n\n# Body\n"
    assert parse_anchor(doc) is None


def test_unknown_artifact_kind_is_tolerated():
    doc = "---\ndoctyze:\n  artifact: not_a_real_kind\n---\n"
    parsed = parse_anchor(doc)
    assert parsed is not None
    assert parsed.artifact is ArtifactKind.UNKNOWN

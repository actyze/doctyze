"""Tests for the renderer base + frontmatter parser."""
from __future__ import annotations

from pathlib import Path

import pytest

from doctyze.renderers.base import (
    CanonicalDoc,
    collect_canonical,
    parse_canonical,
)


def test_parse_canonical_with_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "skill.md"
    p.write_text(
        "---\n"
        "name: foo\n"
        "description: bar\n"
        "---\n"
        "\n"
        "# Heading\n"
        "Body text.\n"
    )
    doc = parse_canonical(p)
    assert doc.frontmatter == {"name": "foo", "description": "bar"}
    assert "# Heading" in doc.body
    assert "Body text." in doc.body
    assert doc.name == "foo"


def test_parse_canonical_without_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "skill.md"
    p.write_text("# Heading\nNo frontmatter here.\n")
    doc = parse_canonical(p)
    assert doc.frontmatter == {}
    assert doc.body == "# Heading\nNo frontmatter here.\n"
    assert doc.name == "skill"   # stem fallback


def test_parse_canonical_with_invalid_yaml_frontmatter(tmp_path: Path) -> None:
    """Malformed YAML in frontmatter should be tolerated, not raise."""
    p = tmp_path / "skill.md"
    p.write_text(
        "---\n"
        ": this is :: not valid : yaml\n"
        "---\n"
        "Body.\n"
    )
    doc = parse_canonical(p)
    # We don't care what specifically we get, just that we didn't crash
    # and that the body is preserved.
    assert "Body." in doc.body


def test_canonical_name_prefers_frontmatter_over_stem(tmp_path: Path) -> None:
    p = tmp_path / "filename-stem.md"
    p.write_text("---\nname: from-frontmatter\n---\nBody.\n")
    doc = parse_canonical(p)
    assert doc.name == "from-frontmatter"


def test_collect_canonical_finds_only_md_files(tmp_path: Path) -> None:
    skills = tmp_path / "docs" / "skills"
    skills.mkdir(parents=True)
    (skills / "a.md").write_text("a")
    (skills / "b.md").write_text("b")
    (skills / "not-a-skill.txt").write_text("ignored")
    (skills / "README").write_text("ignored")

    docs = collect_canonical(tmp_path, "skills")
    names = sorted(d.path.name for d in docs)
    assert names == ["a.md", "b.md"]


def test_collect_canonical_returns_empty_when_dir_missing(tmp_path: Path) -> None:
    # No docs/skills/ exists at all — should return [], not raise.
    docs = collect_canonical(tmp_path, "skills")
    assert docs == []


def test_canonical_doc_dataclass_has_sensible_defaults() -> None:
    doc = CanonicalDoc(path=Path("x.md"))
    assert doc.frontmatter == {}
    assert doc.body == ""
    assert doc.name == "x"

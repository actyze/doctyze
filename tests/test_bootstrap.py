"""M2 tests: stack detection, structure scaffolding, architecture adapter, skills."""
from __future__ import annotations

from pathlib import Path

from doctyze.freshness.anchors import parse_anchor
from doctyze.generate.architecture import is_available, run_codeboarding
from doctyze.generate.manifest import build_manifest
from doctyze.generate.scaffold import ensure_structure
from doctyze.generate.stack import detect_stack


def test_detect_stack_java_and_node(tmp_path: Path):
    (tmp_path / "pom.xml").write_text("<project/>")
    (tmp_path / "azure-pipelines.yml").write_text("steps: []")
    (tmp_path / "Dockerfile").write_text("FROM eclipse-temurin")
    s = detect_stack(tmp_path)
    assert "java" in s.languages
    assert "maven" in s.frameworks
    assert "azure-devops" in s.ci
    assert "docker" in s.deploy


def test_detect_stack_python(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'")
    s = detect_stack(tmp_path)
    assert "python" in s.languages


def test_scaffold_creates_anchored_indexes_idempotently(tmp_path: Path):
    created = ensure_structure(tmp_path)
    assert created, "expected index files created"
    spec_index = tmp_path / "docs" / "specs" / "index.md"
    assert spec_index.exists()
    # the index carries a Doctyze anchor
    assert parse_anchor(spec_index.read_text()) is not None
    # idempotent: second run creates nothing new
    assert ensure_structure(tmp_path) == []


def test_architecture_adapter_degrades_gracefully(tmp_path: Path):
    # CodeBoarding almost certainly not installed in CI -> returns None, no crash
    if not is_available():
        assert run_codeboarding(tmp_path) is None


def test_manifest_mentions_stack_and_skills(tmp_path: Path):
    (tmp_path / "go.mod").write_text("module x")
    s = detect_stack(tmp_path)
    md = build_manifest(tmp_path, s, diagrams_done=False)
    assert "go" in md
    assert "write-spec" in md and "write-architecture" in md


def test_index_builds_navigation(tmp_path: Path):
    from doctyze.generate.index import build_indexes
    from doctyze.generate.scaffold import ensure_structure

    ensure_structure(tmp_path)
    (tmp_path / "docs" / "specs" / "foo.md").write_text("---\n---\n# Foo Feature\n\nDoes the foo thing.\n")
    written = build_indexes(tmp_path)
    assert written
    top = (tmp_path / "docs" / "index.md").read_text()
    assert "# Documentation" in top and "Specs" in top
    spec_index = (tmp_path / "docs" / "specs" / "index.md").read_text()
    assert "Foo Feature" in spec_index and "Does the foo thing" in spec_index


def test_generation_skills_have_valid_frontmatter():
    skills_dir = Path(__file__).resolve().parent.parent / "doctyze" / "skills"
    skill_files = list(skills_dir.glob("*/SKILL.md"))
    assert len(skill_files) >= 6
    for f in skill_files:
        head = f.read_text()
        assert head.startswith("---"), f"{f} missing frontmatter"
        assert "name:" in head and "description:" in head

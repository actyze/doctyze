"""M1 tests: audit -> plan -> apply on a synthetic scattered-docs repo."""
from __future__ import annotations

from pathlib import Path

from doctyze.consolidate.apply import apply_plan
from doctyze.consolidate.audit import audit_docs, classify
from doctyze.consolidate.plan import build_plan
from doctyze.model import ArtifactKind


def _scatter(root: Path) -> None:
    """Build a repo that mimics real scatter (like a typical service repo)."""
    (root / "README.md").write_text("# Service\nSee [the plan](US_1234_PLAN.md).\n")
    (root / "US_1234_PLAN.md").write_text("# Feature plan\nimplementation notes\n")
    (root / "wiki").mkdir()
    (root / "wiki" / "deployment-runbook.md").write_text("# Deploy\nhow we ship\n")
    (root / "docs" / "runbooks").mkdir(parents=True)
    (root / "docs" / "runbooks" / "high-error-rate.md").write_text("# Incident runbook\n")
    (root / "AGENTS.md").write_text("# agents\n")
    (root / ".cursor" / "rules").mkdir(parents=True)
    (root / ".cursor" / "rules" / "write-adr.md").write_text("rule\n")
    dec = root / "docs" / "architecture" / "decisions"
    dec.mkdir(parents=True)
    (dec / "0001-record-decisions.md").write_text("# adr1\n")
    (dec / "0001-aggregation-pattern.md").write_text("# adr1 dup\n")  # collision


def test_classification(tmp_path: Path):
    _scatter(tmp_path)
    kinds = {Path(d.path).name: d.kind for d in audit_docs(tmp_path)}
    assert kinds["README.md"] is ArtifactKind.KEEP_IN_PLACE
    assert kinds["AGENTS.md"] is ArtifactKind.AGENT_CONTEXT
    assert kinds["write-adr.md"] is ArtifactKind.AGENT_CONTEXT  # under .cursor/
    assert kinds["deployment-runbook.md"] is ArtifactKind.RUNBOOK
    assert kinds["high-error-rate.md"] is ArtifactKind.RUNBOOK
    assert kinds["US_1234_PLAN.md"] is ArtifactKind.SPEC
    assert kinds["0001-record-decisions.md"] is ArtifactKind.ADR


def test_plan_moves_and_collision(tmp_path: Path):
    _scatter(tmp_path)
    plan = build_plan(tmp_path, audit_docs(tmp_path))
    actions = {(Path(o.src).name, o.action) for o in plan.ops}
    # loose spec + wiki runbook get moved; agent files and README do not
    assert ("US_1234_PLAN.md", "move") in actions
    assert ("deployment-runbook.md", "move") in actions
    assert not any(Path(o.src).name == "README.md" for o in plan.ops)
    assert not any(Path(o.src).name == "AGENTS.md" for o in plan.ops)
    # one of the duplicate ADRs is renumbered, not overwritten
    assert any(o.action == "renumber" for o in plan.ops)


def test_apply_is_nondestructive_and_idempotent(tmp_path: Path):
    _scatter(tmp_path)
    plan = build_plan(tmp_path, audit_docs(tmp_path))
    moved = apply_plan(tmp_path, plan)
    assert moved, "expected some moves"
    # files landed in canonical locations; originals gone, none deleted
    assert (tmp_path / "docs" / "specs" / "US_1234_PLAN.md").exists()
    assert (tmp_path / "docs" / "runbooks" / "deployment-runbook.md").exists()
    assert not (tmp_path / "US_1234_PLAN.md").exists()
    # both ADRs survive (collision renumbered, not clobbered)
    adrs = list((tmp_path / "docs" / "architecture" / "decisions").glob("*.md"))
    assert len(adrs) == 2
    # re-running applies nothing new
    again = apply_plan(tmp_path, build_plan(tmp_path, audit_docs(tmp_path)))
    assert again == {}


def test_links_are_rewritten_after_move(tmp_path: Path):
    _scatter(tmp_path)
    apply_plan(tmp_path, build_plan(tmp_path, audit_docs(tmp_path)))
    readme = (tmp_path / "README.md").read_text()
    # README stayed put; its link to the moved plan now points at the new location
    assert "docs/specs/US_1234_PLAN.md" in readme

"""End-to-end integration: consolidate -> bootstrap -> distribute -> freshness.

Mirrors the M4 validation on a synthetic git repo (no external deps).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from doctyze.consolidate.apply import apply_plan
from doctyze.consolidate.audit import audit_docs
from doctyze.consolidate.plan import build_plan
from doctyze.distribute.fanout import distribute
from doctyze.freshness.anchors import render_frontmatter
from doctyze.freshness.detect import changed_files, find_stale
from doctyze.generate.scaffold import ensure_structure
from doctyze.model import Anchor, ArtifactKind


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def test_full_pipeline(tmp_path: Path):
    root = tmp_path
    _git(root, "init")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")

    # scattered repo with real code
    (root / "US_99_PLAN.md").write_text("# work\n")
    (root / "src" / "payments").mkdir(parents=True)
    (root / "src" / "payments" / "Pay.java").write_text("class Pay {}\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "init")

    # 1) consolidate
    moved = apply_plan(root, build_plan(root, audit_docs(root)))
    assert (root / "docs" / "specs" / "US_99_PLAN.md").exists()
    assert moved

    # 2) bootstrap structure
    ensure_structure(root)
    assert (root / "docs" / "architecture" / "diagrams" / "index.md").exists()

    # 3) distribute skills to agent files
    distribute(root)
    assert (root / "AGENTS.md").read_text().count("doctyze:start") == 1

    # 4) freshness: an anchored spec goes stale when its code changes
    spec = root / "docs" / "specs" / "payments.md"
    spec.write_text(render_frontmatter(
        Anchor(artifact=ArtifactKind.SPEC, affects=["src/payments/**"], generated_by="write-spec")
    ) + "\n# Payments\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "docs")

    assert find_stale(root, changed_files(root)) == []  # clean
    (root / "src" / "payments" / "Pay.java").write_text("class Pay { int x; }\n")
    _git(root, "add", "-A")
    stale = find_stale(root, changed_files(root, staged=True))
    assert [p.name for p, _, _ in stale] == ["payments.md"]

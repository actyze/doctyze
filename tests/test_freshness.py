"""M3 tests: the affected-docs detector, refresh manifest, and hook install."""
from __future__ import annotations

import subprocess
from pathlib import Path

from doctyze.freshness.anchors import render_frontmatter
from doctyze.freshness.detect import find_stale, matches
from doctyze.freshness.hook import install_hook
from doctyze.freshness.regenerate import write_refresh_manifest
from doctyze.model import Anchor, ArtifactKind


def test_glob_matcher():
    assert matches("src/payments/**", "src/payments/api/Service.java")
    assert matches("src/payments/**", "src/payments/X.java")
    assert matches("pom.xml", "pom.xml")
    assert matches("src/**/*.java", "src/a/b/C.java")
    assert not matches("src/payments/**", "src/orders/Z.java")
    assert not matches("pom.xml", "build.gradle")


def test_glob_leading_and_interior_doublestar_match_root():
    # `**/` means zero-or-more directories (gitignore semantics), so it must match root.
    assert matches("**/config.py", "config.py")           # root-level
    assert matches("**/config.py", "src/deep/config.py")  # nested
    assert matches("src/**/foo.py", "src/foo.py")          # interior **/ at zero depth
    assert matches("src/**/*.java", "src/C.java")          # (was a false negative pre-fix)
    assert not matches("**/config.py", "config_test.py")


def _spec(root: Path, name: str, affects: list[str]) -> None:
    p = root / "docs" / "specs" / f"{name}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    anchor = Anchor(artifact=ArtifactKind.SPEC, affects=affects, generated_by="write-spec")
    p.write_text(render_frontmatter(anchor) + f"\n# {name}\n")


def test_find_stale_matches_only_affected(tmp_path: Path):
    _spec(tmp_path, "payments", ["src/payments/**"])
    _spec(tmp_path, "orders", ["src/orders/**"])

    stale = find_stale(tmp_path, ["src/payments/api/Pay.java"])
    assert [p.name for p, _, _ in stale] == ["payments.md"]

    assert find_stale(tmp_path, ["README.md"]) == []


def test_refresh_manifest_written(tmp_path: Path):
    _spec(tmp_path, "payments", ["src/payments/**"])
    stale = find_stale(tmp_path, ["src/payments/Pay.java"])
    out = write_refresh_manifest(tmp_path, stale)
    assert out.exists()
    text = out.read_text()
    assert "payments.md" in text and "write-spec" in text


def test_install_hook_in_git_repo(tmp_path: Path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    hook = install_hook(tmp_path)
    assert hook is not None and hook.exists()
    assert hook.stat().st_mode & 0o100  # executable
    assert "doctyze watch" in hook.read_text()


def test_install_hook_non_git_returns_none(tmp_path: Path):
    assert install_hook(tmp_path) is None

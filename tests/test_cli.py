"""M0 smoke tests: the package imports and the CLI runs with zero optional deps."""
from __future__ import annotations

import click.testing

import doctyze
from doctyze.cli import main


def test_version_present():
    assert doctyze.__version__.startswith("0.3")


def test_no_forced_llm_dependency():
    # Doctyze must import and run without anthropic/openai installed (BYO-agent).
    import importlib
    import sys

    assert "anthropic" not in sys.modules
    # Importing the package must not pull in an LLM SDK.
    importlib.import_module("doctyze.cli")
    assert "anthropic" not in sys.modules


def test_top_level_help():
    res = click.testing.CliRunner().invoke(main, ["--help"])
    assert res.exit_code == 0
    assert "documentation context layer" in res.output


def test_init_scaffolds_and_distributes(tmp_path):
    res = click.testing.CliRunner().invoke(main, ["init", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert (tmp_path / "docs" / "specs" / "index.md").exists()        # scaffolded
    assert (tmp_path / ".claude" / "skills" / "doctyze" / "SKILL.md").exists()  # distributed
    assert "Next:" in res.output


def test_all_subcommands_run():
    runner = click.testing.CliRunner()
    # Run in an isolated temp dir — these commands now create files.
    for cmd in ("init", "consolidate", "bootstrap", "index", "distribute", "watch"):
        with runner.isolated_filesystem():
            res = runner.invoke(main, [cmd])
            assert res.exit_code == 0, f"{cmd} failed: {res.output}"


def test_watch_exit_code_opt_in_passes_when_fresh():
    # --exit-code is opt-in CI gating; with no stale docs it must still exit 0.
    runner = click.testing.CliRunner()
    with runner.isolated_filesystem():
        res = runner.invoke(main, ["watch", "--exit-code"])
        assert res.exit_code == 0, res.output
        assert "Docs are fresh." in res.output


def _init_repo_with_stale_committed_change(tmp_path):
    """Simulate a CI PR: an anchored doc, then a *committed* change to the anchored file."""
    import subprocess

    def git(*a):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    git("init"); git("config", "user.email", "t@t.co"); git("config", "user.name", "t")
    git("checkout", "-b", "main")
    (tmp_path / "foo.py").write_text("def f():\n    return 1\n")
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "foo.md").write_text(
        "---\ndoctyze:\n  artifact: spec\n  generated_by: write-spec\n"
        "  affects: [foo.py]\n  last_verified: 2026-07-03\n---\n# Foo\n"
    )
    git("add", "-A"); git("commit", "-m", "baseline")
    git("checkout", "-b", "feature")
    (tmp_path / "foo.py").write_text("def f():\n    return 2\n")
    git("add", "-A"); git("commit", "-m", "change foo")


def test_ci_needs_base_to_detect_committed_changes(tmp_path):
    # ADR-0006: without --base a clean CI checkout wrongly reports fresh; --base fixes it.
    _init_repo_with_stale_committed_change(tmp_path)
    runner = click.testing.CliRunner()

    without = runner.invoke(main, ["watch", "--exit-code", str(tmp_path)])
    assert without.exit_code == 0 and "fresh" in without.output.lower()   # the trap

    with_base = runner.invoke(main, ["watch", "--exit-code", "--base", "main", str(tmp_path)])
    assert with_base.exit_code == 1                                        # gate fires
    assert "may be stale" in with_base.output


def test_local_hook_stays_warn_only(tmp_path):
    # ADR-0006: the local pre-commit hook must never gate — no --exit-code, forced exit 0.
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    res = click.testing.CliRunner().invoke(main, ["watch", "--install", str(tmp_path)])
    assert res.exit_code == 0, res.output
    hook = (tmp_path / ".git" / "hooks" / "pre-commit").read_text()
    assert "--exit-code" not in hook          # never gates locally
    assert "exit 0" in hook                    # belt-and-suspenders warn-only

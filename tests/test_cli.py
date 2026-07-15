"""M0 smoke tests: the package imports and the CLI runs with zero optional deps."""
from __future__ import annotations

import re

import click.testing

import doctyze
from doctyze.cli import main


def test_version_present():
    assert re.match(r"^\d+\.\d+(\.\d+)?", doctyze.__version__)


def test_version_matches_pyproject():
    # Single source of truth: __version__ (what `doctyze --version` prints) must equal the
    # packaged version. Prevents the __init__/pyproject/plugin drift found in the 0.3.4 audit.
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parent.parent
    txt = (root / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', txt, re.M)
    assert m, "version not found in pyproject.toml"
    assert doctyze.__version__ == m.group(1), (
        f"__version__ {doctyze.__version__!r} != pyproject {m.group(1)!r} — bump both in lockstep"
    )


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


def test_ci_gate_fails_closed_on_unresolvable_base(tmp_path):
    # ADR-0006 fix: a bad/unfetched base ref must NOT report "fresh" under --exit-code.
    _init_repo_with_stale_committed_change(tmp_path)
    runner = click.testing.CliRunner()

    gated = runner.invoke(main, ["watch", "--exit-code", "--base", "origin/nope", str(tmp_path)])
    assert gated.exit_code == 2                                            # fail closed
    assert "fresh" not in gated.output.lower()

    warn = runner.invoke(main, ["watch", "--base", "origin/nope", str(tmp_path)])
    assert warn.exit_code == 0                                             # warn-only stays non-blocking


def test_watch_staged_and_base_are_mutually_exclusive():
    res = click.testing.CliRunner().invoke(main, ["watch", "--staged", "--base", "main"])
    assert res.exit_code != 0
    assert "mutually exclusive" in res.output


def test_local_hook_stays_warn_only(tmp_path):
    # ADR-0006: the local pre-commit hook must never gate — no --exit-code, forced exit 0.
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    res = click.testing.CliRunner().invoke(main, ["watch", "--install", str(tmp_path)])
    assert res.exit_code == 0, res.output
    hook = (tmp_path / ".git" / "hooks" / "pre-commit").read_text()
    assert "--exit-code" not in hook          # never gates locally
    assert "exit 0" in hook                    # belt-and-suspenders warn-only

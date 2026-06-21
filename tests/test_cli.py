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

"""Doctyze CLI — a thin presenter over the `api` service layer.

The command bodies only parse args and format output; the actual work lives in
`doctyze/api.py` (shared with the MCP server, so the two can't drift). None of
these commands require an API key — generation is delegated to the agent.
"""
from __future__ import annotations

from pathlib import Path

import click

from . import __version__, api


@click.group()
@click.version_option(version=__version__, prog_name="doctyze")
def main() -> None:
    """Generate & maintain a documentation context layer for any repo.

    Doctyze brings the playbook; your existing IDE/CI agent brings the LLM.
    """


@main.command()
@click.argument("path", default=".")
@click.option("--with-mcp", is_flag=True,
              help="Also register the Doctyze MCP server in your IDE configs "
                   "(.mcp.json, .cursor/mcp.json, .vscode/mcp.json). Off by default — "
                   "the `doctyze` CLI over uvx does the same work and needs no MCP.")
def init(path: str, with_mcp: bool) -> None:
    """One-command setup: install the Doctyze skills and scaffold the docs/ structure.
    Run once (e.g. `uvx doctyze init`), then open your IDE and invoke the `doctyze`
    prompt/skill.

    Safe: does NOT move existing docs, does NOT generate prose. The docs, skills and
    freshness workflow all run through the `doctyze` CLI (over `uvx`) — no MCP required.
    Pass --with-mcp to additionally wire the optional Doctyze MCP server into your IDE
    configs.
    """
    from .generate.scaffold import ensure_structure
    from .generate.stack import detect_stack

    root = Path(path).resolve()
    written = api.distribute(root)
    ensure_structure(root)
    stack = detect_stack(root)

    click.echo(f"Doctyze set up in {root.name}/ (stack: {', '.join(stack.languages) or 'unknown'}).")
    click.echo(f"  • Doctyze skills installed to {len(written)} agent file(s) (.claude/skills, .cursor/rules, AGENTS.md)")
    click.echo("  • canonical docs/ structure scaffolded")

    if with_mcp:
        from .setup import wire_mcp
        result = wire_mcp(root)
        click.echo("  • MCP server registered for your IDEs → "
                   f"{', '.join(str(p.relative_to(root)) for p in result['written'])}")
        if result["global_only"]:
            tools = " + ".join(result["global_only"])
            click.echo(f"\nNote: detected {tools} — these use a GLOBAL MCP config (no project scope).")
            click.echo("  Add Doctyze there with the same server: uvx --from \"doctyze[mcp]\" doctyze-mcp")
            click.echo("    Windsurf: ~/.codeium/windsurf/mcp_config.json   Cline: its \"Configure MCP Servers\" UI")

    click.echo("\nNext:")
    click.echo("  1. Reload / reopen your IDE so it loads the Doctyze skills.")
    click.echo("  2. In your assistant, invoke the `doctyze` prompt (Claude Code: /doctyze) —")
    click.echo("     it consolidates existing docs, reads the code, and writes the docs.")
    click.echo("     Runs via the `doctyze` CLI over uvx — no MCP approval needed.")
    click.echo("  3. git add -A && commit → teammates inherit Doctyze (skills) on clone.")

    if with_mcp:
        click.echo("\nUsing the MCP tools (optional) — approve the server once:")
        click.echo("    • Claude Code : run /mcp → select doctyze → Enable")
        click.echo("    • Cursor      : Settings → MCP → enable doctyze")
        click.echo("    • VS Code     : click Start on the doctyze server when prompted")


@main.command()
@click.option("--apply", is_flag=True, help="Apply the migration plan (default: propose only).")
@click.argument("path", default=".")
def consolidate(apply: bool, path: str) -> None:
    """Audit scattered docs and consolidate into the canonical structure.

    Without --apply, writes a reviewable plan and changes nothing. Moves preserve
    git history; nothing is ever deleted.
    """
    root = Path(path).resolve()
    result = api.consolidate_plan(root)

    plan_path = root / ".doctyze" / "consolidation-plan.md"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(result.rendered, encoding="utf-8")

    click.echo(f"Scanned {len(result.docs)} docs; {len(result.plan.ops)} proposed change(s).")
    click.echo(f"Plan written to {plan_path.relative_to(root)}")
    if not result.plan.ops:
        click.echo("Already canonical — nothing to do.")
        return
    if apply:
        moved = api.consolidate_apply(root, result.plan)
        click.echo(f"Applied {len(moved)} change(s), non-destructively.")
    else:
        click.echo("Proposed only. Review the plan, then re-run with --apply.")


@main.command()
@click.argument("path", default=".")
def bootstrap(path: str) -> None:
    """Scaffold the canonical docs/ structure and hand a generation manifest to your agent.

    Deterministic only: structure + stack detection + optional CodeBoarding diagrams.
    The prose generation is then done by your existing agent following the manifest.
    """
    root = Path(path).resolve()
    r = api.bootstrap(root)

    manifest_path = root / ".doctyze" / "bootstrap-manifest.md"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(r.manifest, encoding="utf-8")

    click.echo(f"Scaffolded {len(r.created)} section index file(s); stack: "
               f"{', '.join(r.stack.languages) or 'unknown'}.")
    click.echo("Diagrams: " + ("generated via CodeBoarding." if r.diagrams_done
                                else "CodeBoarding not found — your agent will draw them."))
    click.echo(f"Next steps for your agent: {manifest_path.relative_to(root)}")


@main.command()
@click.argument("path", default=".")
def index(path: str) -> None:
    """(Re)build the docs/ navigation index — a table of contents for humans and agents."""
    root = Path(path).resolve()
    written = api.build_index(root)
    if not written:
        click.echo("No docs/ to index yet.")
        return
    click.echo(f"Wrote {len(written)} index file(s): docs/index.md + per-section tables.")


@main.command()
@click.argument("path", default=".")
def distribute(path: str) -> None:
    """Fan the Doctyze skills out to agent files (.claude/skills, .cursor/rules, AGENTS.md)."""
    root = Path(path).resolve()
    written = api.distribute(root)
    click.echo(f"Distributed skills to {len(written)} agent file(s) under {root.name}/.")


@main.command()
@click.option("--install", is_flag=True, help="Install the warn-first pre-commit freshness hook.")
@click.option("--staged", is_flag=True, help="Check staged changes (used by the hook).")
@click.option("--exit-code", "exit_code", is_flag=True,
              help="Exit non-zero if any doc is stale — opt-in, for CI merge gating. "
                   "Default (and the local pre-commit hook) stay warn-only. See ADR-0006.")
@click.option("--base", default=None, metavar="REF",
              help="Diff against this git ref instead of the working tree (e.g. `origin/main`). "
                   "Required in CI, where committed PR changes are invisible to the default "
                   "working-tree diff. A plain ref uses merge-base (three-dot) semantics so only "
                   "this branch's own changes count; pass an explicit `A..B`/`A...B` to override. "
                   "If the ref can't be resolved, --exit-code fails closed.")
@click.argument("path", default=".")
def watch(install: bool, staged: bool, exit_code: bool, base: str | None, path: str) -> None:
    """Keep docs fresh: flag docs whose anchored code changed; delegate refresh to your agent.

    Warn-first by default — never blocks. `--install` adds the (warn-only) pre-commit hook.
    `--exit-code` opts into a non-zero exit for CI gating (local flow stays warn-only).
    In CI, pass `--base <ref>` so *committed* changes on a PR are detected.
    """
    from .freshness.detect import GitDiffError
    from .freshness.hook import install_hook
    from .freshness.regenerate import write_refresh_manifest

    root = Path(path).resolve()
    if install:
        hook = install_hook(root)
        if hook is None:
            click.echo("Not a git repo — no .git/hooks to install into.")
        else:
            click.echo(f"Installed warn-first freshness hook: {hook.relative_to(root)}")
        return

    if staged and base is not None:
        raise click.UsageError(
            "--staged and --base are mutually exclusive: --staged is the local hook path "
            "(index vs HEAD); --base is the CI path (branch vs a ref)."
        )

    try:
        stale = api.check_freshness(root, staged=staged, base=base or "HEAD")
    except GitDiffError as e:
        # A gate must fail closed: if the base ref can't be resolved, don't report
        # "fresh". Warn-only mode surfaces the error but stays non-blocking (exit 0).
        click.echo(f"error: {e}", err=True)
        if exit_code:
            raise SystemExit(2)
        return

    if not stale:
        click.echo("Docs are fresh.")
        return
    out = write_refresh_manifest(root, stale)
    click.echo(f"{len(stale)} doc(s) may be stale (see {out.relative_to(root)}):")
    for f, anchor, _ in stale:
        click.echo(f"  - {f.relative_to(root)}  (regenerate: {anchor.generated_by})")
    if exit_code:
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()

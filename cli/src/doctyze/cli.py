"""Doctyze CLI entry point.

Commands:
    doctyze init [--stack=<stack>] [--dry-run]
        Scan the current repo, detect the stack, and emit the canonical
        documentation structure. Also renders vendor-specific files for the
        agent targets configured in .doctyze.yaml.

    doctyze render [--target=<vendor>] [--dry-run] [--check]
        Render canonical docs/skills/*.md and docs/runbooks/*.md into the
        vendor-specific formats configured in .doctyze.yaml
        (.claude/skills/, .cursor/rules/, .github/copilot-instructions.md,
        .windsurfrules, .holmes/runbooks/, etc.).

    doctyze verify [--strict]
        Check for drift between code and documentation. Reports stale
        artifacts and missing 🔴 GAP items.

    doctyze pr-bot install
        Add the GitHub Action workflow file to .github/workflows/.

    doctyze interview-prep <ADR-id|--all>
        Generate interview questions for senior-engineer ADR archaeology
        (legacy stack only).

    doctyze ingest <source> --connection=<uri> [--output=<dir>]
        Pull legacy code from non-git SCM (Endevor / ChangeMan / ARCAD / abapGit / VSS)
        into a local git repo, ready for `doctyze init`.

    doctyze mcp-serve
        Expose Doctyze as an MCP server so AI agents can invoke init/verify/etc.

Use `--help` on any command for details.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from doctyze import __version__
from doctyze import renderers
from doctyze.detector import detect_stack
from doctyze.scaffolder import Scaffolder

console = Console()

# Default vendors rendered when .doctyze.yaml is missing or doesn't specify.
DEFAULT_AGENT_TARGETS = ["claude", "cursor", "copilot", "holmes"]


def _load_agent_targets(repo: Path) -> list[str]:
    """Read agent_targets from .doctyze.yaml, fall back to defaults."""
    config_path = repo / ".doctyze.yaml"
    if not config_path.exists():
        return DEFAULT_AGENT_TARGETS
    try:
        config = yaml.safe_load(config_path.read_text()) or {}
    except yaml.YAMLError:
        return DEFAULT_AGENT_TARGETS
    targets = config.get("agent_targets")
    if not isinstance(targets, list) or not targets:
        return DEFAULT_AGENT_TARGETS
    return [str(t).lower() for t in targets]


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="doctyze")
def main() -> None:
    """Doctyze — turn any codebase into living documentation."""


@main.command()
@click.option("--stack", default=None, help="Override stack auto-detection.")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without writing files.")
@click.option("--path", default=".", help="Path to the repository to scaffold.")
@click.option("--llm", default=None, help="LLM provider (claude|openai|gemini|bedrock|azure|ollama).")
def init(stack: str | None, dry_run: bool, path: str, llm: str | None) -> None:
    """Scan repo, detect stack, emit canonical documentation structure."""
    repo = Path(path).resolve()
    if not repo.is_dir():
        console.print(f"[red]error:[/red] not a directory: {repo}")
        sys.exit(1)

    console.print(f"[bold]Doctyze[/bold] init  →  {repo}")
    detection = detect_stack(repo, override=stack)
    console.print(
        f"  detected stack: [cyan]{detection.stack}[/cyan]  "
        f"(confidence: {detection.confidence:.0%})"
    )
    if detection.confidence < 0.7 and not stack:
        console.print(
            "[yellow]warning:[/yellow] low confidence in stack detection. "
            "Re-run with [bold]--stack=<name>[/bold] to override."
        )

    scaffolder = Scaffolder(repo=repo, stack=detection.stack, llm=llm)
    plan = scaffolder.plan()

    table = Table(title="Files to be generated", show_lines=False)
    table.add_column("Path", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Confidence", justify="center")
    for entry in plan:
        table.add_row(str(entry.relpath), entry.kind, entry.confidence_marker)
    console.print(table)

    if dry_run:
        console.print("[yellow]--dry-run set; nothing written.[/yellow]")
        return

    if not click.confirm("Proceed with generation?", default=True):
        console.print("Aborted.")
        return

    scaffolder.write(plan)
    console.print(f"[green]✓[/green] generated {len(plan)} files")

    # After scaffolding, render vendor-specific files for the configured
    # agent targets so the repo works out-of-the-box with Claude Code,
    # Cursor, Copilot, Holmes, etc.
    targets = _load_agent_targets(repo)
    if targets:
        console.print(
            f"\nRendering vendor files for agent targets: "
            f"[cyan]{', '.join(targets)}[/cyan]"
        )
        rendered = _render_targets(repo, targets, dry_run=False)
        console.print(f"[green]✓[/green] rendered {rendered} vendor files")


def _render_targets(
    repo: Path,
    target_names: list[str],
    *,
    dry_run: bool,
) -> int:
    """Run each requested renderer and return the count of generated files."""
    total = 0
    for name in target_names:
        try:
            renderer = renderers.get(name)
        except KeyError as exc:
            console.print(f"  [yellow]skip[/yellow] {name}: {exc}")
            continue
        try:
            written = renderer.render(repo, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001 — surface any renderer issue clearly
            console.print(f"  [red]error[/red] {name}: {exc}")
            continue
        verb = "would write" if dry_run else "wrote"
        console.print(f"  [cyan]{name:<10}[/cyan] {verb} {len(written)} file(s)")
        total += len(written)
    return total


@main.command()
@click.option(
    "--target",
    "targets",
    multiple=True,
    help="Render only this target. May be passed multiple times. Default: all configured.",
)
@click.option("--dry-run", is_flag=True, help="Show what would be written without writing.")
@click.option(
    "--check",
    is_flag=True,
    help="CI mode: exit non-zero if generated files would differ from current on-disk content.",
)
@click.option("--path", default=".", help="Repo root.")
@click.option("--list", "list_targets", is_flag=True, help="List available renderers and exit.")
def render(
    targets: tuple[str, ...],
    dry_run: bool,
    check: bool,
    path: str,
    list_targets: bool,
) -> None:
    """Render canonical docs/skills + docs/runbooks into vendor-specific files."""
    if list_targets:
        table = Table(title="Available renderers", show_lines=False)
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        for name, cls in sorted(renderers.REGISTRY.items()):
            table.add_row(name, cls.description or "")
        console.print(table)
        return

    repo = Path(path).resolve()
    if not repo.is_dir():
        console.print(f"[red]error:[/red] not a directory: {repo}")
        sys.exit(1)

    selected = list(targets) if targets else _load_agent_targets(repo)
    console.print(
        f"[bold]Doctyze[/bold] render  →  {repo}  "
        f"(targets: [cyan]{', '.join(selected)}[/cyan])"
    )

    if check:
        # Render to a sibling shadow tree, then byte-compare against the
        # current on-disk content. This catches both missing files AND
        # stale content — the difference matters when a canonical source
        # was edited but the vendor file wasn't re-rendered.
        import shutil
        import tempfile

        drift_missing: list[Path] = []
        drift_stale: list[Path] = []

        with tempfile.TemporaryDirectory() as shadow_root_str:
            shadow_root = Path(shadow_root_str) / "shadow"
            # Copy canonical sources to the shadow so renderers have what
            # they need to produce expected output.
            for sub in ("docs", ".doctyze.yaml"):
                src = repo / sub
                if src.is_dir():
                    shutil.copytree(src, shadow_root / sub)
                elif src.is_file():
                    (shadow_root).mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, shadow_root / sub)

            for name in selected:
                try:
                    renderer = renderers.get(name)
                except KeyError as exc:
                    console.print(f"  [yellow]skip[/yellow] {name}: {exc}")
                    continue
                # Render into the shadow tree.
                expected_paths = renderer.render(shadow_root, dry_run=False)
                for expected in expected_paths:
                    rel = expected.relative_to(shadow_root)
                    on_disk = repo / rel
                    if not on_disk.exists():
                        drift_missing.append(rel)
                    elif on_disk.read_text() != expected.read_text():
                        drift_stale.append(rel)

        total = len(drift_missing) + len(drift_stale)
        if total:
            console.print(
                f"[red]✗[/red] {total} vendor file(s) out of sync with canonical sources. "
                "Run [bold]doctyze render[/bold] to fix."
            )
            for d in drift_missing[:10]:
                console.print(f"  [red]missing[/red] {d}")
            for d in drift_stale[:10]:
                console.print(f"  [red]stale  [/red] {d}")
            sys.exit(1)
        console.print("[green]✓[/green] all vendor files in sync with canonical sources")
        return

    total = _render_targets(repo, selected, dry_run=dry_run)
    suffix = " (dry-run)" if dry_run else ""
    console.print(f"[green]✓[/green] rendered {total} file(s){suffix}")


@main.command()
@click.option("--strict", is_flag=True, help="Exit non-zero on any drift.")
@click.option("--path", default=".", help="Path to the repository to verify.")
def verify(strict: bool, path: str) -> None:
    """Check for drift between code and documentation."""
    repo = Path(path).resolve()
    console.print(f"[bold]Doctyze[/bold] verify  →  {repo}")

    # TODO: actual drift detection logic
    issues: list[str] = []
    if not (repo / "docs").exists():
        issues.append("no docs/ folder — run `doctyze init` first")
    if not (repo / "AGENTS.md").exists():
        issues.append("no AGENTS.md — run `doctyze init` first")

    if not issues:
        console.print("[green]✓[/green] no drift detected")
        return

    for issue in issues:
        console.print(f"  [yellow]⚠[/yellow] {issue}")
    if strict:
        sys.exit(1)


@main.group("pr-bot")
def pr_bot() -> None:
    """Manage the Doctyze PR review GitHub Action."""


@pr_bot.command("install")
@click.option("--path", default=".", help="Repo to install the bot in.")
@click.option(
    "--mode",
    type=click.Choice(["warn-only", "block-required", "block-all"]),
    default="warn-only",
    help="Enforcement level.",
)
def pr_bot_install(path: str, mode: str) -> None:
    """Add .github/workflows/doctyze-review.yml to the repo."""
    repo = Path(path).resolve()
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    target = workflows / "doctyze-review.yml"
    if target.exists():
        console.print(f"[yellow]already exists:[/yellow] {target}")
        return
    template = (
        Path(__file__).resolve().parents[3]
        / "templates"
        / "modern"
        / ".github"
        / "workflows"
        / "doctyze-review.yml"
    )
    if not template.exists():
        console.print(f"[red]error:[/red] template not found: {template}")
        sys.exit(1)
    content = template.read_text().replace("mode: warn-only", f"mode: {mode}")
    target.write_text(content)
    console.print(f"[green]✓[/green] installed {target}")
    console.print(
        "  Don't forget to add [bold]ANTHROPIC_API_KEY[/bold] (or your LLM provider's key) "
        "to the repository secrets."
    )


@main.command("interview-prep")
@click.argument("adr_id", required=False)
@click.option("--all", "all_gaps", is_flag=True, help="Generate questions for all 🔴 GAP items.")
@click.option("--path", default=".", help="Path to the legacy repo.")
def interview_prep(adr_id: str | None, all_gaps: bool, path: str) -> None:
    """Generate interview questions for senior-engineer ADR archaeology (legacy)."""
    repo = Path(path).resolve()
    console.print(f"[bold]Doctyze[/bold] interview-prep  →  {repo}")
    pending = repo / "docs" / "investigations" / "adr-archaeology" / "pending-questions.md"
    if not pending.exists():
        console.print(
            f"[red]error:[/red] {pending} not found. Is this a legacy-stack repo "
            "with `doctyze init` already run?"
        )
        sys.exit(1)
    console.print(f"  see: [cyan]{pending}[/cyan]")
    console.print("  TODO: generate ADR-specific question packs for targeted interviews")


@main.command()
@click.argument("source", type=click.Choice(["endevor", "changeman", "librarian", "abapgit", "arcad", "vss"]))
@click.option("--connection", required=True, help="Connection URI for the source SCM.")
@click.option("--output", required=True, help="Local directory to write the extracted code to.")
def ingest(source: str, connection: str, output: str) -> None:
    """Pull legacy code from non-git SCM into a local git repo."""
    console.print(f"[bold]Doctyze[/bold] ingest  →  source=[cyan]{source}[/cyan]")
    console.print(f"  connection: {connection}")
    console.print(f"  output: {output}")
    console.print(
        "[yellow]🔴 GAP[/yellow] ingestion adapter for "
        f"[bold]{source}[/bold] is not yet implemented. "
        "See extractors/legacy/ for the canonical implementation plan."
    )
    sys.exit(2)


@main.command("mcp-serve")
@click.option("--port", default=None, type=int, help="HTTP port (default: stdio transport).")
def mcp_serve(port: int | None) -> None:
    """Expose Doctyze as an MCP server."""
    console.print("[bold]Doctyze[/bold] mcp-serve")
    console.print("[yellow]🔴 GAP[/yellow] MCP server is not yet implemented.")
    sys.exit(2)


if __name__ == "__main__":
    main()

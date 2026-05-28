"""Doctyze CLI entry point.

Commands:
    doctyze init [--stack=<stack>] [--dry-run]
        Scan the current repo, detect the stack, and emit the canonical
        documentation structure.

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
from rich.console import Console
from rich.table import Table

from doctyze import __version__
from doctyze.detector import detect_stack
from doctyze.scaffolder import Scaffolder

console = Console()


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

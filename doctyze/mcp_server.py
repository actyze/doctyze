"""Doctyze MCP server — exposes the deterministic tools to any MCP-capable agent.

Thin presenters over `doctyze/api.py` (the same service layer the CLI uses), so
the two entry points can't drift. `mcp` is an optional dependency: this module
imports without it; only `build_server()` needs it.

Install: pip install 'doctyze[mcp]'   Run: doctyze-mcp
"""
from __future__ import annotations

from pathlib import Path

from . import api


def consolidate_plan(path: str = ".") -> str:
    """Audit scattered docs and return the proposed (non-destructive) consolidation plan."""
    return api.consolidate_plan(Path(path)).rendered


def consolidate_apply(path: str = ".") -> str:
    """Apply the consolidation plan non-destructively (git-mv, link rewrite, idempotent)."""
    moved = api.consolidate_apply(Path(path))
    return f"Applied {len(moved)} change(s) non-destructively."


def bootstrap(path: str = ".") -> str:
    """Scaffold the canonical docs/ structure and return the generation manifest."""
    return api.bootstrap(Path(path)).manifest


def rebuild_index(path: str = ".") -> str:
    """(Re)build the docs/ navigation index (table of contents) for humans and agents."""
    return f"Wrote {len(api.build_index(Path(path)))} index file(s)."


def distribute(path: str = ".") -> str:
    """Fan the Doctyze skills out to agent files (.claude/skills, .cursor/rules, AGENTS.md)."""
    return f"Distributed skills to {len(api.distribute(Path(path)))} agent file(s)."


def check_freshness(path: str = ".", staged: bool = False) -> str:
    """List docs whose anchored code changed (and write a refresh manifest)."""
    from .freshness.regenerate import write_refresh_manifest

    root = Path(path).resolve()
    stale = api.check_freshness(root, staged=staged)
    if not stale:
        return "Docs are fresh."
    write_refresh_manifest(root, stale)
    lines = [f"- {p.relative_to(root)} (regenerate: {a.generated_by})" for p, a, _ in stale]
    return f"{len(stale)} doc(s) may be stale:\n" + "\n".join(lines)


def install_freshness_hook(path: str = ".") -> str:
    """Install the warn-first pre-commit hook that flags stale docs on every commit."""
    hook = api.install_freshness_hook(Path(path))
    if hook is None:
        return "Not a git repo — no .git/hooks to install into."
    return f"Installed the warn-first pre-commit freshness hook at {hook}. It runs `doctyze watch` (via CLI or uvx) on each commit."


_TOOLS = [
    consolidate_plan, consolidate_apply, bootstrap, rebuild_index,
    distribute, check_freshness, install_freshness_hook,
]


def build_server():
    """Build the FastMCP server. Requires the optional 'mcp' dependency."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:  # pragma: no cover - exercised only without the extra
        raise SystemExit(
            "doctyze-mcp needs the optional 'mcp' dependency: pip install 'doctyze[mcp]'"
        ) from e
    server = FastMCP("doctyze")
    for fn in _TOOLS:
        server.tool()(fn)
    _register_skill_prompts(server)
    return server


def _load_skill(path: Path) -> tuple[str, str, str]:
    """Return (name, description, body) for a SKILL.md — the playbook, minus frontmatter."""
    text = path.read_text(encoding="utf-8")
    name, description, body = path.parent.name, "", text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            front, body = parts[1], parts[2].lstrip("\n")
            for line in front.splitlines():
                if line.strip().startswith("description:"):
                    description = line.split(":", 1)[1].strip()
                    break
    return name, description, body


def _register_skill_prompts(server) -> None:
    """Expose each Doctyze skill as an MCP prompt so ANY MCP client (not just Claude
    Code) can invoke the guided playbook — served from the skill files, one source of truth."""
    from .distribute.fanout import package_skills_dir

    skills_dir = package_skills_dir()
    if not skills_dir.is_dir():
        return
    for d in sorted(skills_dir.iterdir()):
        skill = d / "SKILL.md"
        if not skill.is_file():
            continue
        name, description, body = _load_skill(skill)

        def make(text: str):
            def prompt() -> str:
                return text
            return prompt

        server.prompt(name=name, description=description or f"Doctyze: {name}")(make(body))


def main() -> None:  # pragma: no cover - entry point
    build_server().run()

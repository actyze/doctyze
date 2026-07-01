"""Wire the Doctyze MCP server into a project's IDE configs (one-command setup).

Writes project-level MCP config so whatever assistant you open the repo with —
Claude Code, Cursor, VS Code/Copilot — picks up Doctyze's tools + prompts. Project
scope is deliberate: it's safe (never touches global settings), committable (teammates
inherit it), and merge-preserving (won't clobber other servers you've configured).
"""
from __future__ import annotations

import json
from pathlib import Path

# Identical server everywhere; uvx fetches the published package on demand (no install).
_SERVER = {"command": "uvx", "args": ["--from", "doctyze[mcp]", "doctyze-mcp"]}


def _merge_json(path: Path, update) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8")) or {}
        except (json.JSONDecodeError, OSError):
            data = {}
    if not isinstance(data, dict):
        data = {}
    update(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def wire_mcp(root: str | Path) -> list[Path]:
    """Register the Doctyze MCP server in each IDE's project config. Idempotent."""
    root = Path(root).resolve()
    written: list[Path] = []

    # Claude Code (and any client that reads a project-root .mcp.json): mcpServers schema.
    def _mcp_servers(d: dict) -> None:
        d.setdefault("mcpServers", {})["doctyze"] = _SERVER

    # Cursor: .cursor/mcp.json, same mcpServers schema.
    for rel in (".mcp.json", ".cursor/mcp.json"):
        p = root / rel
        _merge_json(p, _mcp_servers)
        written.append(p)

    # VS Code / GitHub Copilot: .vscode/mcp.json uses a "servers" map with an explicit type.
    def _vscode(d: dict) -> None:
        d.setdefault("servers", {})["doctyze"] = {"type": "stdio", **_SERVER}

    p = root / ".vscode" / "mcp.json"
    _merge_json(p, _vscode)
    written.append(p)

    return written

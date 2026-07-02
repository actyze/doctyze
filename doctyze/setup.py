"""Wire the Doctyze MCP server into a project's IDE configs (one-command setup).

Writes **project-level** MCP config so whatever assistant you open the repo with picks
up Doctyze's tools + prompts. Project scope is deliberate: safe (never touches global
settings), committable (teammates inherit it), and merge-preserving (won't clobber
other servers). Config paths/schemas verified against each tool's official docs.

- Claude Code / generic : .mcp.json                (mcpServers, JSON)
- Cursor                : .cursor/mcp.json          (mcpServers, JSON)
- VS Code / Copilot     : .vscode/mcp.json          (servers, JSON, type=stdio)
- Codex CLI             : .codex/config.toml        ([mcp_servers.doctyze], TOML)  — if detected
- Gemini CLI            : .gemini/settings.json      (mcpServers, JSON)            — if detected

Windsurf and Cline only support a GLOBAL MCP config (no project scope), so we detect
them and report how to add the server there rather than editing global/fragile paths.
Both read AGENTS.md (written by `distribute`), so their playbook is already covered.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

# Identical server everywhere; uvx fetches the published package on demand (no install).
_SERVER = {"command": "uvx", "args": ["--from", "doctyze[mcp]", "doctyze-mcp"]}


def detect_agents() -> set[str]:
    """Best-effort detection of installed AI assistants (binary on PATH or config dir)."""
    home = Path.home()

    def has(binary: str) -> bool:
        return shutil.which(binary) is not None

    found: set[str] = set()
    if has("codex") or (home / ".codex").exists():
        found.add("codex")
    if has("gemini") or (home / ".gemini").exists():
        found.add("gemini")
    if (home / ".codeium" / "windsurf").exists() or has("windsurf"):
        found.add("windsurf")
    ext = home / ".vscode" / "extensions"
    if (ext.exists() and any(ext.glob("saoudrizwan.claude-dev-*"))) or (home / ".cline").exists():
        found.add("cline")
    return found


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


def _write_codex_toml(path: Path) -> None:
    """Codex uses TOML with a `[mcp_servers.<name>]` table. Append-if-absent (idempotent)."""
    block = (
        "[mcp_servers.doctyze]\n"
        'command = "uvx"\n'
        'args = ["--from", "doctyze[mcp]", "doctyze-mcp"]\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "[mcp_servers.doctyze]" in text:
            return
        prefix = text if text.endswith("\n") else text + "\n"
        path.write_text(prefix + "\n" + block, encoding="utf-8")
    else:
        path.write_text(block, encoding="utf-8")


def wire_mcp(root: str | Path, agents: set[str] | None = None) -> dict:
    """Register the Doctyze MCP server in each IDE's project config. Idempotent.

    Returns {"written": [Path, …], "global_only": [tool names detected that need
    a global MCP config, e.g. windsurf/cline]}.
    """
    root = Path(root).resolve()
    if agents is None:
        agents = detect_agents()
    written: list[Path] = []

    def mcp_servers(d: dict) -> None:
        d.setdefault("mcpServers", {})["doctyze"] = _SERVER

    def vscode(d: dict) -> None:
        d.setdefault("servers", {})["doctyze"] = {"type": "stdio", **_SERVER}

    # Baseline project configs (common assistants; harmless + committable).
    for rel in (".mcp.json", ".cursor/mcp.json"):
        p = root / rel
        _merge_json(p, mcp_servers)
        written.append(p)
    p = root / ".vscode" / "mcp.json"
    _merge_json(p, vscode)
    written.append(p)

    # Detected extras that support project-scoped MCP config.
    if "codex" in agents:
        p = root / ".codex" / "config.toml"
        _write_codex_toml(p)
        written.append(p)
    if "gemini" in agents:
        p = root / ".gemini" / "settings.json"
        _merge_json(p, mcp_servers)
        written.append(p)

    global_only = sorted(a for a in agents if a in ("windsurf", "cline"))
    return {"written": written, "global_only": global_only}

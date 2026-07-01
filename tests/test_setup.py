"""Tests for one-command MCP wiring (doctyze init / setup.wire_mcp)."""
from __future__ import annotations

import json
from pathlib import Path

from doctyze.setup import wire_mcp


def test_wire_mcp_writes_all_ide_configs(tmp_path: Path):
    written = wire_mcp(tmp_path)
    assert len(written) == 3
    assert {p.relative_to(tmp_path).as_posix() for p in written} == {
        ".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json",
    }

    # Claude Code + Cursor use the mcpServers schema
    for rel in (".mcp.json", ".cursor/mcp.json"):
        d = json.loads((tmp_path / rel).read_text())
        srv = d["mcpServers"]["doctyze"]
        assert srv["command"] == "uvx"
        assert "doctyze[mcp]" in srv["args"] and "doctyze-mcp" in srv["args"]

    # VS Code / Copilot use the "servers" schema with an explicit stdio type
    vs = json.loads((tmp_path / ".vscode" / "mcp.json").read_text())
    assert vs["servers"]["doctyze"]["type"] == "stdio"
    assert vs["servers"]["doctyze"]["command"] == "uvx"


def test_wire_mcp_preserves_existing_servers(tmp_path: Path):
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {"other": {"command": "x"}}}')
    wire_mcp(tmp_path)
    d = json.loads((tmp_path / ".mcp.json").read_text())
    assert "other" in d["mcpServers"] and "doctyze" in d["mcpServers"]


def test_wire_mcp_idempotent(tmp_path: Path):
    wire_mcp(tmp_path)
    first = (tmp_path / ".mcp.json").read_text()
    wire_mcp(tmp_path)
    assert (tmp_path / ".mcp.json").read_text() == first  # no duplication/drift

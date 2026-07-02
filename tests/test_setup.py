"""Tests for one-command MCP wiring (doctyze init / setup.wire_mcp)."""
from __future__ import annotations

import json
from pathlib import Path

from doctyze.setup import wire_mcp


def test_baseline_writes_common_ide_configs(tmp_path: Path):
    # no extra agents detected -> the three baseline project configs
    result = wire_mcp(tmp_path, agents=set())
    rels = {p.relative_to(tmp_path).as_posix() for p in result["written"]}
    assert rels == {".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"}
    assert result["global_only"] == []

    for rel in (".mcp.json", ".cursor/mcp.json"):
        srv = json.loads((tmp_path / rel).read_text())["mcpServers"]["doctyze"]
        assert srv["command"] == "uvx" and "doctyze[mcp]" in srv["args"]
    vs = json.loads((tmp_path / ".vscode" / "mcp.json").read_text())["servers"]["doctyze"]
    assert vs["type"] == "stdio"


def test_codex_and_gemini_wired_when_detected(tmp_path: Path):
    result = wire_mcp(tmp_path, agents={"codex", "gemini"})
    rels = {p.relative_to(tmp_path).as_posix() for p in result["written"]}
    assert ".codex/config.toml" in rels and ".gemini/settings.json" in rels

    # Codex is TOML with a [mcp_servers.doctyze] table
    toml = (tmp_path / ".codex" / "config.toml").read_text()
    assert "[mcp_servers.doctyze]" in toml and 'command = "uvx"' in toml
    # Gemini is JSON mcpServers
    gem = json.loads((tmp_path / ".gemini" / "settings.json").read_text())
    assert gem["mcpServers"]["doctyze"]["command"] == "uvx"


def test_windsurf_and_cline_reported_not_written(tmp_path: Path):
    result = wire_mcp(tmp_path, agents={"windsurf", "cline"})
    assert result["global_only"] == ["cline", "windsurf"]  # sorted, reported
    # global-only tools get NO project config written for them
    assert not (tmp_path / ".codeium").exists()


def test_preserves_existing_and_idempotent(tmp_path: Path):
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {"other": {"command": "x"}}}')
    wire_mcp(tmp_path, agents={"codex"})
    d = json.loads((tmp_path / ".mcp.json").read_text())
    assert "other" in d["mcpServers"] and "doctyze" in d["mcpServers"]

    codex_first = (tmp_path / ".codex" / "config.toml").read_text()
    wire_mcp(tmp_path, agents={"codex"})  # re-run
    assert (tmp_path / ".codex" / "config.toml").read_text() == codex_first  # no dup TOML table
    assert json.loads((tmp_path / ".mcp.json").read_text())["mcpServers"].keys() >= {"other", "doctyze"}

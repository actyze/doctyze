"""Release-readiness tests: MCP server, plugin manifests, skill sync."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import doctyze.mcp_server as m

ROOT = Path(__file__).resolve().parent.parent


def test_mcp_tools_run_without_mcp_dependency(tmp_path: Path):
    (tmp_path / "pom.xml").write_text("<p/>")
    assert "write-spec" in m.bootstrap(str(tmp_path))
    assert "fresh" in m.check_freshness(str(tmp_path)).lower()
    assert "Distributed" in m.distribute(str(tmp_path))


def test_build_server_requires_mcp_extra():
    try:
        import mcp  # noqa: F401
        pytest.skip("mcp installed; SystemExit path not exercised")
    except ImportError:
        pass
    with pytest.raises(SystemExit):
        m.build_server()


def test_plugin_manifests_valid():
    mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert mk["name"] and mk["plugins"][0]["name"] == "doctyze"
    pj = json.loads((ROOT / "plugins" / "doctyze" / ".claude-plugin" / "plugin.json").read_text())
    assert pj["name"] == "doctyze" and pj["license"] == "Apache-2.0"
    mcpj = json.loads((ROOT / "plugins" / "doctyze" / ".mcp.json").read_text())
    assert "doctyze" in mcpj["mcpServers"]


def test_plugin_skills_match_canonical():
    """Plugin skills must be byte-identical to the canonical source (run sync script)."""
    canon_dir = ROOT / "doctyze" / "skills"
    plug_dir = ROOT / "plugins" / "doctyze" / "skills"
    canon = {p.relative_to(canon_dir): p.read_text() for p in canon_dir.glob("*/SKILL.md")}
    plug = {p.relative_to(plug_dir): p.read_text() for p in plug_dir.glob("*/SKILL.md")}
    assert len(canon) >= 6
    assert canon.keys() == plug.keys(), "skill set differs — run scripts/sync-plugin-skills.sh"
    drifted = [str(k) for k in canon if canon[k] != plug[k]]
    assert not drifted, f"plugin copy stale for {drifted} — run scripts/sync-plugin-skills.sh"

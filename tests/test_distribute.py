"""M3 tests: skill fan-out to agent files."""
from __future__ import annotations

from pathlib import Path

from doctyze.distribute.fanout import distribute


def _fake_skill(src: Path, name: str) -> None:
    d = src / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n# {name}\n")


def test_distribute_builtin_writes_all_formats(tmp_path: Path):
    src = tmp_path / "src_skills"
    _fake_skill(src, "write-spec")
    root = tmp_path / "repo"
    root.mkdir()

    distribute(root, skills_src=src)
    assert (root / ".claude" / "skills" / "write-spec" / "SKILL.md").exists()
    assert (root / ".cursor" / "rules" / "write-spec.md").exists()
    agents = (root / "AGENTS.md").read_text()
    assert "doctyze:start" in agents and "write-spec" in agents


def test_distribute_idempotent_agents_block(tmp_path: Path):
    src = tmp_path / "s"
    _fake_skill(src, "write-adr")
    root = tmp_path / "r"
    root.mkdir()
    distribute(root, skills_src=src)
    distribute(root, skills_src=src)  # twice
    agents = (root / "AGENTS.md").read_text()
    assert agents.count("doctyze:start") == 1  # single managed block, not duplicated


def test_distribute_real_package_skills(tmp_path: Path):
    written = distribute(tmp_path)  # uses the shipped doctyze/skills
    assert any(p.name == "SKILL.md" for p in written)
    agents = (tmp_path / "AGENTS.md").read_text()
    assert "doctyze" in agents and "write-spec" in agents

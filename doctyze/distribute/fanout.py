"""Fan the canonical Doctyze skills out to every agent file format (deterministic).

Default built-in fan-out (no external dep): writes Claude Code skills, Cursor
rules, and an AGENTS.md managed block. `ruler` can be used instead when present,
but isn't required. Idempotent.
"""
from __future__ import annotations

import re
from pathlib import Path

_START = "<!-- doctyze:start -->"
_END = "<!-- doctyze:end -->"


def package_skills_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills"


def _read_skills(src: Path):
    for d in sorted(src.iterdir()):
        sk = d / "SKILL.md"
        if d.is_dir() and sk.exists():
            yield d.name, sk.read_text(encoding="utf-8")


def distribute(root: str | Path, skills_src: str | Path | None = None) -> list[Path]:
    root = Path(root).resolve()
    src = Path(skills_src) if skills_src else package_skills_dir()
    written: list[Path] = []
    names: list[str] = []

    for name, content in _read_skills(src):
        names.append(name)
        cc = root / ".claude" / "skills" / name / "SKILL.md"
        cc.parent.mkdir(parents=True, exist_ok=True)
        cc.write_text(content, encoding="utf-8")
        written.append(cc)

        cur = root / ".cursor" / "rules" / f"{name}.md"
        cur.parent.mkdir(parents=True, exist_ok=True)
        cur.write_text(content, encoding="utf-8")
        written.append(cur)

    written.append(_write_agents_section(root / "AGENTS.md", names))
    return written


def _write_agents_section(agents_path: Path, names: list[str]) -> Path:
    block = (
        f"{_START}\n## Doctyze skills\n"
        "This repo uses Doctyze. Skills available to your agent:\n"
        + "".join(f"- `{n}`\n" for n in names)
        + _END
    )
    if agents_path.exists():
        text = agents_path.read_text(encoding="utf-8")
        if _START in text and _END in text:
            text = re.sub(re.escape(_START) + ".*?" + re.escape(_END), block, text, flags=re.S)
        else:
            text = text.rstrip() + "\n\n" + block + "\n"
    else:
        text = "# AGENTS.md\n\n" + block + "\n"
    agents_path.write_text(text, encoding="utf-8")
    return agents_path

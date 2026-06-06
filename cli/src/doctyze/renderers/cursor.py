"""Cursor rules renderer.

Reads canonical `docs/skills/*.md` and writes `.cursor/rules/<name>.md`. Cursor
auto-loads anything in `.cursor/rules/` as project context.
"""
from __future__ import annotations

from pathlib import Path

from doctyze.renderers.base import CanonicalDoc, Renderer, collect_canonical


class CursorRenderer(Renderer):
    name = "cursor"
    description = "Cursor — .cursor/rules/<name>.md (one file per canonical skill)"

    def render(self, repo_root: Path, *, dry_run: bool = False) -> list[Path]:
        skills = collect_canonical(repo_root, "skills")
        written: list[Path] = []
        for skill in skills:
            target = repo_root / ".cursor" / "rules" / f"{skill.name}.md"
            content = self._build_rule(skill)
            written.append(self._write(target, content, dry_run))
        return written

    def _build_rule(self, skill: CanonicalDoc) -> str:
        banner = self._generated_banner(f"docs/skills/{skill.path.name}")
        # Cursor reads plain markdown — frontmatter is harmless but not required.
        # Pass through the body with a banner; keep the H1 if present.
        body = skill.body.lstrip()
        return banner + body

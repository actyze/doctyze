"""Windsurf rules renderer.

Windsurf reads a single `.windsurfrules` file at the repo root. Like Copilot,
we concatenate the canonical skills with dividers.
"""
from __future__ import annotations

from pathlib import Path

from doctyze.renderers.base import Renderer, collect_canonical


class WindsurfRenderer(Renderer):
    name = "windsurf"
    description = "Windsurf — .windsurfrules (single concatenated file)"

    def render(self, repo_root: Path, *, dry_run: bool = False) -> list[Path]:
        skills = collect_canonical(repo_root, "skills")
        target = repo_root / ".windsurfrules"
        banner = self._generated_banner("docs/skills/*.md")
        if not skills:
            content = banner + (
                "# Project rules for Windsurf\n\n"
                "No canonical skills under `docs/skills/` yet. "
                "Also read `AGENTS.md` at the repo root.\n"
            )
            return [self._write(target, content, dry_run)]

        sections: list[str] = [
            "# Project rules for Windsurf\n",
            "Canonical source: `docs/skills/`. Also see `AGENTS.md`.\n\n",
        ]
        for skill in skills:
            title = skill.frontmatter.get("name") or skill.path.stem
            description = skill.frontmatter.get("description", "")
            sections.append(f"## {title}\n")
            if description:
                sections.append(f"\n_{description}_\n\n")
            sections.append(skill.body.strip() + "\n\n---\n\n")
        content = banner + "".join(sections).rstrip() + "\n"
        return [self._write(target, content, dry_run)]

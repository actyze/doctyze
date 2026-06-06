"""GitHub Copilot instructions renderer.

Copilot reads a single file at `.github/copilot-instructions.md`. We concatenate
every canonical skill into that one file with clear section dividers.
"""
from __future__ import annotations

from pathlib import Path

from doctyze.renderers.base import Renderer, collect_canonical


class CopilotRenderer(Renderer):
    name = "copilot"
    description = "GitHub Copilot — .github/copilot-instructions.md (single concatenated file)"

    def render(self, repo_root: Path, *, dry_run: bool = False) -> list[Path]:
        skills = collect_canonical(repo_root, "skills")
        target = repo_root / ".github" / "copilot-instructions.md"
        if not skills:
            # If there are no canonical skills, still produce a small stub so
            # Copilot finds the AGENTS.md pointer.
            content = self._build_stub(repo_root)
        else:
            content = self._build_combined(skills)
        return [self._write(target, content, dry_run)]

    def _build_combined(self, skills: list) -> str:
        banner = self._generated_banner("docs/skills/*.md")
        header = (
            "# Copilot instructions for this repository\n\n"
            "This file is the concatenated view of every canonical skill in\n"
            "`docs/skills/`. For full context, also read `AGENTS.md` at the\n"
            "repository root.\n\n"
            "---\n\n"
        )
        sections: list[str] = []
        for skill in skills:
            title = skill.frontmatter.get("name") or skill.path.stem
            description = skill.frontmatter.get("description", "")
            sections.append(
                f"## Skill: `{title}`\n\n"
                f"_{description}_\n\n" if description else f"## Skill: `{title}`\n\n"
            )
            sections.append(skill.body.strip() + "\n\n---\n\n")
        return banner + header + "".join(sections).rstrip() + "\n"

    def _build_stub(self, repo_root: Path) -> str:
        banner = self._generated_banner("docs/skills/ (empty)")
        return (
            banner
            + "# Copilot instructions for this repository\n\n"
            "No canonical skills are defined yet under `docs/skills/`.\n"
            "Also read `AGENTS.md` at the repository root for project context.\n"
        )

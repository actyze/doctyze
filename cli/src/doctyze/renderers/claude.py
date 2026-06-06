"""Claude Code skills renderer.

Reads canonical `docs/skills/*.md` and writes `.claude/skills/<name>/SKILL.md`
in Claude Code's expected layout. Each skill becomes its own subdirectory so
the skill can later carry references/scripts/examples alongside SKILL.md.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from doctyze.renderers.base import CanonicalDoc, Renderer, collect_canonical


class ClaudeRenderer(Renderer):
    name = "claude"
    description = "Claude Code (Anthropic) — .claude/skills/<name>/SKILL.md"

    def render(self, repo_root: Path, *, dry_run: bool = False) -> list[Path]:
        skills = collect_canonical(repo_root, "skills")
        written: list[Path] = []
        for skill in skills:
            target = repo_root / ".claude" / "skills" / skill.name / "SKILL.md"
            content = self._build_skill_md(skill)
            written.append(self._write(target, content, dry_run))
        return written

    def _build_skill_md(self, skill: CanonicalDoc) -> str:
        """Claude Code SKILL.md format: YAML frontmatter (name + description)
        followed by the markdown body. The canonical frontmatter is already in
        this shape — we pass it through, adding the generated banner."""
        # Claude Code requires `name` and `description` in frontmatter
        fm = dict(skill.frontmatter)
        fm.setdefault("name", skill.path.stem)
        if "description" not in fm:
            fm["description"] = self._infer_description(skill.body)
        fm_yaml = yaml.safe_dump(fm, sort_keys=False).strip()
        banner = self._generated_banner(f"docs/skills/{skill.path.name}")
        return f"---\n{fm_yaml}\n---\n\n{banner}{skill.body}"

    @staticmethod
    def _infer_description(body: str) -> str:
        """If the canonical skill has no description, lift the first non-header
        sentence as a best-effort placeholder."""
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line[:200]
        return "TODO: add a description"

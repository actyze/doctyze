"""Create the canonical docs/ structure with anchored index files (deterministic).

This lays down the skeleton the agent then fills. Idempotent: never overwrites
an existing file.
"""
from __future__ import annotations

import datetime
from pathlib import Path

from ..config import SECTIONS
from ..freshness.anchors import render_frontmatter
from ..model import Anchor


def ensure_structure(root: str | Path) -> list[Path]:
    """Create canonical dirs + an anchored index.md per scaffolded section.

    Derives sections from the single SECTIONS registry. Idempotent. Returns
    created files.
    """
    root = Path(root).resolve()
    today = datetime.date.today().isoformat()
    created: list[Path] = []
    for key, section in SECTIONS.items():
        if not section.scaffold:
            continue
        d = root / section.path
        d.mkdir(parents=True, exist_ok=True)
        index = d / "index.md"
        if index.exists():
            continue
        anchor = Anchor(artifact=section.kind, generated_by="bootstrap", last_verified=today)
        index.write_text(
            render_frontmatter(anchor) + f"\n# {key.title()}\n\n{section.blurb}\n",
            encoding="utf-8",
        )
        created.append(index)
    return created

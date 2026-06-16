"""Turn stale-doc findings into a refresh request for the existing agent.

Doctyze doesn't rewrite docs itself (no LLM). It records which docs are stale and
which skill regenerates each; the agent does the rewriting.
"""
from __future__ import annotations

from pathlib import Path

from ..model import Anchor


def write_refresh_manifest(root: str | Path, stale: list[tuple[Path, Anchor, list[str]]]) -> Path:
    root = Path(root).resolve()
    lines = [
        "# Docs needing refresh",
        "",
        "These docs are anchored to code that changed. Re-run the listed skill to",
        "refresh each — your agent does the writing, grounded in the new code.",
        "",
        "| Doc | Regenerate with | Changed files |",
        "|---|---|---|",
    ]
    for f, anchor, matched in stale:
        rel = Path(f).relative_to(root)
        skill = anchor.generated_by or "(unknown skill)"
        shown = ", ".join(matched[:3]) + (" …" if len(matched) > 3 else "")
        lines.append(f"| `{rel}` | `{skill}` | {shown} |")
    out = root / ".doctyze" / "refresh-needed.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out

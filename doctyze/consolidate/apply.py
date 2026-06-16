"""Apply a MigrationPlan non-destructively: git-mv where possible, fix links, idempotent."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from .audit import discover
from ..model import MigrationPlan

_LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")
_SKIP_LINK_PREFIXES = ("http://", "https://", "#", "mailto:", "tel:")


def _git_mv(src: Path, dst: Path, root: Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(root), "mv", str(src), str(dst)],
            capture_output=True, text=True,
        )
        return r.returncode == 0
    except (OSError, FileNotFoundError):
        return False


def apply_plan(root: str | Path, plan: MigrationPlan) -> dict[Path, Path]:
    """Execute the plan. Returns {old_abs -> new_abs}. Safe to re-run (idempotent)."""
    root = Path(root).resolve()
    moved: dict[Path, Path] = {}

    for op in plan.ops:
        src = Path(op.src).resolve()
        dst = Path(op.dst).resolve()
        if dst.exists() and not src.exists():
            continue  # already applied
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            continue  # don't overwrite; non-destructive
        if not _git_mv(src, dst, root):
            shutil.move(str(src), str(dst))
        moved[src] = dst

    if moved:
        _fix_links(root, moved)
    return moved


def _fix_links(root: Path, moved: dict[Path, Path]) -> None:
    """Rewrite relative markdown links that pointed at moved files.

    Links were authored relative to each referencing file's ORIGINAL location, so
    we resolve against that original dir, then re-relativize from the file's
    current dir to the moved target's new location.
    """
    inv = {new: old for old, new in moved.items()}  # current path -> original path

    for f in discover(root):
        f = f.resolve()
        orig_dir = inv.get(f, f).parent
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        def repl(m: re.Match) -> str:
            target = m.group(2)
            if target.startswith(_SKIP_LINK_PREFIXES):
                return m.group(0)
            path_part, sep, anchor = target.partition("#")
            if not path_part:
                return m.group(0)
            old_target = (orig_dir / path_part).resolve()
            if old_target not in moved:
                return m.group(0)
            new_target = moved[old_target]
            try:
                rel = Path(os.path.relpath(new_target, f.parent))
            except ValueError:
                return m.group(0)
            return f"{m.group(1)}{rel.as_posix()}{sep}{anchor}{m.group(3)}"

        new_text = _LINK_RE.sub(repl, text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")

"""Affected-docs detection: which anchored docs are stale given changed code.

Deterministic and self-contained — uses the freshness anchors + git diff. This is
the "affected docs" primitive: nobody else maps a code change to the specific
docs it invalidates via declared anchors. (fiberplane/drift is an optional
alternative; not required.)
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..consolidate.audit import discover
from ..model import Anchor
from .anchors import parse_anchor


def _glob_to_re(pattern: str) -> re.Pattern:
    pattern = pattern.replace("\\", "/")
    out = []
    k = 0
    while k < len(pattern):
        if pattern[k:k + 2] == "**":
            out.append(".*")
            k += 2
        elif pattern[k] == "*":
            out.append("[^/]*")
            k += 1
        elif pattern[k] == "?":
            out.append("[^/]")
            k += 1
        else:
            out.append(re.escape(pattern[k]))
            k += 1
    return re.compile("^" + "".join(out) + "$")


def matches(pattern: str, path: str) -> bool:
    return _glob_to_re(pattern).match(path.replace("\\", "/")) is not None


def changed_files(root: str | Path, *, staged: bool = False, base: str = "HEAD") -> list[str]:
    args = ["git", "-C", str(root), "diff", "--name-only"]
    args.append("--cached" if staged else base)
    try:
        r = subprocess.run(args, capture_output=True, text=True)
    except (OSError, FileNotFoundError):
        return []
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def find_stale(root: str | Path, changed: list[str]) -> list[tuple[Path, Anchor, list[str]]]:
    """Return [(doc_path, anchor, matched_changed_files)] for docs invalidated by `changed`."""
    root = Path(root).resolve()
    changed = [c.replace("\\", "/") for c in changed]
    stale: list[tuple[Path, Anchor, list[str]]] = []
    for f in discover(root):
        try:
            anchor = parse_anchor(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if not anchor or not anchor.affects:
            continue
        matched = [c for c in changed if any(matches(p, c) for p in anchor.affects)]
        if matched:
            stale.append((f.resolve(), anchor, matched))
    return stale

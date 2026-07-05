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
        if pattern[k:k + 3] == "**/":
            out.append("(?:.*/)?")   # zero or more dir segments (so **/x matches root x)
            k += 3
        elif pattern[k:k + 2] == "**":
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


class GitDiffError(RuntimeError):
    """`git diff` failed — e.g. an explicitly requested base ref can't be resolved.

    Raised only for an explicit `base` (the CI gate path) so the caller can fail
    *closed*; the local working-tree/staged default stays tolerant (returns []).
    """


def changed_files(root: str | Path, *, staged: bool = False, base: str = "HEAD") -> list[str]:
    ref = "--cached" if staged else base
    # For an explicit base ref (CI: a PR branch vs its target), use merge-base
    # (three-dot) semantics so only *this branch's* changes count — not files the
    # base advanced independently after the fork. `..`/`...` given by the user is
    # respected as-is; the local working-tree default (HEAD) is left untouched.
    if not staged and base != "HEAD" and ".." not in base:
        ref = f"{base}...HEAD"
    args = ["git", "-C", str(root), "diff", "--name-only", ref]
    try:
        r = subprocess.run(args, capture_output=True, text=True)
    except OSError:
        return []   # git not available at all — can't compare, stay tolerant
    if r.returncode != 0:
        # Fail *closed* for an explicit base ref (the CI gate), so a green check
        # never means "unresolvable ref". Stay tolerant for the local default,
        # where "nothing to compare" (no repo / no HEAD) is benign.
        if not staged and base != "HEAD":
            raise GitDiffError(
                f"git diff against '{base}' failed (exit {r.returncode}): "
                f"{r.stderr.strip() or 'unknown error'}. In CI, fetch full history "
                f"(e.g. fetch-depth: 0) and make sure the base ref is fetched."
            )
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

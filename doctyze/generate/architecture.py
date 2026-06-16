"""Adapter for CodeBoarding — generates architecture docs + Mermaid diagrams.

Optional and gracefully degrading: if CodeBoarding isn't installed, return None
and let the agent produce the diagrams instead (it can read code and emit
Mermaid directly). Doctyze never hard-depends on it.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..config import CANONICAL_LAYOUT


def is_available() -> bool:
    """True if a CodeBoarding CLI is on PATH."""
    return shutil.which("codeboarding") is not None


def run_codeboarding(root: str | Path, timeout: int = 600) -> list[Path] | None:
    """Run CodeBoarding to emit diagrams into docs/architecture/diagrams/.

    Returns the list of produced files, or None if CodeBoarding is unavailable or
    fails (caller should then fall back to agent-generated diagrams).
    """
    root = Path(root).resolve()
    if not is_available():
        return None
    out = root / CANONICAL_LAYOUT["diagrams"]
    out.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            ["codeboarding", "--output", str(out), str(root)],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return sorted(out.glob("*.md")) + sorted(out.glob("*.mmd"))

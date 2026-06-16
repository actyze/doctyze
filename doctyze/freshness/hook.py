"""Install a warn-first pre-commit hook that runs the freshness check.

Per ADR-0003, enforcement is warn-first: the hook reports stale docs but never
blocks the commit. Portable POSIX sh; on Windows, Git's bundled sh runs it.
"""
from __future__ import annotations

from pathlib import Path

_HOOK = """#!/bin/sh
# Doctyze freshness check (warn-only — never blocks a commit).
command -v doctyze >/dev/null 2>&1 && doctyze watch --staged || true
exit 0
"""


def install_hook(root: str | Path) -> Path | None:
    root = Path(root).resolve()
    git_dir = root / ".git"
    if not git_dir.is_dir():
        return None
    hooks = git_dir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"
    hook.write_text(_HOOK, encoding="utf-8")
    hook.chmod(0o755)
    return hook

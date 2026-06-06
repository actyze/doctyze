"""Vendor-specific renderers.

Canonical content lives in `docs/skills/` (markdown + YAML frontmatter) and
`docs/runbooks/` (markdown with frontmatter). Renderers transform these into
vendor-native formats: Claude Code, Cursor, Copilot, Windsurf, HolmesGPT, etc.

Add a new renderer by subclassing :class:`Renderer` and registering it in
:data:`REGISTRY`.
"""
from __future__ import annotations

from doctyze.renderers.base import Renderer
from doctyze.renderers.claude import ClaudeRenderer
from doctyze.renderers.copilot import CopilotRenderer
from doctyze.renderers.cursor import CursorRenderer
from doctyze.renderers.holmes import HolmesRenderer
from doctyze.renderers.windsurf import WindsurfRenderer


REGISTRY: dict[str, type[Renderer]] = {
    "claude": ClaudeRenderer,
    "cursor": CursorRenderer,
    "copilot": CopilotRenderer,
    "windsurf": WindsurfRenderer,
    "holmes": HolmesRenderer,
}


def get(name: str) -> Renderer:
    """Look up a renderer by name (case-insensitive)."""
    key = name.lower()
    if key not in REGISTRY:
        raise KeyError(
            f"unknown renderer: {name!r}. "
            f"Known: {sorted(REGISTRY)}"
        )
    return REGISTRY[key]()


__all__ = ["Renderer", "REGISTRY", "get"]

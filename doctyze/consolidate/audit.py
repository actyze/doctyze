"""Audit: discover every documentation file in a repo and classify it.

Deterministic, heuristic first pass — no LLM. The agent-run skill can refine the
classification afterward; this gives a solid, reviewable starting point.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path

from ..model import ArtifactKind, DocFile

DOC_EXTS = {".md", ".mdx", ".rst", ".adoc"}

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", "target",
    "__pycache__", ".archive", ".pytest_cache", ".idea", ".mypy_cache",
    ".doctyze",  # Doctyze's own working files (plans, state) — never consolidate these
}

# Standard repo files that always stay where they are (root convention files).
STANDARD_STEMS = {
    "README", "CONTRIBUTING", "CODE_OF_CONDUCT", "SECURITY", "CHANGELOG",
    "LICENSE", "NOTICE", "MAINTAINERS", "GOVERNANCE",
}

AGENT_CONTEXT_DIRS = {".cursor", ".claude", ".github", ".holmes", ".windsurf"}
AGENT_CONTEXT_NAMES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "copilot-instructions.md"}


def discover(root: Path):
    """Yield every doc file under root, skipping noise/vendor directories."""
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.startswith("_"):
                continue  # convention: _-prefixed are meta/working files, not content
            p = Path(dirpath) / fn
            if p.suffix.lower() in DOC_EXTS:
                yield p


def _has(name: str, *needles: str) -> bool:
    low = name.lower()
    return any(n in low for n in needles)


def classify(path: Path, root: Path) -> ArtifactKind:
    rel = path.relative_to(root)
    parts = [p.lower() for p in rel.parts]
    stem = path.stem
    name = path.name

    # Agent context files/dirs are managed by `distribute`, not consolidated.
    if any(p in AGENT_CONTEXT_DIRS for p in rel.parts) or name in AGENT_CONTEXT_NAMES:
        return ArtifactKind.AGENT_CONTEXT

    # READMEs and standard root files stay in place.
    if stem.upper().startswith("README"):
        return ArtifactKind.KEEP_IN_PLACE
    if len(rel.parts) == 1 and stem.upper() in STANDARD_STEMS:
        return ArtifactKind.KEEP_IN_PLACE

    # Path-based (already-organized docs/ trees).
    if "decisions" in parts:
        return ArtifactKind.ADR
    if "archive" in parts:
        return ArtifactKind.STALE
    if "specs" in parts:
        return ArtifactKind.SPEC
    if "runbooks" in parts:
        return ArtifactKind.RUNBOOK
    if "observability" in parts or "investigations" in parts:
        return ArtifactKind.OBSERVABILITY
    if "skills" in parts:
        return ArtifactKind.SKILL
    if "diagrams" in parts:  # must precede 'architecture' (diagrams live under it)
        return ArtifactKind.DIAGRAM
    if "architecture" in parts:
        return ArtifactKind.ARCHITECTURE

    # Stale hints by name (explicit, or an old year in the filename).
    if _has(name, "deprecated", "-old", "old-", "outdated", "draft-"):
        return ArtifactKind.STALE
    for token in name.replace("_", "-").split("-"):
        if token.isdigit() and len(token) == 4 and 2000 <= int(token) <= datetime.date.today().year - 2:
            return ArtifactKind.STALE

    # Filename hints.
    if _has(name, "adr", "decision-record"):
        return ArtifactKind.ADR
    if _has(name, "runbook", "incident", "deploy", "oncall", "on-call", "rollback",
            "operational", "operations", "playbook", "disaster", "failover"):
        return ArtifactKind.RUNBOOK
    # NOTE: use "logging" (not "log") so "changelog" doesn't match here.
    if _has(name, "postmortem", "post-mortem", "investigation", "rca", "logging",
            "observability", "monitor", "monitoring", "metrics", "telemetry",
            "tracing", "alerting"):
        return ArtifactKind.OBSERVABILITY
    if _has(name, "standards", "convention", "guideline", "style-guide", "styleguide", "best-practice", "how-to", "howto"):
        return ArtifactKind.GUIDE
    if _has(name, "architecture", "design", "c4", "overview", "diagram"):
        return ArtifactKind.ARCHITECTURE
    if _has(name, "spec", "requirements", "openapi", "api", "feature"):
        return ArtifactKind.SPEC

    # Loose working docs (e.g. US_1234_PLAN.md) default to spec material.
    if len(rel.parts) == 1 or "docs" in parts:
        return ArtifactKind.SPEC
    # A README-less doc sitting next to code (e.g. component-tests/notes.md): keep local.
    return ArtifactKind.KEEP_IN_PLACE


def audit_docs(root: str | Path) -> list[DocFile]:
    root = Path(root).resolve()
    docs = [DocFile(path=str(p), kind=classify(p, root)) for p in discover(root)]
    docs.sort(key=lambda d: d.path)
    return docs

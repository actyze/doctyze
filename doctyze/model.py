"""Core types shared across consolidate / generate / freshness."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ArtifactKind(str, Enum):
    SPEC = "spec"
    FUNCTIONAL_SPEC = "functional_spec"  # product-owner-facing: user stories + acceptance criteria
    ADR = "adr"
    RUNBOOK = "runbook"
    ARCHITECTURE = "architecture"
    DIAGRAM = "diagram"
    SKILL = "skill"
    OBSERVABILITY = "observability"
    GUIDE = "guide"  # coding/testing standards, conventions, how-to guides
    AGENT_CONTEXT = "agent_context"  # AGENTS.md / CLAUDE.md / .cursor rules
    KEEP_IN_PLACE = "keep_in_place"  # local README next to code
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass
class DocFile:
    """A documentation file discovered during audit."""

    path: str
    kind: ArtifactKind = ArtifactKind.UNKNOWN


@dataclass
class Anchor:
    """The freshness contract embedded in a generated doc's frontmatter.

    `affects` is the set of code globs that, when changed, make this doc stale.
    """

    artifact: ArtifactKind
    affects: list[str] = field(default_factory=list)  # globs whose change makes this doc stale
    generated_by: str | None = None
    last_verified: str | None = None


@dataclass
class MigrationOp:
    """One step in a consolidation plan. Non-destructive: move/archive, never delete."""

    action: str  # "move" | "archive" | "fix-links" | "renumber"
    src: str
    dst: str | None = None
    reason: str = ""


@dataclass
class MigrationPlan:
    ops: list[MigrationOp] = field(default_factory=list)

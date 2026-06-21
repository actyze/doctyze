"""Canonical docs/ taxonomy — the single source of truth for where artifacts live.

Consolidation (where to move scattered docs) and generation (where to write new
docs) both derive their paths from SECTIONS here. Do not redefine the taxonomy
elsewhere — derive from SECTIONS.
"""
from __future__ import annotations

from dataclasses import dataclass

from .model import ArtifactKind


@dataclass(frozen=True)
class Section:
    path: str           # location under the repo root
    kind: ArtifactKind  # artifact kind anchored in this section
    blurb: str          # one-line description for the scaffolded index
    scaffold: bool = True   # whether `bootstrap` creates an index.md here


# The canonical docs/ taxonomy. One entry per section.
SECTIONS: dict[str, Section] = {
    "specs":         Section("docs/specs", ArtifactKind.SPEC,
                             "Feature specifications — what each capability does."),
    "architecture":  Section("docs/architecture", ArtifactKind.ARCHITECTURE,
                             "System architecture: components, boundaries, integrations."),
    "diagrams":      Section("docs/architecture/diagrams", ArtifactKind.DIAGRAM,
                             "Architecture & integration diagrams (Mermaid)."),
    "decisions":     Section("docs/architecture/decisions", ArtifactKind.ADR,
                             "Architecture Decision Records (MADR)."),
    "runbooks":      Section("docs/runbooks", ArtifactKind.RUNBOOK,
                             "Operational runbooks, including deployment."),
    "observability": Section("docs/observability", ArtifactKind.OBSERVABILITY,
                             "Incident investigations, metrics, logging, alerting."),
    "skills":        Section("docs/skills", ArtifactKind.SKILL,
                             "Generated dev/testing skills.", scaffold=False),
    "archive":       Section("docs/archive", ArtifactKind.STALE,
                             "Archived / superseded docs.", scaffold=False),
}

# Derived views — the only places these are needed; both come from SECTIONS.
CANONICAL_LAYOUT: dict[str, str] = {key: s.path for key, s in SECTIONS.items()}

# Artifact kind -> canonical move target, for the consolidator. Includes
# 'diagrams' so diagram files under docs/architecture/diagrams/ are recognized as
# already-canonical (and stray diagrams move there) rather than pulled up to
# docs/architecture/.
KIND_TO_DIR: dict[ArtifactKind, str] = {
    s.kind: s.path
    for key, s in SECTIONS.items()
    if key in ("specs", "decisions", "runbooks", "architecture", "diagrams", "observability", "skills")
}

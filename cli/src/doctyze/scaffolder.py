"""Scaffolder — copies the canonical template into the user's repo.

Produces a plan first (read-only), then writes when confirmed. Every
generated artifact is stamped with an initial confidence marker; LLM-driven
extraction (in :mod:`doctyze.extractor`) fills the placeholders afterward and
can revise the markers based on extracted confidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from doctyze.detector import MODERN_STACKS


@dataclass(frozen=True)
class PlanEntry:
    relpath: Path
    kind: str
    confidence_marker: str


class Scaffolder:
    def __init__(self, repo: Path, stack: str) -> None:
        self.repo = repo
        self.stack = stack
        self.family = "modern" if stack in MODERN_STACKS else "legacy"
        self.template_root = self._locate_template_root()

    def _locate_template_root(self) -> Path:
        """Find the template directory next to this package.

        Doctyze ships templates inside the source distribution; in dev mode
        they live in <repo>/templates/<family>/.
        """
        # In dev: cli/src/doctyze/scaffolder.py → up 3 → repo root → templates/
        here = Path(__file__).resolve()
        candidate = here.parents[3] / "templates" / self.family
        if candidate.is_dir():
            return candidate
        # Installed package layout: templates packaged inside doctyze/
        packaged = here.parent / "templates" / self.family
        if packaged.is_dir():
            return packaged
        raise FileNotFoundError(
            f"Could not locate templates for family '{self.family}'. "
            f"Looked at {candidate} and {packaged}."
        )

    def plan(self) -> list[PlanEntry]:
        """Compute the list of files to be generated."""
        entries: list[PlanEntry] = []
        for src in self._iter_template_files():
            rel = src.relative_to(self.template_root)
            target_rel = self._target_path(rel)
            kind = self._classify(rel)
            marker = self._confidence_for(rel)
            entries.append(
                PlanEntry(relpath=target_rel, kind=kind, confidence_marker=marker)
            )
        return entries

    def write(self, plan: list[PlanEntry]) -> None:
        """Materialize the plan onto disk."""
        for entry in plan:
            target = self.repo / entry.relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            src = self._source_for(entry.relpath)
            content = src.read_text()
            # Strip the ".template" suffix on rename
            target.write_text(content)

    # ── internals ─────────────────────────────────────────────────────

    def _iter_template_files(self):
        for p in self.template_root.rglob("*"):
            if p.is_file():
                yield p

    def _target_path(self, rel: Path) -> Path:
        """Map a template path to the target path in the user's repo.

        Strips the `.template` suffix so `AGENTS.md.template` becomes
        `AGENTS.md` and `.sh.template` becomes `.sh`.
        """
        s = str(rel)
        if s.endswith(".template"):
            s = s[: -len(".template")]
        return Path(s)

    def _source_for(self, target_rel: Path) -> Path:
        """Find the source template file for a target path."""
        candidates = [
            self.template_root / target_rel,
            self.template_root / f"{target_rel}.template",
        ]
        for c in candidates:
            if c.exists():
                return c
        raise FileNotFoundError(f"no source template for {target_rel}")

    def _classify(self, rel: Path) -> str:
        """Map a template path to a human-readable artifact kind.

        Vendor-output paths (.claude/, .cursor/, .holmes/, .windsurfrules,
        .github/copilot-instructions.md) are intentionally absent — those
        are produced by :mod:`doctyze.renderers` from canonical sources,
        not scaffolded directly.
        """
        s = str(rel)
        if s.startswith("docs/architecture/decisions/"):
            return "ADR"
        if s.startswith("docs/architecture/diagrams/"):
            return "diagram"
        if s.startswith("docs/skills/"):
            return "skill (canonical)"
        if s.startswith("docs/runbooks/"):
            return "runbook (canonical)"
        if s.startswith("docs/specs/"):
            return "spec"
        if s.startswith("docs/investigations/"):
            return "investigation"
        if s.startswith("docs/api/"):
            return "API contract"
        if s.startswith("docs/data/"):
            return "data catalog"
        if s.startswith("docs/programs/"):
            return "program doc"
        if s.startswith("docs/jobs/"):
            return "job doc"
        if s.startswith("docs/interfaces/"):
            return "interface doc"
        if s.startswith(".github/workflows/"):
            return "GitHub Action"
        if s == "AGENTS.md.template" or s == "AGENTS.md":
            return "AGENTS.md"
        if s == "README.md":
            return "README"
        if s.startswith("tools/"):
            return "ingestion tool"
        return "other"

    def _confidence_for(self, rel: Path) -> str:
        """Initial confidence marker for a generated file.

        Most artifacts ship as 🟡 INFERRED so the LLM extractor knows to fill
        them, or 🔴 GAP where human input is required (e.g., ADR archaeology
        pending-questions). ADR-0001 is self-evidently 🟢 CONFIRMED (the act
        of having an ADRs folder *is* the decision the ADR describes).
        """
        s = str(rel)
        if "0001-record-architecture-decisions" in s:
            return "🟢"
        if "pending-questions" in s or "adr-archaeology" in s:
            return "🔴"
        return "🟡"

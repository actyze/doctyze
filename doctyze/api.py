"""Service layer — the single implementation of each job.

Both the CLI (`cli.py`) and the MCP server (`mcp_server.py`) are thin presenters
over these functions, so the two entry points can't drift. Functions return
structured data; callers do their own formatting/echoing.

Imports of the job packages are local so the package still imports cheaply and
with no optional deps at module load.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import Anchor, DocFile, MigrationPlan


@dataclass
class ConsolidatePlan:
    docs: list[DocFile]
    plan: MigrationPlan
    rendered: str  # human-readable markdown plan


def consolidate_plan(root: str | Path) -> ConsolidatePlan:
    from .consolidate.audit import audit_docs
    from .consolidate.plan import build_plan, render_plan

    root = Path(root).resolve()
    docs = audit_docs(root)
    plan = build_plan(root, docs)
    return ConsolidatePlan(docs, plan, render_plan(root, docs, plan))


def consolidate_apply(root: str | Path, plan: MigrationPlan | None = None) -> dict[Path, Path]:
    from .consolidate.apply import apply_plan

    root = Path(root).resolve()
    if plan is None:
        plan = consolidate_plan(root).plan
    return apply_plan(root, plan)


@dataclass
class BootstrapResult:
    created: list[Path]
    stack: object  # generate.stack.Stack
    diagrams_done: bool
    manifest: str


def bootstrap(root: str | Path) -> BootstrapResult:
    from .generate.architecture import run_codeboarding
    from .generate.manifest import build_manifest
    from .generate.scaffold import ensure_structure
    from .generate.stack import detect_stack

    root = Path(root).resolve()
    created = ensure_structure(root)
    stack = detect_stack(root)
    diagrams = run_codeboarding(root)
    manifest = build_manifest(root, stack, diagrams_done=bool(diagrams))
    return BootstrapResult(created, stack, bool(diagrams), manifest)


def distribute(root: str | Path) -> list[Path]:
    from .distribute.fanout import distribute as _distribute

    return _distribute(Path(root).resolve())


def check_freshness(root: str | Path, *, staged: bool = False) -> list[tuple[Path, Anchor, list[str]]]:
    from .freshness.detect import changed_files, find_stale

    root = Path(root).resolve()
    return find_stale(root, changed_files(root, staged=staged))

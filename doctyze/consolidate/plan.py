"""Plan: turn an audit into a non-destructive MigrationPlan (no files touched)."""
from __future__ import annotations

import re
from pathlib import Path

from ..config import CANONICAL_LAYOUT, KIND_TO_DIR
from ..model import ArtifactKind, DocFile, MigrationOp, MigrationPlan

# Kinds we never move (managed elsewhere or intentionally local).
LEAVE_ALONE = {ArtifactKind.KEEP_IN_PLACE, ArtifactKind.AGENT_CONTEXT, ArtifactKind.UNKNOWN}

_ADR_NUM = re.compile(r"^(\d{3,4})[-_]")


def _adr_number(name: str) -> int | None:
    m = _ADR_NUM.match(name)
    return int(m.group(1)) if m else None


def build_plan(root: str | Path, docs: list[DocFile]) -> MigrationPlan:
    root = Path(root).resolve()
    ops: list[MigrationOp] = []
    decisions_dir = root / CANONICAL_LAYOUT["decisions"]
    archive_dir = root / CANONICAL_LAYOUT["archive"]

    # --- ADR pass: resolve numbering collisions (including dups already in place) ---
    adrs = sorted((d for d in docs if d.kind is ArtifactKind.ADR), key=lambda d: d.path)
    # Reserve every number that already appears, so a renumber never steals a real one.
    used: set[int] = {n for d in adrs if (n := _adr_number(Path(d.path).name)) is not None}
    seen: set[int] = set()
    for d in adrs:
        src = Path(d.path)
        n = _adr_number(src.name)
        if n is None:
            target = decisions_dir / src.name
            if target != src:
                ops.append(MigrationOp("move", str(src), str(target), reason="ADR → decisions"))
            continue
        if n in seen:  # a duplicate of an already-claimed number → renumber
            new_n = 1
            while new_n in used:
                new_n += 1
            used.add(new_n)
            name = _ADR_NUM.sub(f"{new_n:04d}-", src.name, count=1)
            ops.append(MigrationOp("renumber", str(src), str(decisions_dir / name),
                                   reason=f"ADR {n:04d} already used → {new_n:04d}"))
            continue
        seen.add(n)
        target = decisions_dir / src.name
        if target != src:
            ops.append(MigrationOp("move", str(src), str(target), reason="ADR → decisions"))

    # --- everything else ---
    for d in docs:
        if d.kind is ArtifactKind.ADR or d.kind in LEAVE_ALONE:
            continue
        src = Path(d.path)
        if d.kind is ArtifactKind.STALE:
            if src.parent != archive_dir:
                ops.append(MigrationOp("archive", str(src), str(archive_dir / src.name),
                                       reason="looks stale/outdated"))
            continue
        target = root / KIND_TO_DIR[d.kind] / src.name
        if target != src:
            ops.append(MigrationOp("move", str(src), str(target),
                                   reason=f"{d.kind.value} → {KIND_TO_DIR[d.kind]}"))

    return MigrationPlan(ops)


def render_plan(root: str | Path, docs: list[DocFile], plan: MigrationPlan) -> str:
    root = Path(root).resolve()
    kept = sum(1 for d in docs if d.kind in LEAVE_ALONE)
    lines = [
        "# Doctyze consolidation plan",
        "",
        f"Scanned **{len(docs)}** doc files. Proposed **{len(plan.ops)}** changes "
        f"(non-destructive: moves preserve git history; nothing is deleted). "
        f"{kept} files left in place.",
        "",
        "Review, then run `doctyze consolidate --apply` to execute.",
        "",
        "| Action | From | To | Why |",
        "|---|---|---|---|",
    ]
    for op in plan.ops:
        frm = str(Path(op.src).relative_to(root))
        to = str(Path(op.dst).relative_to(root)) if op.dst else ""
        lines.append(f"| {op.action} | `{frm}` | `{to}` | {op.reason} |")
    if not plan.ops:
        lines.append("| — | — | — | already canonical |")
    lines.append("")
    return "\n".join(lines)

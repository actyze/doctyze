"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest


SKILL_FIXTURE = """\
---
name: write-adr
description: Use when adding a new external dependency or making a non-obvious design choice.
---

# How to write an ADR

## When to apply
When you're making an architectural decision that future engineers
will need to understand the rationale for.

## Required artifact
A new MADR file at `docs/architecture/decisions/NNNN-<slug>.md`.
"""

RUNBOOK_FIXTURE = """\
---
runbook_id: high-error-rate
alert_names:
  - OrdersApiHighErrorRate
severity: high
service: orders-api
confidence: confirmed
---

# Runbook — high error rate

## Symptom
5xx rate > 1% over 5 minutes.

## Diagnostic steps
1. Check recent deploys.
2. Pull error logs.
"""


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    """A throwaway repo with one canonical skill and one canonical runbook."""
    (tmp_path / "docs" / "skills").mkdir(parents=True)
    (tmp_path / "docs" / "runbooks").mkdir(parents=True)
    (tmp_path / "docs" / "skills" / "write-adr.md").write_text(SKILL_FIXTURE)
    (tmp_path / "docs" / "runbooks" / "high-error-rate.md").write_text(RUNBOOK_FIXTURE)
    return tmp_path

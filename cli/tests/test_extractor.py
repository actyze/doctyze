"""Tests for the LLM extractor + placeholder substitution."""
from __future__ import annotations

from pathlib import Path

import pytest

from doctyze.extractor import (
    PLACEHOLDER_RE,
    _find_placeholders,
    _substitute,
    extract_and_fill,
)
from doctyze.llm import LLM, ExtractionRequest, ExtractionResult
from doctyze.llm.noop import NoopLLM


def test_placeholder_regex_matches_uppercase_with_underscores() -> None:
    text = "Service: {{SERVICE_NAME}} runs on {{LANGUAGE}}. Description: {{ONE_PARAGRAPH_PURPOSE}}."
    found = {m.group(1) for m in PLACEHOLDER_RE.finditer(text)}
    assert found == {"SERVICE_NAME", "LANGUAGE", "ONE_PARAGRAPH_PURPOSE"}


def test_placeholder_regex_does_not_match_lowercase_or_mixed() -> None:
    text = "{{lowercase}} and {{MixedCase}} should not match."
    found = list(PLACEHOLDER_RE.finditer(text))
    assert found == []


def test_substitute_replaces_known_keys_and_leaves_unknown() -> None:
    text = "Hello {{NAME}}, your job is {{ROLE}}."
    results = {
        "NAME": ExtractionResult(value="Ada", confidence="confirmed"),
        # ROLE intentionally absent → should be left as-is.
    }
    out = _substitute(text, results)
    assert "Hello Ada" in out
    assert "{{ROLE}}" in out


def test_find_placeholders_walks_multiple_files(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("Has {{ONE}} and {{TWO}}.")
    (tmp_path / "b.md").write_text("Has {{TWO}} and {{THREE}}.")
    (tmp_path / "c.txt").write_text("No placeholders.")
    found = _find_placeholders([tmp_path / "a.md", tmp_path / "b.md", tmp_path / "c.txt"])
    assert found == {"ONE", "TWO", "THREE"}


def test_extract_and_fill_with_noop_returns_zero_filled(tmp_path: Path) -> None:
    """Noop backend marks every placeholder as 🔴 GAP."""
    (tmp_path / "AGENTS.md").write_text("# {{SERVICE_NAME}}\n\nPurpose: {{ONE_PARAGRAPH_PURPOSE}}")
    backend = NoopLLM()
    summary = extract_and_fill(tmp_path, stack="python", llm=backend)
    assert summary.placeholders_filled == 0
    assert summary.placeholders_gap == 2
    assert summary.files_touched == 1
    # Both placeholders were replaced with TODO: stubs
    content = (tmp_path / "AGENTS.md").read_text()
    assert "TODO:" in content
    assert "{{SERVICE_NAME}}" not in content
    assert "{{ONE_PARAGRAPH_PURPOSE}}" not in content


def test_extract_and_fill_returns_empty_summary_when_no_placeholders(tmp_path: Path) -> None:
    """If a scaffolded repo has no placeholders, extractor is a no-op."""
    (tmp_path / "AGENTS.md").write_text("# orders-api\n\nNo placeholders here.")
    summary = extract_and_fill(tmp_path, stack="python", llm=NoopLLM())
    assert summary.placeholders_filled == 0
    assert summary.placeholders_gap == 0
    assert summary.files_touched == 0


class _StubLLM(LLM):
    """Test backend that returns predictable results from a fixture map."""

    name = "stub"

    def __init__(self, results: dict[str, ExtractionResult]) -> None:
        self._results = results

    def extract(self, request: ExtractionRequest) -> dict[str, ExtractionResult]:
        return {
            key: self._results.get(
                key,
                ExtractionResult(value="UNSET", confidence="gap"),
            )
            for key in request.placeholders
        }


def test_extract_and_fill_with_stub_backend_replaces_placeholders(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(
        "# {{SERVICE_NAME}}\n\nLanguage: {{LANGUAGE}}\n"
    )
    backend = _StubLLM({
        "SERVICE_NAME": ExtractionResult(value="orders-api", confidence="confirmed"),
        "LANGUAGE": ExtractionResult(value="Python 3.11", confidence="confirmed"),
    })
    summary = extract_and_fill(tmp_path, stack="python", llm=backend)
    assert summary.placeholders_filled == 2
    assert summary.placeholders_gap == 0
    assert summary.files_touched == 1
    content = (tmp_path / "AGENTS.md").read_text()
    assert "# orders-api" in content
    assert "Language: Python 3.11" in content

"""Anthropic Claude backend.

Uses the official `anthropic` SDK (installed via the `[llm]` extra).
Reads `ANTHROPIC_API_KEY` from the environment.
"""
from __future__ import annotations

import json
import os
from typing import Any

from doctyze.llm.base import LLM, ExtractionRequest, ExtractionResult

DEFAULT_MODEL = "claude-opus-4-7"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.0


class ClaudeLLM(LLM):
    name = "claude"
    description = "Anthropic Claude (ANTHROPIC_API_KEY)"

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("DOCTYZE_CLAUDE_MODEL", DEFAULT_MODEL)

    def extract(self, request: ExtractionRequest) -> dict[str, ExtractionResult]:
        try:
            import anthropic  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "Claude backend requires the `anthropic` package. "
                "Install with: pip install actyze-doctyze[llm]"
            ) from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. "
                "Export it, or pick a different backend with `--llm=...`."
            )

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            system=self._system_prompt(),
            messages=[{"role": "user", "content": self._build_user_message(request)}],
        )

        # The model is asked to return JSON; parse it tolerantly.
        text = "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        )
        return _parse_response(text, request.placeholders)


def _parse_response(text: str, placeholders: dict[str, str]) -> dict[str, ExtractionResult]:
    """Parse the model's JSON response into ExtractionResult per placeholder.

    Tolerates the common case where the model wraps JSON in a markdown code
    fence. Falls back to a 'gap' result for any key it failed to provide.
    """
    cleaned = _strip_markdown_fence(text)
    try:
        data: dict[str, Any] = json.loads(cleaned)
    except json.JSONDecodeError:
        data = {}

    results: dict[str, ExtractionResult] = {}
    for key, desc in placeholders.items():
        raw = data.get(key)
        if isinstance(raw, dict) and "value" in raw:
            results[key] = ExtractionResult(
                value=str(raw.get("value", "")),
                confidence=_normalize_confidence(raw.get("confidence", "inferred")),
                rationale=str(raw.get("rationale", "")),
            )
        else:
            results[key] = ExtractionResult(
                value=f"TODO: {desc}",
                confidence="gap",
                rationale="model did not provide a value for this placeholder",
            )
    return results


def _strip_markdown_fence(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        # ```json ... ``` or ``` ... ```
        first_newline = s.find("\n")
        if first_newline >= 0:
            s = s[first_newline + 1 :]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()


def _normalize_confidence(raw: Any) -> str:
    value = str(raw).strip().lower()
    if value in {"confirmed", "inferred", "gap"}:
        return value
    return "inferred"

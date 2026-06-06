"""OpenAI backend.

Uses the official `openai` SDK (installed via the `[llm]` extra).
Reads `OPENAI_API_KEY` from the environment.
"""
from __future__ import annotations

import os

from doctyze.llm.base import LLM, ExtractionRequest, ExtractionResult
from doctyze.llm.claude import _parse_response  # re-use the JSON parser

DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.0


class OpenAILLM(LLM):
    name = "openai"
    description = "OpenAI (OPENAI_API_KEY)"

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("DOCTYZE_OPENAI_MODEL", DEFAULT_MODEL)

    def extract(self, request: ExtractionRequest) -> dict[str, ExtractionResult]:
        try:
            from openai import OpenAI  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI backend requires the `openai` package. "
                "Install with: pip install actyze-doctyze[llm]"
            ) from exc

        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY not set. "
                "Export it, or pick a different backend with `--llm=...`."
            )

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": self._build_user_message(request)},
            ],
        )
        text = response.choices[0].message.content or "{}"
        return _parse_response(text, request.placeholders)

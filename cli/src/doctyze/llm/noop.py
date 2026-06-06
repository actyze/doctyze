"""No-op LLM backend.

Used when no LLM credentials are configured. Leaves placeholders as 🔴 GAP
markers so the human knows to fill them in. Lets `doctyze init` produce a
clean structural scaffold without requiring API access.
"""
from __future__ import annotations

from doctyze.llm.base import LLM, ExtractionRequest, ExtractionResult


class NoopLLM(LLM):
    name = "none"
    description = "No LLM — leaves all placeholders as 🔴 GAP for human filling"

    def extract(self, request: ExtractionRequest) -> dict[str, ExtractionResult]:
        return {
            key: ExtractionResult(
                value=f"TODO: {desc}",
                confidence="gap",
                rationale="no-op backend; human fill required",
            )
            for key, desc in request.placeholders.items()
        }

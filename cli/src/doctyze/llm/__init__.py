"""LLM extraction backends.

Doctyze uses an LLM to fill template placeholders ({{SERVICE_NAME}},
{{ONE_PARAGRAPH_PURPOSE}}, etc.) with content extracted from the actual
repository (README, source files, build configuration, alert rules, ADRs).

Backends:
    - claude:   Anthropic Claude (ANTHROPIC_API_KEY)
    - openai:   OpenAI (OPENAI_API_KEY)
    - bedrock:  AWS Bedrock (AWS credentials chain)
    - azure:    Azure OpenAI (AZURE_OPENAI_*)
    - ollama:   Local Ollama (air-gapped / on-prem)
    - none:     No LLM. Leaves placeholders for human filling. Useful when
                you want the structure but plan to author content yourself.

Add a new backend by subclassing :class:`LLM` and registering it in REGISTRY.
"""
from __future__ import annotations

import os

from doctyze.llm.base import LLM, ExtractionRequest, ExtractionResult


def get(name: str | None = None) -> LLM:
    """Get an LLM backend by name. Falls back to env-detected default."""
    if name is None:
        name = _detect_default()
    key = name.lower()

    if key == "none":
        from doctyze.llm.noop import NoopLLM
        return NoopLLM()
    if key == "claude":
        from doctyze.llm.claude import ClaudeLLM
        return ClaudeLLM()
    if key == "openai":
        from doctyze.llm.openai import OpenAILLM
        return OpenAILLM()
    if key == "ollama":
        from doctyze.llm.ollama import OllamaLLM
        return OllamaLLM()

    raise KeyError(
        f"unknown LLM backend: {name!r}. "
        "Known: claude | openai | bedrock | azure | ollama | none"
    )


def _detect_default() -> str:
    """Pick a sensible default backend based on environment."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("OLLAMA_HOST") or os.environ.get("MANIFEST_LLM_ENDPOINT"):
        return "ollama"
    # No credentials anywhere — fall back to noop so `doctyze init` doesn't
    # explode in a fresh sandbox.
    return "none"


__all__ = ["LLM", "ExtractionRequest", "ExtractionResult", "get"]

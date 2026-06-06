"""Ollama / local-LLM backend.

For air-gapped / on-prem deployments where source code can't leave the
boundary. Talks to an Ollama server (or any HTTP endpoint that mimics the
Ollama /api/chat shape).

Reads:
    OLLAMA_HOST              — base URL, e.g. http://localhost:11434
    DOCTYZE_OLLAMA_MODEL     — model name, e.g. llama-3.3-70b

Only requires the standard library + httpx (already a Doctyze dependency).
"""
from __future__ import annotations

import json
import os

import httpx

from doctyze.llm.base import LLM, ExtractionRequest, ExtractionResult
from doctyze.llm.claude import _parse_response  # re-use the JSON parser

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama-3.3-70b"


class OllamaLLM(LLM):
    name = "ollama"
    description = "Ollama / local LLM (OLLAMA_HOST, DOCTYZE_OLLAMA_MODEL)"

    def __init__(self, host: str | None = None, model: str | None = None) -> None:
        self.host = host or os.environ.get("OLLAMA_HOST") or DEFAULT_HOST
        self.model = model or os.environ.get("DOCTYZE_OLLAMA_MODEL", DEFAULT_MODEL)

    def extract(self, request: ExtractionRequest) -> dict[str, ExtractionResult]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": self._build_user_message(request)},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.0},
        }
        try:
            resp = httpx.post(
                f"{self.host.rstrip('/')}/api/chat",
                json=payload,
                timeout=120.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Ollama call failed against {self.host}: {exc}. "
                "Check OLLAMA_HOST or pick a different backend."
            ) from exc

        body = resp.json()
        text = body.get("message", {}).get("content", "{}")
        return _parse_response(text, request.placeholders)

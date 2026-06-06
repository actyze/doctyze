"""LLM backend base class + the extraction-request shape every backend handles."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass
class ExtractionRequest:
    """The structured ask Doctyze sends to an LLM backend.

    The placeholders the scaffolder writes (e.g., {{SERVICE_NAME}},
    {{ONE_PARAGRAPH_PURPOSE}}) become keys in `placeholders`. Each carries
    a description so the backend knows what kind of content is expected.

    The `context` field contains files from the user's repo the backend can
    read for evidence — README excerpts, package.json, the first N lines of
    the entry-point file, alert rules, etc. The scaffolder builds this; the
    backend just consumes it.
    """

    placeholders: dict[str, str]
    """Map of placeholder key → one-line description of what should go there."""

    context: dict[str, str] = field(default_factory=dict)
    """Map of file-label → file-contents that the backend can use as evidence."""

    repo_path: Path | None = None
    """Repo root, in case the backend wants to read additional files itself."""

    stack: str = ""
    """Detected stack identifier (e.g., 'python', 'java-spring')."""


@dataclass
class ExtractionResult:
    """What the LLM returns for one placeholder."""

    value: str
    """The filled-in content. May contain newlines."""

    confidence: Literal["confirmed", "inferred", "gap"]
    """Confidence marker. The scaffolder stamps the artifact accordingly."""

    rationale: str = ""
    """Optional: brief reason the LLM gave for this value. Useful for review."""


class LLM(ABC):
    """Base class for LLM backends."""

    name: str = ""
    """Identifier — lowercase, no spaces."""

    description: str = ""
    """Human-readable description for `doctyze init --llm=...` help text."""

    @abstractmethod
    def extract(self, request: ExtractionRequest) -> dict[str, ExtractionResult]:
        """Fill the placeholders in `request`. Return one result per key.

        Implementations should:
        - Be deterministic-ish (temperature low) so re-runs converge
        - Mark anything genuinely uncertain as 'gap' rather than fabricate
        - Never expose secrets from context to other API calls
        """

    # ── shared utilities ──

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You extract structured documentation context from a software repository. "
            "You receive a list of placeholders the user wants filled and a set of "
            "evidence files from the repo. For each placeholder, return: \n"
            "  - value: the content to insert (concise, factual, repo-specific)\n"
            "  - confidence: 'confirmed' (directly extracted from evidence), "
            "    'inferred' (inferred from patterns; needs human verification), "
            "    or 'gap' (cannot determine from evidence)\n"
            "  - rationale: one-line reason\n"
            "Prefer 'gap' over fabrication. Never invent service names, owners, "
            "or technologies that aren't in the evidence."
        )

    @staticmethod
    def _build_user_message(request: ExtractionRequest) -> str:
        """Standard prompt structure shared by Claude/OpenAI/Ollama backends."""
        lines: list[str] = []
        lines.append(f"Stack: {request.stack or 'unknown'}")
        lines.append("")
        lines.append("Placeholders to fill (placeholder_key → expected content):")
        for key, desc in request.placeholders.items():
            lines.append(f"  - {key}: {desc}")
        lines.append("")
        lines.append("Evidence files from the repository:")
        for label, contents in request.context.items():
            snippet = contents.strip()
            if len(snippet) > 4000:
                snippet = snippet[:4000] + "\n...[truncated]"
            lines.append(f"\n--- {label} ---\n{snippet}")
        lines.append("")
        lines.append(
            "Respond as JSON: a single object mapping placeholder_key to an "
            'object with keys "value", "confidence", "rationale".'
        )
        return "\n".join(lines)

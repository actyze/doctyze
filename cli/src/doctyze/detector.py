"""Stack detection from file signatures.

Detects whether a repo is modern or legacy and which sub-stack it is.
Conservative: when signals conflict, reports low confidence and lets the
user pick via ``--stack=<name>``.

Confidence is a float in [0, 1]. Below 0.7, the CLI prompts for override.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Supported stacks. Used by the scaffolder to pick the template directory.
MODERN_STACKS = {
    "java-spring",
    "python",
    "node-react",
    "go",
}
LEGACY_STACKS = {
    "cobol",
    "abap",
    "ibm-i-rpg",
    "vb6",
    "dotnet-framework",
    "powerbuilder",
    "delphi",
}
ALL_STACKS = MODERN_STACKS | LEGACY_STACKS


@dataclass(frozen=True)
class Detection:
    stack: str
    confidence: float
    signals: list[str]

    @property
    def family(self) -> str:
        return "modern" if self.stack in MODERN_STACKS else "legacy"


# ── Signal patterns ────────────────────────────────────────────────────
#
# Each detector returns the count of matching files for a given stack.
# The stack with the highest count wins; ties report low confidence.

_SIGNATURES: dict[str, dict[str, list[str]]] = {
    # Modern
    "java-spring": {
        "files": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
        "globs": ["src/main/java/**/*.java", "src/main/resources/application.yml"],
    },
    "python": {
        "files": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
        "globs": ["**/*.py"],
    },
    "node-react": {
        "files": ["package.json", "tsconfig.json", "next.config.js", "vite.config.ts", "yarn.lock", "pnpm-lock.yaml"],
        "globs": ["src/**/*.tsx", "src/**/*.jsx", "src/**/*.ts", "src/**/*.js"],
    },
    "go": {
        "files": ["go.mod", "go.sum"],
        "globs": ["**/*.go"],
    },
    # Legacy
    "cobol": {
        "files": [],
        "globs": ["**/*.cbl", "**/*.cob", "**/*.cpy", "**/*.jcl", "**/*.JCL"],
    },
    "abap": {
        "files": [".abapgit.xml"],
        "globs": ["**/*.abap", "**/*.clas.abap", "**/*.prog.abap"],
    },
    "ibm-i-rpg": {
        "files": [],
        "globs": ["**/*.rpgle", "**/*.sqlrpgle", "**/*.dds", "**/*.clp", "**/*.clle"],
    },
    "vb6": {
        "files": [],
        "globs": ["**/*.vbp", "**/*.frm", "**/*.cls", "**/*.bas"],
    },
    "dotnet-framework": {
        # .NET Framework — distinct from modern .NET (net8.0+).
        # Detected by checking csproj for <TargetFrameworkVersion>v4.x</...>.
        "files": [],
        "globs": ["**/*.csproj", "**/packages.config"],
    },
    "powerbuilder": {
        "files": [],
        "globs": ["**/*.pbl", "**/*.pbt", "**/*.pbw"],
    },
    "delphi": {
        "files": [],
        "globs": ["**/*.dpr", "**/*.dproj", "**/*.pas"],
    },
}


def _count_signature(repo: Path, signature: dict[str, list[str]], cap: int = 50) -> int:
    """Count matching files for a signature, capped to avoid scanning huge repos."""
    hits = 0
    for f in signature.get("files", []):
        if (repo / f).exists():
            hits += 5  # explicit build/manifest files weigh more
    for pattern in signature.get("globs", []):
        # rglob via pathlib for `**` semantics
        n = 0
        for _ in repo.rglob(pattern.replace("**/", "")):
            n += 1
            if n >= cap:
                break
        hits += n
    return hits


def _is_dotnet_framework(repo: Path) -> bool:
    """Distinguish legacy .NET Framework from modern .NET (net8.0+)."""
    for csproj in repo.rglob("*.csproj"):
        try:
            text = csproj.read_text(errors="ignore")
        except OSError:
            continue
        if "<TargetFrameworkVersion>v4." in text or "<TargetFrameworkVersion>v3." in text:
            return True
        if "<TargetFramework>net8" in text or "<TargetFramework>net9" in text:
            return False
    return False


def detect_stack(repo: Path, override: str | None = None) -> Detection:
    """Detect the dominant stack in *repo*.

    If *override* is supplied, validate it and return Detection with
    confidence 1.0.
    """
    if override:
        if override not in ALL_STACKS:
            raise ValueError(f"unknown stack: {override}. Allowed: {sorted(ALL_STACKS)}")
        return Detection(stack=override, confidence=1.0, signals=["--stack override"])

    scores: dict[str, int] = {}
    for stack, sig in _SIGNATURES.items():
        scores[stack] = _count_signature(repo, sig)

    # Special-case .NET Framework: only count if we confirmed v4.x or earlier.
    if scores.get("dotnet-framework", 0) > 0 and not _is_dotnet_framework(repo):
        scores["dotnet-framework"] = 0

    if not any(scores.values()):
        # Nothing matched — fall back to "python" with low confidence
        # rather than failing outright.
        return Detection(
            stack="python",
            confidence=0.1,
            signals=["no recognizable signature; default fallback"],
        )

    top_stack, top_score = max(scores.items(), key=lambda kv: kv[1])
    total = sum(scores.values())
    confidence = top_score / total if total else 0.0
    signals = [f"{s}: {n}" for s, n in sorted(scores.items(), key=lambda kv: -kv[1]) if n > 0]
    return Detection(stack=top_stack, confidence=confidence, signals=signals)

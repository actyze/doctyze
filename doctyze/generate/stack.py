"""Detect a repo's tech stack from file signatures (deterministic, no LLM).

Used to tailor the bootstrap manifest (which artifacts to generate, what the
agent should look at). Best-effort and language-agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# signature filename -> (language, framework_hint)
_SIGNATURES: dict[str, tuple[str, str | None]] = {
    "pom.xml": ("java", "maven"),
    "build.gradle": ("java", "gradle"),
    "build.gradle.kts": ("kotlin", "gradle"),
    "package.json": ("javascript", "node"),
    "tsconfig.json": ("typescript", "node"),
    "go.mod": ("go", None),
    "Cargo.toml": ("rust", "cargo"),
    "pyproject.toml": ("python", None),
    "requirements.txt": ("python", "pip"),
    "Gemfile": ("ruby", None),
    "composer.json": ("php", "composer"),
    "pubspec.yaml": ("dart", "flutter"),
}

_CI_SIGNATURES = {
    ".github/workflows": "github-actions",
    "azure-pipelines.yml": "azure-devops",
    "azure-pipelines.yaml": "azure-devops",
    ".gitlab-ci.yml": "gitlab-ci",
    "Jenkinsfile": "jenkins",
}

_DEPLOY_SIGNATURES = {
    "Dockerfile": "docker",
    "docker-compose.yml": "docker-compose",
    "docker-compose.yaml": "docker-compose",
    "Chart.yaml": "helm",
    "*.tf": "terraform",
}


@dataclass
class Stack:
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    ci: list[str] = field(default_factory=list)
    deploy: list[str] = field(default_factory=list)


def detect_stack(root: str | Path) -> Stack:
    root = Path(root)
    s = Stack()
    for sig, (lang, fw) in _SIGNATURES.items():
        if (root / sig).exists() or any(root.glob(f"**/{sig}")):
            if lang not in s.languages:
                s.languages.append(lang)
            if fw and fw not in s.frameworks:
                s.frameworks.append(fw)
    for sig, name in _CI_SIGNATURES.items():
        if (root / sig).exists():
            if name not in s.ci:
                s.ci.append(name)
    for sig, name in _DEPLOY_SIGNATURES.items():
        hit = any(root.glob(f"**/{sig}")) if "*" in sig else (root / sig).exists()
        if hit and name not in s.deploy:
            s.deploy.append(name)
    return s

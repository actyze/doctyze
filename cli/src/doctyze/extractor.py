"""LLM-driven placeholder extractor.

Bridges the scaffolder and the LLM backend. Given a freshly-scaffolded
repo (with {{PLACEHOLDER}} tokens in the canonical files), this module:

1. Walks every file under docs/ + AGENTS.md and finds {{PLACEHOLDER}} tokens
2. Collects high-signal evidence from the repo (README, build configs,
   entry-point source, alert rules, CODEOWNERS, etc.)
3. Sends one extraction request to the configured LLM backend
4. Replaces every placeholder in every file with the extracted value
5. Stamps confidence markers on each file based on the lowest-confidence
   placeholder that file contained

The "all in one call" design keeps token usage bounded and ensures the
LLM sees the full set of placeholders together (which gives better
consistency than one-call-per-placeholder).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from doctyze.llm import LLM, ExtractionRequest, ExtractionResult

PLACEHOLDER_RE = re.compile(r"{{([A-Z][A-Z0-9_]*)}}")

# Map placeholder key → one-line description sent to the LLM.
KNOWN_PLACEHOLDERS: dict[str, str] = {
    "SERVICE_NAME": "The short kebab-case name of this service. Lifted from package.json, pyproject.toml, Chart.yaml, or the repo directory name.",
    "SERVICE_DESCRIPTION": "One-paragraph description of what the service does. From README first paragraph or similar.",
    "ONE_LINE_DESCRIPTION": "Single sentence describing the service.",
    "ONE_PARAGRAPH_PURPOSE": "One paragraph describing the service's purpose.",
    "LANGUAGE": "Primary programming language (e.g., Python, Java, TypeScript).",
    "LANGUAGE_VERSION": "Language version (e.g., 3.11, 21, ES2022).",
    "BUILD_TOOL": "Build tool (e.g., pip/setuptools, Maven, Gradle, npm).",
    "TEST_FRAMEWORK": "Test framework in use (e.g., pytest, JUnit, Vitest).",
    "LICENSE": "License identifier (e.g., Apache-2.0, MIT).",
    "BUILD_COMMANDS": "Multi-line shell snippet showing how to build/test/run the service.",
    "CONVENTIONS_INFERRED_FROM_CODE": "Bullet list of code conventions evident in the repo.",
    "SKILLS_LIST": "Bullet list of canonical skill names found in docs/skills/.",
    "GENERATION_DATE": "Today's date in YYYY-MM-DD format.",
    "SYSTEM_CONTEXT_MERMAID": "Mermaid LR graph showing User → this service → external dependencies.",
    "CONTAINER_VIEW_MERMAID": "Mermaid LR graph showing internal containers (web/api/db/queue).",
    "CRITICAL_FLOW_1": "Short kebab-case name of the most important user-facing flow.",
    "DEPLOYMENT_DESCRIPTION": "How the service is deployed (Kubernetes, ECS, Lambda, etc.).",
    "LOCAL_PORT": "Default local development port (e.g., 8000).",
    "ALERT_RULES_FILE": "Path to the alert-rules file if one exists, else the string 'TODO'.",
    "ALERT_RULES_LINK": "Same as ALERT_RULES_FILE but as a relative link.",
    "DASHBOARD_URL": "URL to the primary monitoring dashboard, or 'TODO' if unknown.",
}


@dataclass
class ExtractionSummary:
    placeholders_filled: int
    placeholders_gap: int
    files_touched: int


def extract_and_fill(repo: Path, stack: str, llm: LLM) -> ExtractionSummary:
    """Walk the freshly-scaffolded repo, fill placeholders, stamp confidence markers."""
    candidate_files = _candidate_files(repo)
    placeholders_found = _find_placeholders(candidate_files)
    if not placeholders_found:
        return ExtractionSummary(0, 0, 0)

    request = ExtractionRequest(
        placeholders={
            key: KNOWN_PLACEHOLDERS.get(key, f"Fill in {key} based on evidence.")
            for key in placeholders_found
        },
        context=_collect_evidence(repo),
        repo_path=repo,
        stack=stack,
    )

    results = llm.extract(request)
    return _apply_results(candidate_files, results)


def _candidate_files(repo: Path) -> list[Path]:
    """Files that may contain placeholders."""
    candidates: list[Path] = []
    targets = [
        repo / "AGENTS.md",
        repo / "README.md",
        repo / ".doctyze.yaml",
    ]
    for t in targets:
        if t.is_file():
            candidates.append(t)
    docs = repo / "docs"
    if docs.is_dir():
        for p in docs.rglob("*"):
            if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".mmd", ".dsl"}:
                candidates.append(p)
    return candidates


def _find_placeholders(files: list[Path]) -> set[str]:
    found: set[str] = set()
    for f in files:
        try:
            text = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for m in PLACEHOLDER_RE.finditer(text):
            found.add(m.group(1))
    return found


def _collect_evidence(repo: Path) -> dict[str, str]:
    """Pull high-signal files for the LLM to read."""
    evidence: dict[str, str] = {}
    for path in [
        repo / "README.md",
        repo / "pyproject.toml",
        repo / "package.json",
        repo / "pom.xml",
        repo / "go.mod",
        repo / "Cargo.toml",
        repo / "Dockerfile",
        repo / "CODEOWNERS",
        repo / ".github" / "CODEOWNERS",
        repo / "AGENTS.md",
    ]:
        if path.is_file():
            try:
                evidence[str(path.relative_to(repo))] = path.read_text()
            except (UnicodeDecodeError, OSError):
                continue
    # First source file for tone + framework hints.
    for src_dir in [repo / "src", repo / "lib", repo / "app"]:
        if src_dir.is_dir():
            for p in src_dir.rglob("*.py"):
                evidence[str(p.relative_to(repo))] = p.read_text()
                break
            break
    return evidence


def _apply_results(
    files: list[Path],
    results: dict[str, ExtractionResult],
) -> ExtractionSummary:
    files_touched = 0
    filled = sum(1 for r in results.values() if r.confidence != "gap")
    gaps = sum(1 for r in results.values() if r.confidence == "gap")

    for path in files:
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        new_text = _substitute(text, results)
        if new_text != text:
            path.write_text(new_text)
            files_touched += 1

    return ExtractionSummary(
        placeholders_filled=filled,
        placeholders_gap=gaps,
        files_touched=files_touched,
    )


def _substitute(text: str, results: dict[str, ExtractionResult]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        result = results.get(key)
        if result is None:
            return match.group(0)   # leave it alone
        return result.value
    return PLACEHOLDER_RE.sub(repl, text)

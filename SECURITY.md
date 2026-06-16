# Security Policy

We take Doctyze's security seriously. If you discover a security issue,
please report it privately so we can fix it before it becomes public.

## Supported versions

Doctyze is pre-alpha. Security fixes apply to the current `main` branch.
Once we cut tagged releases, this section will list which versions
receive security updates.

| Version | Supported |
|---|---|
| `main` (HEAD) | ✅ |
| (no tagged releases yet) | — |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

Instead, report security issues privately by one of these channels:

### 1. GitHub Private Vulnerability Reporting (preferred)

Go to
**[github.com/actyze/doctyze/security/advisories/new](https://github.com/actyze/doctyze/security/advisories/new)**
and submit a draft advisory. This is the recommended path — it gives us
a private space to coordinate the fix and assign a CVE if appropriate.

### 2. Email

Send a description to **security@actyze.com** with:

- A summary of the issue
- Steps to reproduce
- The affected version / commit
- Your assessment of impact
- (Optional) Suggested mitigation

## What to expect

| Step | Timeline |
|---|---|
| Acknowledgment of report | within 3 business days |
| Initial assessment | within 7 business days |
| Fix or mitigation in `main` | as fast as severity warrants — critical within days, high within weeks |
| Public disclosure | coordinated with the reporter, typically after a fix is available |

We'll credit you in the security advisory unless you ask to remain
anonymous.

## Scope

In scope:

- The `doctyze` Python package on PyPI
- The published Doctyze GitHub Actions
  (`action.yml`, the reusable freshness Action)
- Code in this repository
- The Doctyze MCP server (when published)

Out of scope:

- Third-party dependencies (please report those upstream to the
  respective project)
- Issues in the user's own LLM provider account (Anthropic, OpenAI, etc.)
- Repos that *use* Doctyze — those are the user's responsibility

## What counts as a security issue

Examples of issues we want to know about:

- A way for a malicious canonical source (e.g., a crafted
  `docs/skills/*.md`) to make Doctyze write files outside the intended
  agent target directories (.claude/skills, .cursor/rules, AGENTS.md)
- A path traversal that lets a malicious template escape the repo root
- Any code execution path triggered by reading user-supplied content
- LLM prompt injection that causes Doctyze to leak
  secrets, write files, or run arbitrary commands
- A way for a malicious PR to manipulate the freshness Action into
  granting privileges it shouldn't have
- Credential leakage (API keys appearing in logs, in generated files,
  or in the audit trail)
- Supply-chain risks in our published packages

Examples of things that are not security issues but still worth a
regular GitHub issue:

- A documentation typo
- Doctyze producing the wrong content for a non-malicious input
- Your IDE/CI agent giving a low-quality answer

If you're not sure whether something qualifies, err on the side of
reporting privately.

## Hall of fame

When we receive valid reports, we acknowledge reporters in the
corresponding security advisory and in `SECURITY_THANKS.md` (created
on first acknowledgment).

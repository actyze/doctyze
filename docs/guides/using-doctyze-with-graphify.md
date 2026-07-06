# Using Doctyze with Graphify

Doctyze and Graphify are adjacent halves of the same workflow. Doctyze authors the prose artifacts in your repo — specs, ADRs, architecture docs with Mermaid, `AGENTS.md` — each generated file carrying a frontmatter `affects:` anchor that ties it to the code it describes. Graphify reads code *and* those artifacts and indexes them into one queryable NetworkX graph (`graph.json`, plus an MCP server). Neither tool calls the other: the seam between them is a directory of files on disk. Doctyze writes Markdown into `docs/`; Graphify later reads that same `docs/` tree alongside your source. You run each tool's own commands; the handoff is the filesystem.

## Worked example

Start in the root of a repo that has source code but thin or no docs.

### Step 1 — Author the docs with Doctyze

```bash
uvx doctyze init
```

Then open your IDE assistant and invoke the `/doctyze` prompt. Doctyze is BYO-agent — it never calls an LLM itself and needs no API key; it drives the agent already in your editor. The run produces the `docs/` tree: specs under `docs/specs/`, ADRs under `docs/architecture/decisions/`, architecture docs with Mermaid under `docs/architecture/`, and an `AGENTS.md`. Every generated doc gets a frontmatter `affects:` anchor scoped to the code it documents.

Keep those docs honest over time with the built-in freshness check:

```bash
doctyze watch --base "origin/main"
```

This matches changed files against each doc's `affects:` anchor using `git diff` — deterministic, no model involved.

### Step 2 — Index code and docs with Graphify

Now that `docs/` exists, point Graphify at the repo so it graphs code *and* the prose Doctyze just wrote:

```bash
uv tool install graphifyy        # PyPI package name has a double-y
graphify install
```

Then invoke `/graphify .` in your assistant. Graphify walks the repository, parses the source into an AST-level graph (structural edges such as `imports`, `calls`, `inherits`), adds document and concept nodes for the Markdown under `docs/`, and writes `graphify-out/graph.json`. Because Doctyze already populated `docs/`, those doc nodes land in the same graph as the code — one corpus, one file.

### Step 3 — Query the merged graph

Query it directly from the CLI:

```bash
graphify query "where is refund logic implemented"
graphify path payments.refund billing.Invoice
graphify explain payments/refund.py
graphify affected core/money.py     # reverse-reachability: what depends on this node
```

Or serve the same graph over MCP so an assistant can query it in-session:

```bash
python -m graphify.serve graphify-out/graph.json
```

## Who owns what

| | Doctyze | Graphify |
|---|---|---|
| Role | Generates the in-repo `docs/` tree and keeps it fresh | Indexes code + docs into one graph and answers queries |
| Writes | Specs, ADRs, architecture + Mermaid, `AGENTS.md` | `graphify-out/graph.json`, an MCP server |
| Commands | `doctyze init`, `/doctyze`, `doctyze watch` | `graphify install`, `/graphify .`, `graphify query/path/explain/affected`, `python -m graphify.serve` |
| Freshness signal | Deterministic: `affects:` anchor + `git diff` | Query-time graph lookup |

## Caveats — read before you rely on this

The two freshness signals are not the same kind of thing:

- **Doctyze's `affects:` freshness is deterministic.** It is a literal `git diff` against each doc's anchor globs. Same inputs, same output, no LLM, reproducible in CI.
- **Graphify's doc↔code links are model-inferred, so treat them as advisory.** The edges that connect a doc node to the code it describes are inferred by a model; they are useful for discovery and navigation, not a gate you can trust to never miss.

**The "affected docs, powered by the graph" idea is proposed, not shipped.** Wiring Doctyze's affected-docs check to consume Graphify's `graph.json` — so a change to an imported module can flag docs on the importing module via transitive reachability — is evaluated in [ADR-0007](../architecture/decisions/0007-graphify-graph-for-affected-docs.md). It is a design decision under review, **not** a wired-up feature you can run today. Nothing in the two tools calls the other.

**So, today:** use each tool through its own commands. Author and keep docs fresh with `doctyze` (`/doctyze` to write, `doctyze watch` to check). Index and query with `graphify` (`/graphify .` to build, `graphify query`/`affected`/`explain` or the MCP server to ask). The integration in ADR-0007 may change that later; until it ships, run them side by side.

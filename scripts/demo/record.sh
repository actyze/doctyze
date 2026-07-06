#!/usr/bin/env bash
# Render the Doctyze freshness-loop demo GIF.
#
#   ./scripts/demo/record.sh          → writes scripts/demo/freshness-loop.gif
#
# Requires: vhs (brew install vhs) and uvx (uv). The GIF is intentionally NOT
# committed — regenerate it from the tape when the demo changes.
#
# We do the git setup HERE (not in the tape) and invoke vhs from inside the
# prepared repo, so the tape's commands run against real files — no dependence
# on vhs inheriting env vars or a particular working directory.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v vhs >/dev/null || { echo "vhs not found — install: brew install vhs  (https://github.com/charmbracelet/vhs)"; exit 1; }
command -v uvx >/dev/null || { echo "uvx not found — install uv: https://docs.astral.sh/uv/"; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cp -R "$here/sample/." "$work/"
git -C "$work" init -q
git -C "$work" add -A
git -C "$work" -c user.email=demo@doctyze -c user.name=demo commit -qm initial >/dev/null

# Invoke vhs from inside the prepared repo so the tape runs against real files.
( cd "$work" && vhs "$here/freshness-loop.tape" )

mv "$work/freshness-loop.gif" "$here/freshness-loop.gif"
echo "✔ wrote $here/freshness-loop.gif"
echo "  Reference it in the README hero:  ![Doctyze freshness loop](scripts/demo/freshness-loop.gif)"

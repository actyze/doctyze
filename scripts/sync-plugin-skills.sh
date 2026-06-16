#!/bin/sh
# Sync canonical skills (doctyze/skills) into the Claude Code plugin.
# doctyze/skills/ is the single source of truth; plugins/doctyze/skills/ is generated.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/doctyze/skills"
DST="$ROOT/plugins/doctyze/skills"
rm -rf "$DST"
mkdir -p "$DST"
cp -R "$SRC"/. "$DST"/
echo "Synced $(find "$DST" -name SKILL.md | wc -l | tr -d ' ') skills to the plugin."

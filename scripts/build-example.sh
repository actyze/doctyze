#!/usr/bin/env bash
#
# build-example.sh — produce an entry for the Doctyze examples gallery.
#
# Doctyze is BYO-agent: this script does only the DETERMINISTIC halves (clone +
# `doctyze init`, then collect the generated docs/). The prose generation in
# between is an agent step you run in your IDE (`/doctyze`) — the script cannot
# and does not fake it.
#
# Usage:
#   scripts/build-example.sh prep    <name> <git-url> [ref]
#   scripts/build-example.sh collect <name>
#
# Then edit examples/README.md to add the row (SHA is in PROVENANCE.md).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
examples="$here/examples"
work="$examples/.work"

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

cmd="${1:-}"; shift || true

case "$cmd" in
  prep)
    name="${1:-}"; url="${2:-}"; ref="${3:-}"
    [ -n "$name" ] && [ -n "$url" ] || die "usage: build-example.sh prep <name> <git-url> [ref]"
    command -v git >/dev/null   || die "git not found"
    command -v uvx >/dev/null   || die "uvx not found (install uv: https://docs.astral.sh/uv/)"

    clone="$work/$name"
    mkdir -p "$work"
    if [ -d "$clone/.git" ]; then
      echo "• reusing existing clone at examples/.work/$name"
    else
      echo "• cloning $url → examples/.work/$name"
      git clone --depth 1 ${ref:+--branch "$ref"} "$url" "$clone"
    fi

    sha="$(git -C "$clone" rev-parse HEAD)"
    dver="$(uvx doctyze --version 2>/dev/null || echo 'unknown')"

    echo "• running deterministic setup: uvx doctyze init"
    ( cd "$clone" && uvx doctyze init )

    dest="$examples/$name"
    mkdir -p "$dest"
    cat > "$dest/PROVENANCE.md" <<EOF
# Provenance — $name

- **Source:** $url
- **Commit:** \`$sha\`${ref:+ (ref: $ref)}
- **Generated with:** $dver
- **Generated on:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

Reproduce:
\`\`\`bash
scripts/build-example.sh prep $name $url ${ref:-}
# then run /doctyze in your IDE on examples/.work/$name
scripts/build-example.sh collect $name
\`\`\`
EOF
    echo
    echo "✔ prep done. Provenance → examples/$name/PROVENANCE.md"
    echo
    echo "NEXT (agent step — not scriptable):"
    echo "  1. Open  examples/.work/$name  in your IDE."
    echo "  2. Run  /doctyze  to generate the docs (reads the code, writes docs/)."
    echo "  3. Run  scripts/build-example.sh collect $name  to copy docs/ into the gallery."
    ;;

  collect)
    name="${1:-}"
    [ -n "$name" ] || die "usage: build-example.sh collect <name>"
    clone="$work/$name"
    src="$clone/docs"
    [ -d "$src" ] || die "no docs/ in examples/.work/$name — run the /doctyze agent step first"

    dest="$examples/$name/docs"
    rm -rf "$dest"
    mkdir -p "$dest"
    # copy the generated tree only (no source code)
    cp -R "$src/." "$dest/"
    count="$(find "$dest" -type f | wc -l | tr -d ' ')"
    echo "✔ collected $count doc file(s) → examples/$name/docs/"
    echo "  Now add a row to examples/README.md (SHA in examples/$name/PROVENANCE.md)."
    ;;

  *)
    die "usage: build-example.sh {prep|collect} ... (see examples/README.md)"
    ;;
esac

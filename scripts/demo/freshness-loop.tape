# Doctyze — the affected-docs loop, as a GIF.
# Do NOT run this tape directly: it expects to run inside an already-prepared git
# repo (a copy of ./sample). Use ./record.sh, which sets that up and invokes vhs
# from the prepared dir. Requires: vhs (https://github.com/charmbracelet/vhs) + uvx.

Output freshness-loop.gif
Require uvx

Set Shell "bash"
Set FontSize 20
Set Width 1200
Set Height 720
Set Theme "Dracula"
Set TypingSpeed 55ms
Set Padding 24

Hide
Type "clear"
Enter
Sleep 300ms
Show

# --- the story (runs in the prepared repo record.sh cd'd into) ---
Type "# Each doc declares the code it describes, in an 'affects:' anchor:"
Enter
Sleep 1s
Type "grep -A1 'affects' docs/specs/refunds.md docs/specs/money.md"
Enter
Sleep 2500ms

Type "# Change the refund limit in the code..."
Enter
Sleep 800ms
Type "sed -i '' 's/100.00/500.00/' src/payments/refund.py"
Enter
Sleep 900ms

Type "# ...which docs did that make stale?"
Enter
Sleep 700ms
Type "uvx doctyze watch"
Enter
Sleep 4500ms

Type "# Exactly refunds.md — money.md is untouched. Regenerate only what changed."
Enter
Sleep 3500ms

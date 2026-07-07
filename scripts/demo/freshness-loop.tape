# Doctyze — generate the docs from code, then catch exactly which ones a change breaks.
# Do NOT run this tape directly: it expects to run inside an already-prepared git repo
# (a copy of ./sample). Use ./record.sh, which sets that up and invokes vhs from the
# prepared dir. Requires: vhs (https://github.com/charmbracelet/vhs) + uvx.

Output freshness-loop.gif
Require uvx

Set Shell "bash"
Set FontSize 20
Set Width 1220
Set Height 760
Set Theme "Dracula"
Set TypingSpeed 50ms
Set Padding 26

Hide
Type "clear"
Enter
Sleep 300ms
Show

# --- 1. GENERATE: your IDE agent wrote a docs layer from the code ---
Type "# 1. Doctyze + your IDE agent wrote these docs from the code:"
Enter
Sleep 1s
Type "find docs -name '*.md' | sort"
Enter
Sleep 2600ms
Type "# the refund spec it wrote — note the limit it documents:"
Enter
Sleep 800ms
Type "sed -n '8,12p' docs/specs/refunds.md"
Enter
Sleep 2800ms

# --- 2. CHANGE: edit the code (edit hidden; shown as a real diff) ---
Hide
Type "perl -i -pe 's/100\.00/500.00/' src/payments/refund.py"
Enter
Sleep 200ms
Show
Type "# 2. Now you change the refund limit in the code:"
Enter
Sleep 800ms
Type "git diff src/payments/refund.py"
Enter
Sleep 3000ms

# --- 3. CATCH: exactly which docs did that make stale? ---
Type "# 3. Which docs did that just make stale?"
Enter
Sleep 800ms
Type "uvx doctyze watch"
Enter
Sleep 4500ms

# --- 4. FIX: regenerate only that doc, in your IDE (the agent step) ---
Type "# 4. Exactly refunds.md — money.md and the ADR are untouched."
Enter
Sleep 1600ms
Type "#    Regenerate just it in your IDE: /doctyze  (your model, no API key)"
Enter
Sleep 3800ms

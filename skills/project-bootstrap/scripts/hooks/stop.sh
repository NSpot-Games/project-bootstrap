#!/bin/sh
input=$(cat)
[ -f tools/check_docs.py ] || exit 0
py=python3
"$py" -c "pass" >/dev/null 2>&1 || py=python
"$py" -c "pass" >/dev/null 2>&1 || { echo 'check_docs: no python interpreter found; skipping'; exit 0; }
if printf '%s' "$input" | "$py" -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("stop_hook_active") else 1)' 2>/dev/null; then exit 0; fi
current="$PWD/docs/CURRENT.md"
if [ ! -f "$current" ]; then
  # No current-focus file yet: the bootstrap is still running and a red linter is its normal state.
  "$py" tools/check_docs.py --root . || echo "check_docs found errors; not blocking because $current does not exist yet (bootstrap in progress)"
  exit 0
fi
"$py" tools/check_docs.py --root . || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }

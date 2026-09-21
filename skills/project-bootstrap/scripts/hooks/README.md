# Running check_docs automatically

The linter is meant to run without anyone remembering to run it. The project keeps its own
copy at `<project>/tools/check_docs.py` (the bootstrap skill copies `scripts/check_docs.py`
there in its generation step), and the snippets below run that copy.

The Stop hook below picks `python3` or `python` itself, whichever works. The pre-commit and CI
snippets call `python3`, the name on macOS and Debian-family Linux; Windows users substitute
`python`.

## Claude Code Stop hook (per project)

Copy `scripts/hooks/stop.sh` to `<project>/tools/hooks/stop.sh`. It receives Claude Code's
JSON on stdin and exits 0 when `stop_hook_active` is true, so a session that cannot fix the
errors is not blocked forever:

```sh
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
```

Add to `<project>/.claude/settings.json` (or `settings.local.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "sh tools/hooks/stop.sh"
          }
        ]
      }
    ]
  }
}
```

Exit code 2 from a Stop hook blocks the stop and shows the message to the agent. Warnings do
not block. Until `<project>/docs/CURRENT.md` exists the hook prints the findings and exits 0
instead of blocking: a bootstrap runs across several sessions, and a red linter is its normal
state until generation has run.

## Claude Code Stop hook (from the plugin)

If the kit was installed as a Claude Code plugin, the plugin already registers a Stop hook. It
runs the project's `tools/check_docs.py` when that file exists and does nothing otherwise, so
no per-project setting is needed. Installing both is harmless; the linter runs twice.

## Pre-commit hook

`<project>/.git/hooks/pre-commit` (make it executable), or the equivalent entry in your
pre-commit framework:

```sh
#!/bin/sh
python3 tools/check_docs.py --root . || exit 1
```

## CI

Run `python3 tools/check_docs.py --root .` as a step. It exits 1 on any E-code.

## Regenerating indexes

`python3 tools/check_docs.py --root . --fix` rewrites `<project>/docs/milestones/README.md`,
`<project>/docs/plans/README.md`, `<project>/docs/decisions/README.md`, and
`<project>/docs/CURRENT.md`. Run it at the end of every session and commit the result. Never
edit those four files by hand.

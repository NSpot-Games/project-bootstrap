# M1-01 — Add and reverse entries
**Status:** done
**Milestone:** M1
**Branch:** feat/M1-01-add-and-reverse
**Design docs:** `docs/design/product-design.md §4.2`
**ADRs:** `docs/decisions/0001-entries-are-append-only.md`
**Depends on:** M0-02

## Sessions
- 2026-09-14T09:00Z — claude-code — feat/M1-01-add-and-reverse

## Objective
CLI commands to add and reverse an entry.

## Tasks
- [x] T1 — add. **Verify:** `pytest tests/test_cli.py`
- [x] T2 — reverse. **Verify:** `pytest tests/test_cli.py`

## Progress notes
- 2026-09-14 — done.

## Verification log
- T1, T2: `pytest tests/test_cli.py` → `6 passed`

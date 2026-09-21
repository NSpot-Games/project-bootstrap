# M2-01 — Push endpoint
**Status:** in progress
**Milestone:** M2
**Branch:** feat/M2-01-push-endpoint
**Design docs:** `docs/design/sync/sync-design.md §1`
**ADRs:**
**Depends on:** M1-01

## Sessions
- 2026-09-16T09:00Z — claude-code — feat/M2-01-push-endpoint

## Objective
A device can push new entries to the service.

## Current state
- Service skeleton exists; no endpoint yet.

## Approach
POST a batch of entries; the service appends and acks.

## Tasks
- [x] T1 — Endpoint. **Verify:** `pytest tests/test_push.py`
- [ ] T2 — Client call. **Verify:** `pytest tests/test_client.py`

## Progress notes
- 2026-09-16 — endpoint done; client next.

## Verification log
- T1: `pytest tests/test_push.py` → `3 passed`

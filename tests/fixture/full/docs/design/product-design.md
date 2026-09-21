# Ledgerlite product design
**Project:** Ledgerlite  **Status:** stable  **Audience:** anyone testing the linter at the full tier
Related: `docs/roadmap.md`, `docs/design/sync/sync-design.md`

---

## 1. One-liner
A personal ledger file that syncs between a person's own devices.

## 2. Pillars
### 2.1 The file is the product
Everything lives in one JSON ledger the user can read.

## 3. Success criteria
- P1: one ledger opens, edits and saves round-trip.
- P2: two devices converge within a minute.

## 4. Constraints
4.1 The ledger file is plain JSON, one entry per line.
4.2 No entry is ever deleted; a reversal entry is appended instead.
4.3 The sync service never sees plaintext amounts.

## Changelog
- 2026-09-15 — created.

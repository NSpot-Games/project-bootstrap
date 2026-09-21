# Roadmap
**No checkboxes here.** Scope and progress live in `docs/milestones/`.

## Principles
- Every milestone ends in something runnable or measurable.

## P1 — Local core
**Status:** done
**Exit:** one ledger opens, edits and saves round-trip; see `docs/design/product-design.md §3`.

### M0 — Schema
Goal: the ledger file format and one example ledger.

### M1 — Editing
Goal: entries can be added and edited locally.

## P2 — Sync
**Status:** active
**Exit:** two devices converge on the same ledger within a minute; see `docs/design/sync/sync-design.md §2`.

### M2 — Sync protocol
Goal: a device pushes and pulls changes.

### M3 — Conflict handling
Goal: concurrent edits merge without loss.

### M4 — Multi-device UX
**Status:** sketch
Goal: TBD.

## P3 — Sharing
**Status:** sketch
**Exit:** TBD

### M5 — Shared ledgers
Goal: TBD.

## Explicitly deferred
- Bank imports.

# Sync design
**Project:** Ledgerlite
**Status:** draft
**Audience:** whoever builds M2 and M3
Related: `docs/design/product-design.md §4`

---

## 1. Protocol
A device pushes its new entries and pulls entries it has not seen; entries are append-only (`docs/design/product-design.md §4.2`).

## 2. Convergence
Two devices converge once each has pulled the other's push. Conflicts are handled in M3.

## Changelog
- 2026-09-16 — created.

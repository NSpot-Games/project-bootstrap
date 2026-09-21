# 0001. Entries are append-only
**Status:** accepted
**Date:** 2026-09-12
**Deciders:** the team
**Related:** `docs/design/product-design.md §4.2`

## Context
Sync is far simpler when nothing is ever deleted.

## Decision
Entries are never deleted; a reversal entry is appended.

## Alternatives considered
Tombstones.

## Consequences
The ledger only grows; compaction is deferred.

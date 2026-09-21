# 0001. YAML frontmatter is optional; a missing date falls back to the filename
**Status:** proposed
**Date:** 2026-09-19
**Deciders:** the team
**Related:** `docs/design/architecture.md §6`
**Blocking:** no

## Context
Notes are written in a hurry; requiring frontmatter rejects real notes.

## Decision
Frontmatter is optional. A missing date comes from the `YYYY-MM-DD-` filename prefix; a missing title from the first heading.

## Alternatives considered
Requiring frontmatter and rejecting notes without it.

## Consequences
The loader needs fallbacks and a diagnostic for notes with no date anywhere.

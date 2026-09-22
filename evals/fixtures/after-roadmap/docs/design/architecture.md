# Architecture
**Project:** Fieldnote  **Status:** draft  **Audience:** whoever changes the internals
Related: `docs/design/api-surface.md`, `docs/design/fieldnote-design.md §5`

---

## 1. Repo layout
`src/fieldnote/` (the package), `src/fieldnote/cli.py`, `tests/`, `fixtures/golden/<id>/`
(golden examples, each a folder of notes plus `expected-index.json`).

## 2. Key internal interfaces
`parse_note(text, path) -> Note`; `Indexer.add(note)`; `Renderer.page(kind, key, notes)`.

## 3. Data flow and performance budget
load → parse → index → render. Budget: 500 notes in under five seconds end to end; parsing
is the only stage allowed to touch the file system.

## 4. Dependency policy
`markdown-it-py` and `pyyaml` are the only runtime dependencies; nothing vendored.

## 5. Testing strategy
Unit tests per stage; the golden examples are integration tests; one benchmark against the
500-note synthetic folder with the budget as its baseline.

## 6. Decisions
1. Notes are plain files; the index is derived and never hand-edited — *owner*.
2. YAML frontmatter is optional; a missing date falls back to the filename — *owner*.
3. `markdown-it-py` and `pyyaml` are the only runtime dependencies — *recommended, not confirmed*.
4. Tags are case-insensitive and stored lowercase — *owner*.

Questions live in `docs/OPEN-QUESTIONS.md`, never in this document.

## Changelog
- 2026-09-19 — created.

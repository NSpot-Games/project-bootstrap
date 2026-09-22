# API surface
**Project:** Fieldnote  **Status:** draft  **Audience:** anyone calling the library or the CLI
Related: `docs/design/fieldnote-design.md §2`, `docs/design/architecture.md §2`

---

## 1. Principles
Public: `fieldnote.load_notes`, `fieldnote.build_index`, `fieldnote.render_site`, the `Note`
and `Index` types, and the CLI. Internal: everything under `fieldnote._internal`. One
stability tier before 1.0: none.

## 2. The surface
### 2.1 `load_notes(folder: Path) -> list[Note]`
Reads every `*.md` under `folder`. Frontmatter is optional; a missing date falls back to the
filename prefix; a missing title falls back to the first heading.
### 2.2 `build_index(notes: list[Note]) -> Index`
Groups by place, date and tag. Tags are lowercased.
### 2.3 `render_site(index: Index, out_dir: Path) -> None`
Writes one page per place and per tag, an index page and `index.json`.
### 2.4 CLI
`fieldnote index <folder>` prints the index as JSON; `fieldnote build <folder> --out <dir>`
renders the site.

## 3. Error model
`NoteError(path, line, message)` for malformed frontmatter. A note with no date anywhere is a
warning and is indexed as undated.

## 4. Golden usage examples
`fixtures/golden/basic/`: two notes and `expected-index.json`; the test suite builds the index
and compares.

## 5. Deprecation and removal
None before 1.0; after 1.0, one minor release of warning before removal.

## 6. Decisions
1. Frontmatter is optional; a missing date falls back to the filename prefix — *owner*.
2. A note with no date anywhere is a warning and is indexed as undated — *recommended, not confirmed*.

Questions live in `docs/OPEN-QUESTIONS.md`, never in this document.

## Changelog
- 2026-09-19 — created.

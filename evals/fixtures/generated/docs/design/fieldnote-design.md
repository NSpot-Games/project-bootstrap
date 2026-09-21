# Fieldnote design
**Project:** Fieldnote  **Status:** draft  **Audience:** whoever builds the first release
Related: `docs/design/api-surface.md`, `docs/design/architecture.md`, `docs/roadmap.md`

---

## 1. Who this is for and what it replaces
Fieldnote is a command-line tool and Python library that turns a folder of dated markdown field
notes into a searchable static site. It is for people who write one note per visit to a place
and want an index by place, date and tag without running a general static-site generator. It
replaces a hand-kept index page.

## 2. API design principles
### 2.1 Naming
Verbs for functions (`load_notes`, `build_index`, `render_site`), nouns for types (`Note`,
`Index`). No abbreviations in the public surface.
### 2.2 Ergonomics
One call does one stage; the CLI composes them. Every public call works on the golden example.
### 2.3 Stability promise
Nothing is stable before 1.0. The surface doc (`docs/design/api-surface.md`) carries the promise
once it is made.

## 3. Supported platforms and runtimes
Python 3.11 and later on Linux, macOS and Windows. Pure Python; no native extensions.

## 4. Non-goals for v1
- Editing notes in a browser.
- Sync between machines.
- A plugin system before there are two real plugins to generalise from.

## 5. Success criteria for the first prototype
- The golden example at `fixtures/golden/basic/` builds to an index equal to its
  `expected-index.json`, checked by a test.
- `fieldnote build` on 500 notes completes in under five seconds on a laptop.

## Changelog
- 2026-09-18 — created.

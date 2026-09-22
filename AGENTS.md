# AGENTS.md

This repository is the bootstrap kit itself — one Agent Skill at `skills/project-bootstrap/`
holding `references/core/`, `references/profiles/`, `assets/templates/` and
`scripts/check_docs.py` — not a project built on the kit. Read `BOOTSTRAP.md` first: it states
the idea, names the machinery, and points into the skill.

## Rules

- Every path any doc here cites must exist, and every `§N` cited must be a real numbered
  heading. Run `python skills/project-bootstrap/scripts/check_docs.py --root .` before ending
  a session — zero errors, always.
- Paths have three forms. Inside `skills/project-bootstrap/`, kit paths are relative to the
  skill root (`references/core/layers.md §1`) so the skill works when installed alone. At the
  repo root they are full (`skills/project-bootstrap/references/core/layers.md §1`). Paths in
  the project being bootstrapped are written `<project>/...`.
- Templates (`skills/project-bootstrap/assets/templates/*.md`) keep the exact field formats
  `scripts/check_docs.py` parses: status lines, ID forms, checkbox syntax. Changing a
  template's shape without updating the linter breaks every project that copies it.
- A change to what the linter checks adds a test to `tests/test_check_docs.py` and, where the
  change needs one, an edit to a fixture under `tests/fixture/`.
- No double-brace placeholders outside `skills/project-bootstrap/assets/templates/`.
  Elsewhere, a name that isn't fixed yet is written `<angle-bracketed>`.
- Section numbers (`## N. Title`) are contracts once another doc cites them — append a lettered
  section rather than renumbering.
- The version is `2.7.0` in `skills/project-bootstrap/SKILL.md` metadata,
  `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; bump all three together.

## Commands

- `python -m pytest tests -q` — the linter's own test suite and the skill package tests.
- `python skills/project-bootstrap/scripts/check_docs.py --root .` — lint the kit's own docs;
  must report zero errors and zero warnings.

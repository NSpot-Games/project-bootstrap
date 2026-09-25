# AGENTS.md

Instructions for any AI agent in this repository. `CLAUDE.md` imports this file. Keep under 120 lines.

## What this is
**Fieldnote** is a command-line tool and library that turns a folder of dated markdown field notes into a searchable static site. The rule that shapes everything: **the golden example is a test, not a document**.
**Profile:** library-sdk-cli  **Tier:** standard

## Read first
1. `DOCS.md`  2. `docs/CURRENT.md`  3. `docs/design/fieldnote-design.md`  4. `docs/GLOSSARY.md`  5. `docs/WORKFLOW.md`
Then the design doc for the area you're touching.

## Non-negotiable rules
- No public function without a golden example that exercises it.
- ...

## Repository layout
- `src/fieldnote/` — the package (`docs/design/architecture.md §1`)
- `fixtures/golden/<id>/` — golden examples, each a folder of notes plus an expected index
- `docs/` — see `DOCS.md`

## How to work
1. Open `docs/CURRENT.md`. Resume a feature you claimed, or claim the next unclaimed one: set its plan to `in progress` and add a session stamp under `## Sessions`.
2. No plan? Ground → Brainstorm → Plan. No code before the plan.
3. Plan exists? Read it fully; resume at the first unticked task.
4. Work a task, run its verification, paste evidence, tick, commit as `M1-03: what changed`.
5. Before ending: plan matches reality; notes say where you stopped.
6. Before ending: run `python tools/check_docs.py --fix` and commit the generated files with your work.
Small fixes skip the plan (`docs/WORKFLOW.md` §5).

## Stopping rules
- Keep going when a step needs no input; put the status in the same message as the next action.
- Stop and ask before anything destructive (deleting data, force-pushing, rewriting history), anything outside this repository (pushing its own branch is fine), or anything that spends money.
- A question that doesn't block goes to `docs/OPEN-QUESTIONS.md` with the default you chose; continue on it.
- End each session with the report `docs/WORKFLOW.md` §3a orders: Needs from you first.

## Commands
- `python -m pytest -q` — tests, including the golden examples
- `python -m fieldnote build fixtures/golden/basic --out build/site` — render the golden example
Once `check` exists, it runs exactly what CI's fast job runs; run it before pushing, never push to find out.

## Conventions
- Words: `docs/GLOSSARY.md`. Say the precise term, not the loose one.
- Cross-references: `docs/design/<file>.md §N.M`, `ADR <NNNN>`, `M<n>-<nn>`.
- Tests: only tests that pin a contract, reproduce a real bug, or guard an expensive invariant (`docs/WORKFLOW.md` §2). Every golden example is a test; write the expected index before the code that produces it.
- Docs and code agree, in the same commit.
- Hard-to-reverse choices get an ADR; agents propose, humans accept.

## Don't
- Don't build browser editing or sync; both are deferred in `docs/roadmap.md`.
- Don't tick a box without running the verification.
- Don't run the full suite after every change: the task's check while working, the full suite once at Close.
- Don't paste full test output as evidence; paste the summary line.
- Don't renumber sections in design docs.
- Don't edit `docs/CURRENT.md` or any `README.md` index by hand; they are generated.
- Don't start a feature whose plan has a session stamp under 24 hours old from someone else.

## Tool-specific notes
- Claude Code: `CLAUDE.md` is `@AGENTS.md` plus nothing.
- Codex: reads this natively; nested `AGENTS.md` files scope to their subtree.
- Others: point them here first.

# AGENTS.md

Instructions for any AI agent in this repository. `CLAUDE.md` imports this file. Keep under 120 lines.

## What this is
**{{Project}}** is {{one_sentence}}. The rule that shapes everything: **{{one_rule}}**.
**Profile:** {{profile}}  **Tier:** {{tier}}

## Read first
1. `DOCS.md`  2. `docs/CURRENT.md`  3. `docs/design/{{product}}-design.md`  4. `docs/GLOSSARY.md`  5. `docs/WORKFLOW.md`
Then the design doc for the area you're touching.

## Non-negotiable rules
- {{rule}}
- ...

## Repository layout
One line per top-level entry; cite `<file>.md §N`.

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
{{commands}}
Once `check` exists, it runs exactly what CI's fast job runs; run it before pushing, never push to find out.

## Conventions
- Words: `docs/GLOSSARY.md`. Say the precise term, not the loose one.
- Cross-references: `docs/design/<file>.md §N.M`, `ADR <NNNN>`, `M<n>-<nn>`.
- Tests: only tests that pin a contract, reproduce a real bug, or guard an expensive invariant (`docs/WORKFLOW.md` §2). Note what is test-first for this project.
- Docs and code agree, in the same commit.
- Hard-to-reverse choices get an ADR; agents propose, humans accept.

## Don't
- {{deferred}}
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

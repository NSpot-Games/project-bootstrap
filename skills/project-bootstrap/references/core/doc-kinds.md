# Document kinds

Five kinds of document, one job each, and the rules that keep a design doc trustworthy.

## 1. Why docs are the contract

An agent's session carries no memory into the next one. Everything it knows about the project when it starts is whatever it can read. If the docs are complete, current, and consistent, every session starts grounded in the real state of the work. If they are not, every session starts by guessing, and each guess drifts a little further from what is actually true. The docs are not a record kept alongside the project; they are the contract the project and its agents run on.

## 2. The five kinds

| Kind | Lives in | Answers | Changes |
|---|---|---|---|
| Design | `<project>/docs/design/` | What is this and why is it shaped this way | Rarely, deliberately, with a changelog entry |
| Decision | `<project>/docs/decisions/` | Why this over that | Never edited; superseded |
| Direction | `<project>/docs/roadmap.md` | In what order, and what each phase must prove | At phase boundaries and milestone reviews |
| Progress | `<project>/docs/milestones/`, `<project>/docs/plans/`, `<project>/docs/CURRENT.md` | What are we building now, what is done | Every session |
| Reference | `<project>/DOCS.md`, `<project>/docs/WORKFLOW.md`, `<project>/docs/GLOSSARY.md`, `<project>/AGENTS.md`, `<project>/docs/OPEN-QUESTIONS.md` | How we work, what words mean, what is unresolved | When the process changes |

**Design** states what a part of the system is and why it is shaped that way: vision, data model, architecture, the reasoning behind a shape. It does not carry checkboxes, session notes, or a log of what happened — that drifts the moment it is written and nobody trusts it after the second drift.

**Decision** records a choice between alternatives at the moment it was made, so later sessions do not relitigate it or silently reverse it. An ADR is never edited to reflect a later change of mind; a later choice supersedes it and says so. It does not hold ongoing rationale for something still open — that belongs in the design doc once decided, or in `<project>/docs/OPEN-QUESTIONS.md` until then.

**Direction** is the roadmap: the order of phases and milestones and what each phase must prove before the next starts. It carries no checkboxes — progress is not tracked here, only sequence and intent. It changes at phase boundaries and milestone reviews, not every session.

**Progress** is what is being built right now and what has shipped: milestone files with feature checkboxes, one plan per feature, and the generated `<project>/docs/CURRENT.md`. It changes constantly, by design, and is the only kind of document a routine session is expected to edit by hand (milestone checkboxes and plan files; the indexes and `<project>/docs/CURRENT.md` are generated, never hand-edited).

**Reference** is how the project works and what its words mean: the workflow, the glossary, the agent instructions, and the list of things still unresolved. It changes only when the process itself changes, not when a feature ships.

## 3. Design doc rules

Every design doc opens with the header from `assets/templates/design-header.md`: an H1 title, then one line carrying `**Project:**`, `**Status:**`, and `**Audience:**`, then a `Related:` line naming the other docs it depends on, then a rule before the body starts.

Status is exactly one of `draft`, `stable`, or `living`. `draft` means the doc is ahead of the phase it describes and may still change on first contact with the work; `stable` means the described part is built and the doc is deliberately maintained; `living` means the doc is expected to change often as understanding improves (a glossary-adjacent design area, for example) and a changelog entry is still required per change.

Every design doc ends with a numbered *Decisions* section (the decisions it rests on, each marked *owner*, *recovered* or *recommended, not confirmed*; the source the ADR backfill reads), then the one-line pointer to `<project>/docs/OPEN-QUESTIONS.md`, then a `## Changelog` section. A design change made during a milestone appends a changelog line in the same commit that makes the change — never a separate cleanup commit, and never silence.

The linter checks both rules on every file under `<project>/docs/design/` (an index file named README and generated files excepted): a missing header or a status outside `draft`, `stable`, `living` is `E014`; a missing `## Changelog` is `E015`.

One numbered heading per section, never two numbers in one heading, so every anchor resolves. Section anchors are contracts. Once another doc, a plan, or an ADR cites `§6.1`, that number is fixed forever; renumbering breaks every citation that used it. A section inserted later gets an appended letter — `§6.1a` between `§6.1` and `§6.2` — never a renumbering of what follows.

A citation to a document whose exact name is not fixed yet (a doc that will exist per-project, or a generic pattern this kit describes rather than ships) is written with the variable part in angle brackets: `<file>.md §N.M`, never a literal-looking path that does not exist. A citation to a real file that a later bootstrap step will create is different: write the real path. While the bootstrap is running — before `<project>/docs/CURRENT.md` exists — the linter reports such a citation to any file inside the project as `W007`, a warning; once generation has run, the same missing file is `E001`. A doc the profile schedules for a later phase is created by neither the bootstrap nor generation: name it in prose until it exists, never by path. Likewise a generic reference to a per-instance file ("each case's README") is prose, not a citation. Any backticked filename — a readme, a note's name, a note's name with a section number — is a citation, resolved against the citing file's folder, the project root and `docs/`, and reported when it resolves nowhere; a file named in prose is cited by its full path from the project root or written without backticks.

## 4. Where things go

Restated in every project's own `<project>/DOCS.md` (see `assets/templates/DOCS.md §4`), so it is worth stating once here too:

- A new rule → the design doc. If it contradicts the doc, that is a design change: update it, and add an ADR if the change is hard to reverse.
- A choice between alternatives → an ADR, plus a one-line pointer from the design doc.
- Something to build → a milestone feature line. Never a design doc.
- How it is being built → the plan. Never a design doc or an ADR.
- A new term → the glossary, in the same change that introduces it.
- An open question → `<project>/docs/OPEN-QUESTIONS.md`. Once answered → an ADR, and the entry is removed.
- A measurement → the evidence directory, linked from the milestone it supports.
- A phase or a reordering → the roadmap, with an ADR if the order changed for a stated reason.
- Current focus → nowhere by hand; `<project>/docs/CURRENT.md` is generated (`references/core/long-horizon.md §7`).

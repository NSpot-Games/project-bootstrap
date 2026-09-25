# BOOTSTRAP.md

The entry point to this kit. Read this file first; it states the idea in one page, names the
machinery, and points into the skill at `skills/project-bootstrap/`, where the rules
(`references/core/`), profiles (`references/profiles/`), templates (`assets/templates/`) and
linter (`scripts/check_docs.py`) live. It contains no templates of its own.

## 1. The idea in one page

**Docs are the contract with your agents.** An agent's session carries no memory into the next
one; what it knows about the project is only what it can read. If the docs are complete,
current, and consistent, every session starts grounded in the real state of the work. If they
aren't, every session starts by guessing, and each guess drifts a little further from what's
true.

**Five kinds of document, each with one job:** design (what is this and why is it shaped this
way), decision (why this over that, recorded once and never edited), direction (the roadmap:
what order, and what each phase must prove), progress (what's being built now, what's done),
and reference (how the project works, what its words mean). `skills/project-bootstrap/references/core/doc-kinds.md §2`.

**Four layers of work:** phase (a group of milestones with its own exit) → milestone (features
with checkboxes, the source of truth for progress) → feature (one line in its milestone) → plan
(one per feature: grounding, approach, tasks with checkboxes, progress notes — the handoff
between sessions). `skills/project-bootstrap/references/core/layers.md §1`.

**A five-step feature lifecycle, with two hatches:** Ground → Brainstorm → Plan → Execute →
Close (`skills/project-bootstrap/references/core/lifecycle.md §1`). No code before a plan; no ticked box without verification
evidence. A brainstorm that hits a technical question rather than a matter of direction may
spend a time-boxed spike answering it before planning (`skills/project-bootstrap/references/core/lifecycle.md §2`). Three kinds of
small change skip the plan entirely — a bug fix with a reproducing test, a typo, a dependency
bump with no API change (`skills/project-bootstrap/references/core/lifecycle.md §3`).

**One instruction file for all agents:** `<project>/AGENTS.md` at the project root is canonical;
`<project>/CLAUDE.md` is `@AGENTS.md` and nothing else; nested `<project>/AGENTS.md` files scope
rules to subtrees.

## 2. The machinery

**Document kinds** (`skills/project-bootstrap/references/core/doc-kinds.md`) — the five kinds above, where each lives, and how each
is allowed to change; the rules that keep a design doc trustworthy (a fixed header, a
changelog, section anchors as contracts).

**Layers and identifiers** (`skills/project-bootstrap/references/core/layers.md`) — the four layers above, each with an ID form and
exactly one place its status lives. Its rules say what happens when a milestone is dropped,
split, or a feature moves to another milestone: IDs are never reused or renumbered.

**Lifecycle** (`skills/project-bootstrap/references/core/lifecycle.md`) — the full detail behind Ground, Brainstorm, Plan, Execute,
and Close, including the Close checklist and the two escape hatches named above.

**Long-horizon rules** (`skills/project-bootstrap/references/core/long-horizon.md`) — a rolling wave keeps only the current and next
milestone `planned`; everything further out is a one-sentence `sketch` until a phase review
promotes it. `<project>/docs/CURRENT.md` is generated and held under forty lines so a session's
read cost never grows with the project's history.

**Parallel agents** (`skills/project-bootstrap/references/core/parallel-agents.md`) — a feature is claimed by setting its plan
`in progress` and stamping a session line; four index files are generated, never hand-edited,
so two sessions working at once never collide on the same file.

**Tiers** (`skills/project-bootstrap/references/core/tiers.md`) — lite, standard, or full scale the file set to the project's size,
with rules for promoting from one to the next as a project grows.

**Economy** (`skills/project-bootstrap/references/core/economy.md`) — tests that earn their place,
checks sized to the moment (the full suite once, at Close), one CI workflow with a fast and a slow
job, stopping rules and a session report that opens with what the human must decide.

## 3. Start here

- New project → `skills/project-bootstrap/references/core/adoption.md §1`.
- Existing code → `skills/project-bootstrap/references/core/adoption.md §2`.
- Pick a profile in `skills/project-bootstrap/references/profiles/README.md`.
- Templates in `skills/project-bootstrap/assets/templates/`.
- Linter in `skills/project-bootstrap/scripts/check_docs.py`; hooks in
  `skills/project-bootstrap/scripts/hooks/README.md`.
- Agents with skills: `skills/project-bootstrap/SKILL.md`, or install it — see `README.md`.

## 4. Target structure

A project on the standard tier (`skills/project-bootstrap/references/core/tiers.md §3`, most projects) looks like this. Lite drops
`docs/milestones/` and `docs/plans/` and keeps checkboxes on the roadmap itself
(`skills/project-bootstrap/references/core/tiers.md §2`); full adds phases, per-area design docs, and an evidence trail
(`skills/project-bootstrap/references/core/tiers.md §4`).

```
<project>/AGENTS.md                              canonical agent instructions (< 120 lines), points outward
<project>/CLAUDE.md                              "@AGENTS.md" and nothing else
<project>/DOCS.md                                map of docs/ and the rules for it
<project>/README.md                              one paragraph for humans, pointer to <project>/DOCS.md
<project>/docs/WORKFLOW.md                       the five-step lifecycle in this project's words, session handoff
<project>/docs/GLOSSARY.md                       the project's words, grouped by area, with ID prefixes
<project>/docs/OPEN-QUESTIONS.md                 every open question, one place, with an owner and a deadline
<project>/docs/CURRENT.md                        generated: active phase, in-progress work, claimed features
<project>/docs/roadmap.md                        phases and milestones in order; principles; deferred list
<project>/docs/design/<product>-design.md        design docs the chosen profile calls for (see note below)
<project>/docs/decisions/AGENTS.md               how to write ADRs; backfill list
<project>/docs/decisions/README.md               generated ADR index
<project>/docs/decisions/<NNNN>-<slug>.md        one decision each, never edited once written
<project>/docs/milestones/README.md              generated index with status
<project>/docs/milestones/M<n>.md                goal, exit criteria, evidence, features as checkboxes
<project>/docs/plans/README.md                   generated index
<project>/docs/plans/M<n>/M<n>-<nn>-<slug>.md    one plan per feature, one directory per milestone
<project>/docs/evidence/                         measurements and write-ups, linked from the milestone
```

Not every project writes the same design docs, and not every project calls them the same
things — that list, and its vocabulary, comes from the chosen profile
(`skills/project-bootstrap/references/profiles/README.md §3`).

## 5. Lessons

What the reference project got right and wrong building v1, and what changed building v2 to fix
it, are collected in one place, in the same spirit either way: `skills/project-bootstrap/references/core/lessons.md`.

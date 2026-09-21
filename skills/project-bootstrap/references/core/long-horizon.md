# Long-horizon planning

Rules so a project with twenty milestones is planned as honestly as one with three: bounded detail ahead, bounded read cost at session start, and a fixed point in the process where the plan gets re-examined.

## 1. Rolling wave

At any time, the current milestone and the next one are `planned` or later: a measurable exit, features listed, the milestone file present. Everything beyond that is `sketch`: a goal in one or two sentences in the roadmap, no milestone file, no exit criteria required yet. The linter permits `TBD` inside `sketch` sections of the roadmap and nowhere else outside `<project>/docs/OPEN-QUESTIONS.md`.

## 2. Phase exits

Each phase states what it must prove and how that is measured. The design doc's success-criteria section is organised by phase, not by "first prototype" or similarly vague milestones. Phase 1's criteria are numeric from bootstrap, since it is the phase being built immediately; later phases' criteria are sketched at bootstrap and sharpened when the phase becomes `active`.

## 3. Design docs by phase

Bootstrap writes the vision, the core data model, the architecture skeleton, and one example instance covering phase 1 only. Each later phase, when it becomes `active`, gets the per-area design docs it needs under `<project>/docs/design/<area>/` and a new example instance exercising the systems that phase adds. A design doc written before its phase is active is `draft` and says so in its header (`references/core/doc-kinds.md §3`).

## 4. Re-planning cadence

The Close step of a milestone's last feature includes a roadmap review (`references/core/lifecycle.md §5`, item 7), run in this order:

1. Check the milestone's exit criteria against the evidence collected.
2. Promote the next `sketch` milestone to `planned` with a real, measurable exit.
3. Re-order or split milestones if what was learned during the milestone demands it.
4. Record any reordering, with its reason, as an ADR.
5. Batch-accept any ADRs still `proposed` from the milestone just closed.

## 5. Milestone size

Three to ten features per milestone, exit demonstrable in a single session by someone who did not build it; larger is split, smaller is folded into a neighbour. The full rule and its ID consequences are in `references/core/layers.md §5` and `references/core/layers.md §2`.

## 6. Dependencies

A milestone or feature line may carry `depends on: M3, M4-02`, written on the milestone's header or the feature's line. Dependencies let the roadmap run parallel tracks: the roadmap shows each track as a sub-section under its phase rather than forcing a single sequence.

The linter enforces two things here: it fails (`E008`) if a `planned` or `in progress` item depends on something `sketch` or `dropped`, and it warns (`W002`) if a plan is `in progress` while a dependency's feature is still unticked.

## 7. Bounded read cost

`<project>/docs/CURRENT.md` is generated, not written by hand: the active phase, the in-progress milestone or milestones with their exit criteria on one line each, each claimed feature with its plan path and last progress note, open blockers, the next unclaimed features, any row of `<project>/docs/OPEN-QUESTIONS.md` whose *Blocks* column names one of the listed features or milestones, and the most recent evidence. When no milestone is `in progress` yet — the state right after bootstrap — it lists the first `planned` milestone and its features instead, so the first session always has something to claim. It stays under forty lines by construction — anything longer belongs in the plan it points to, not in `<project>/docs/CURRENT.md` itself.

Session start reads `<project>/AGENTS.md`, then `<project>/docs/CURRENT.md`, then the plan for the feature being resumed or claimed. The milestone file and the roadmap are read only when planning a new feature or reviewing the roadmap, not on every session. Done plans stay where they are but appear only in a collapsed section of the generated index, so the index stays short as the project grows.

## 8. Worked example

A twenty-milestone project, three phases: P1 is `M1`–`M6`, P2 is `M7`–`M13`, P3 is `M14`–`M20`.

**At bootstrap.** P1 is `active`; P2 and P3 are `sketch`. `M1` and `M2` are `planned` (the rolling wave's current and next); `M3` through `M20` are `sketch` — a goal sentence each in the roadmap, no milestone files yet.

**At M2 close.** `M1` and `M2` are `done`. Each milestone close promotes the next `sketch` milestone to `planned`, so by the time `M2` closes, `M3` (promoted when `M1` closed) is the current milestone and `M4` (promoted now) is next, both `planned`. `M5` through `M20` remain `sketch`. P1 is still `active`.

**At P1 close.** `M1` through `M6` are all `done`; the rolling wave has already carried the `planned` pair past the phase boundary, so `M7` and `M8` are `planned` from milestones promoted during `M5`'s and `M6`'s closes. P1's exit criteria are checked against evidence and P1 becomes `done`; P2 becomes `active`, which is the trigger for writing P2's per-area design docs and its new example instance (`§3`). `M9` through `M20` remain `sketch`.

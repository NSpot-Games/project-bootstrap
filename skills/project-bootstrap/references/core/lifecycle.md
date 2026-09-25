# Lifecycle

Ground → Brainstorm → Plan → Execute → Close, as every feature moves through it, and the escape hatches that keep the process from being a straitjacket. Each project copies this cycle into its own `<project>/docs/WORKFLOW.md §2` in the words that fit its profile; this page is where the rules behind those words live.

## 1. The five steps

**Ground.** Before anything else, read `<project>/AGENTS.md` (which imports the rest of the reference set), then `<project>/docs/CURRENT.md` to see the project's actual state, not the state remembered from a previous session. Then, concretely: read the milestone file the feature belongs to, read the design docs the feature line cites, grep `<project>/docs/decisions/` for ADRs that already constrain the area, run the tests for the packages the feature will touch (the full suite ran at the previous Close and runs in CI, `references/core/economy.md §2`), inspect the packages the feature will change, and read the previous feature's plan if one exists. Write three to ten concrete bullets into the plan's Current state section before brainstorming starts. Mark any bullet you could not confirm and say where you looked. "Understand the current state" is not an action a session can perform; reading a specific file and running a specific command are. If Ground turns up that the feature is already done, mis-scoped, or blocked on something else, stop here and say so rather than planning against an imagined codebase.

**Brainstorm.** Propose an approach, list the alternatives considered (one line each, not a full write-up), name the risks and how each will be checked, list the docs that will need updating when the feature lands, and decide whether the change is hard to reverse enough to need an ADR — if so, write it now with status `proposed` so it exists before Close needs it. Do this with the human when the direction is ambiguous; alone when the docs already say what to build clearly enough that a second opinion adds nothing. A brainstorm may end in a spike instead of a plan when the open question is technical rather than a matter of direction (`§2`).

**Plan.** Break the approach into tasks, each sized to one commit and each naming how it will be verified — the cheapest check that still proves the task (`references/core/economy.md §2`): a command, a manual check, a specific assertion, not "test it works." State **Done when** (checkable end states) and **Stop and ask if** (the conditions that bring the human in). List every test the feature adds under **Tests this feature adds**, one line each; a test earns its place only by the rule in `references/core/economy.md §1`. Order tests before the code they check where tests apply to the change. A feature expected to take three commits or fewer may use a lite plan instead (`§3a`). Set the plan's status to `planned` and link it from the milestone's feature line, so the milestone always points at real, current work.

**Execute.** Work task by task: do the work, run the task's check, paste its summary line into the plan as evidence (never the full output), tick the task, commit with the feature ID as the commit message's prefix, and note anything learned along the way, even things that do not change the plan. If execution reveals the plan is wrong — a task does not do what was expected, or a step was missed — fix the plan first and commit that fix, rather than quietly deviating from what the plan says and leaving the next reader confused.

**Close.** A self-review of the diff against `main` for blocking problems only, all tasks ticked with evidence, the full suite run once and green (or the plan says exactly what is red and why that is acceptable), docs updated in the same change that needed them, ADRs written during the feature reviewed: accepted by a human, or left `proposed` (non-blocking unless `**Blocking:** yes`), the feature ticked in its milestone, and the plan set to `done`. See `§5` for the full checklist.

## 2. Spikes

A spike is time-boxed, throwaway code written to answer one question a brainstorm could not resolve by reading and reasoning alone — which of two libraries handles a case correctly, whether an approach is even feasible, what an unfamiliar API actually returns. It is scoped before it starts: the question it answers and the time box are written down, not discovered afterward. The result — what was learned — is recorded in the plan's Current state, or in an ADR if the spike settled a decision that other work depends on. Spike code is either deleted once the question is answered or re-enters the project properly through Plan, with tests and the usual scrutiny; it is never committed to `main` as-is, no matter how tempting it is to keep code that already "works."

## 3. Small changes

Three cases skip the plan entirely: a bug fix accompanied by a reproducing test, a typo or formatting fix, and a dependency bump with no API change. Each is small enough that Ground-Brainstorm-Plan would cost more than the change itself, and without this hatch the process gets skipped outright the first time someone needs to fix a typo — which then makes it easier to skip for the next change too.

The promotion rule: if a small change grows past one commit, it is no longer small. Stop, write a plan, and let it proceed as a feature from there. Growth past one commit is the signal, not a subjective sense that the change "got complicated."

## 3a. Plan-lite

A feature expected to take three commits or fewer may use `<project>/tools/templates/plan-lite.md`
instead of the full plan: the same header plus `**Shape:** lite`, Sessions, Objective, Done when,
Stop and ask if, Current state (one to three bullets, replacing Ground's three to ten — Ground still happens), Tasks with a check
each, Progress notes and a verification log. No Approach, alternatives, risks, docs to update or
separate test list; any test the feature needs is named in its task line. Status, claiming and
Close are unchanged.

The promotion rule mirrors `§3`: a fourth task makes it a full plan. Copy the missing sections
from `<project>/tools/templates/plan.md`, delete the Shape line, and continue; the linter warns
(`W008`) on an open lite plan holding more than three tasks. The plan shape is not the tier:
a lite-tier project keeps its checkboxes on the roadmap and writes no plans at all
(`references/core/tiers.md §2`).

## 4. Experiments

Under the data-ml profile, a feature is often an experiment rather than a build. An experiment that closes with a negative result still closes `done` — a negative result is evidence, not a failed feature, and the milestone that measured it succeeded at measuring, even though the hypothesis did not hold. The evidence file (`assets/templates/evidence.md`) records what was measured, how, and the result, whichever way it came out; the roadmap review (`references/core/long-horizon.md §4`) reads that evidence when deciding what to plan next.

## 5. Close in detail

1. Every task in the plan is ticked, each with verification evidence pasted in.
2. Before asking for review, review the diff against `main` and list only blocking problems — each with the file, the line, why it is wrong, and how to show it failing — and fix each or record it in the plan (`references/core/economy.md §4`). Then run the full suite, once: it is green, or the plan states exactly what is red and why that is acceptable at this point.
3. Every doc whose described behaviour changed is updated in the same commit.
4. ADRs opened during the feature are reviewed; a `proposed` ADR does not block Close unless it is marked `**Blocking:** yes`.
5. The feature's checkbox is ticked in the milestone file, and the plan's status is set to `done`.
6. Run `tools/check_docs.py --fix` and commit the regenerated indexes alongside the rest of the change.
7. If this is the milestone's last feature, run the roadmap review checklist (`references/core/long-horizon.md §4`) before ending the session.

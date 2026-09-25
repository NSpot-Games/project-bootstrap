# Workflow

## 1. Four layers
`roadmap.md` (phase; narrative, no checkboxes) → `docs/milestones/M<n>.md` (milestone; features, checkboxes; source of truth) → feature (one line, checkbox) → `docs/plans/M<n>/M<n>-<nn>-<slug>.md` (plan; grounding, approach, tasks, notes; session handoff).
Feature IDs: `M<n>-<nn>`. Status lives in exactly one place per layer.
IDs are allocated in order and never reused. A moved feature gets a new ID; the old plan stays with status `moved to M<n>-<nn>`.

## 2. Feature lifecycle
**Ground** — read `docs/CURRENT.md`, then AGENTS/CLAUDE, the milestone, the cited design docs; grep `decisions/`; run the tests for the packages the feature will touch (the full suite ran at the last Close and runs in CI); inspect the packages touched; read the previous feature's plan. Write 3–10 concrete bullets into **Current state**, marking anything you could not confirm and where you looked. If the feature is done, mis-scoped, or blocked: stop and say so.
**Brainstorm** — approach, alternatives (one line each), risks and how they'll be checked, docs to update, ADR needed? (write it as `proposed` now). A brainstorm may end in a **spike**: time-boxed, throwaway code to answer one question. The spike's question, box, and result are recorded in the plan's **Current state** (or an ADR if it decided something). Spike code is deleted or re-enters through Plan; spikes are never committed to `main`. With the human if ambiguous; alone if the docs already say what to build.
**Plan** — tasks, each one commit, each naming its verification: the cheapest check that still proves it. Fill **Done when** and **Stop and ask if**. List every new test under **Tests this feature adds**; a test earns its place only if it pins behaviour a user or contract depends on, reproduces a real bug, or guards an invariant that is expensive to debug — not implementation restatements, trivial accessors, mocks of mocks, blanket snapshots, or coverage padding. Tests first where tests apply. Three commits or fewer: a lite plan (§5b). Set plan status `planned`; link it from the milestone.
**Execute** — task by task: do, run the task's check (while editing: typecheck plus the test file you touch), paste its summary line as evidence — never full output — tick, commit `M1-03: ...`, note anything learned. A redundant or brittle test may be deleted with a one-line note. Plan wrong? Fix the plan first.
**Close** — review the diff against `main`: blocking problems only, each with file, line, why, and how to show it failing; fix or record each. Then the full suite, once, green; all tasks ticked; docs updated; ADRs reviewed: accepted by a human, or left `proposed` (non-blocking unless `**Blocking:** yes`); feature ticked in the milestone; plan `done`. Run `python tools/check_docs.py --fix`. If this is the milestone's last feature, run the roadmap review checklist (§10).

## 3. Sessions
Claim before you start: plan status `in progress` plus a stamp line `- <date>T<hh>:<mm>Z — <agent> — <branch>` (UTC; the agent is the tool's name, `claude-code`, `codex`; the branch is the one you are on) under `## Sessions`, and the plan's path appended to the feature line in the milestone. The first claim in a milestone also sets that milestone's `**Status:**` to `in progress`. Never take a feature stamped under 24 hours ago by someone else.
Start: `AGENTS.md` → `docs/CURRENT.md` → your plan → first unticked task. End: plan matches reality; notes say where you stopped; tree green or the plan says what's red. One feature per session by default.

## 3a. Working for a human
A question that doesn't block the next step goes to `docs/OPEN-QUESTIONS.md` with the default you chose; carry on with that default. Only a blocking question stops the session. End every session with a report in this order: **Needs from you** (decisions, approvals, answers) → **Done** (with evidence summary lines) → **Findings** → **Next**.

## 4. Branches and commits
`feat/M1-03-title`. Commit messages start with the feature ID. PRs link the plan; don't duplicate it. `main` is always green.

## 5. Small changes
Skip the plan for: obvious bug fixes with a reproducing test; typos and formatting; no-API-change dependency bumps. If it grows past one commit, it's a feature.

## 5a. Spikes
Time-boxed, throwaway code to answer one question. Never committed to `main`. Record the question, the time box, and the result in the plan's Current state, or in an ADR if it decided something.

## 5b. Plan-lite
A feature you expect to take three commits or fewer may use `tools/templates/plan-lite.md`: header with `**Shape:** lite`, Sessions, Objective, Done when, Stop and ask if, one to three Current state bullets, Tasks, Progress notes, Verification log. Tests go in the task lines. A fourth task makes it a full plan: copy the missing sections from `tools/templates/plan.md` and delete the Shape line. The linter warns (W008) on a lite plan over three tasks.

## 6. When things don't fit
Too big → split. Blocked on a decision → ADR `proposed`, move on. Exit criteria unmeetable → say so with numbers. Doc is wrong → fix it in the same change.

## 7. Plan template
Copy `tools/templates/plan.md` (or `tools/templates/plan-lite.md`, §5b) to `docs/plans/M<n>/M<n>-<nn>-<slug>.md` and fill every double-brace token; none may remain.

## 8. Milestone template
Copy `tools/templates/milestone.md` to `docs/milestones/M<n>.md` and fill every double-brace token. A feature line gains its plan path when the plan is written, not before.

## 9. Every session, in order
1. Read `AGENTS.md`. 2. Open `docs/CURRENT.md`. 3. Claim or resume your feature. 4. Verify before ticking. 5. Run `python tools/check_docs.py --fix`. 6. Leave the plan true.

## 10. Roadmap review checklist
Run this when a milestone's last feature closes:
1. Check the milestone's exit criteria with evidence.
2. Promote the next `sketch` milestone to `planned` with a real exit.
3. Re-order or split milestones if what was learned demands it.
4. Record a reasoned re-order as an ADR.
5. Batch-accept proposed ADRs.

# Workflow

## 1. Four layers
`roadmap.md` (phase; narrative, no checkboxes) → `docs/milestones/M<n>.md` (milestone; features, checkboxes; source of truth) → feature (one line, checkbox) → `docs/plans/M<n>/M<n>-<nn>-<slug>.md` (plan; grounding, approach, tasks, notes; session handoff).
Feature IDs: `M<n>-<nn>`. Status lives in exactly one place per layer.
IDs are allocated in order and never reused. A moved feature gets a new ID; the old plan stays with status `moved to M<n>-<nn>`.

## 2. Feature lifecycle
**Ground** — read `docs/CURRENT.md`, then AGENTS/CLAUDE, the milestone, the cited design docs; grep `decisions/`; run tests; inspect the packages touched; read the previous feature's plan. Write 3–10 concrete bullets into **Current state**. If the feature is done, mis-scoped, or blocked: stop and say so.
**Brainstorm** — approach, alternatives (one line each), risks and how they'll be checked, docs to update, ADR needed? (write it as `proposed` now). A brainstorm may end in a **spike**: time-boxed, throwaway code to answer one question. The spike's question, box, and result are recorded in the plan's **Current state** (or an ADR if it decided something). Spike code is deleted or re-enters through Plan; spikes are never committed to `main`. With the human if ambiguous; alone if the docs already say what to build.
**Plan** — tasks, each one commit, each naming its verification. Tests first where tests apply. Set plan status `planned`; link it from the milestone.
**Execute** — task by task: do, verify, paste evidence, tick, commit `M1-03: ...`, note anything learned. Plan wrong? Fix the plan first.
**Close** — all tasks ticked, suite green, docs updated, ADRs reviewed: accepted by a human, or left `proposed` (non-blocking unless `**Blocking:** yes`), feature ticked in the milestone, plan `done`. Run `python tools/check_docs.py --fix`. If this is the milestone's last feature, run the roadmap review checklist (§10).

## 3. Sessions
Claim before you start: plan status `in progress` plus a stamp line `- {{date}}T{{hh}}:{{mm}}Z — {{agent}} — {{branch}}` under `## Sessions`, and the plan's path appended to the feature line in the milestone. The first claim in a milestone also sets that milestone's `**Status:**` to `in progress`. Never take a feature stamped under 24 hours ago by someone else.
Start: `AGENTS.md` → `docs/CURRENT.md` → your plan → first unticked task. End: plan matches reality; notes say where you stopped; tree green or the plan says what's red. One feature per session by default.

## 4. Branches and commits
`feat/M1-03-title`. Commit messages start with the feature ID. PRs link the plan; don't duplicate it. `main` is always green.

## 5. Small changes
Skip the plan for: obvious bug fixes with a reproducing test; typos and formatting; no-API-change dependency bumps. If it grows past one commit, it's a feature.

## 5a. Spikes
Time-boxed, throwaway code to answer one question. Never committed to `main`. Record the question, the time box, and the result in the plan's Current state, or in an ADR if it decided something.

## 6. When things don't fit
Too big → split. Blocked on a decision → ADR `proposed`, move on. Exit criteria unmeetable → say so with numbers. Doc is wrong → fix it in the same change.

## 7. Plan template
```markdown
# M{{n}}-{{nn}} — {{Title}}
**Status:** grounding
**Milestone:** M{{n}}
**Branch:** feat/M{{n}}-{{nn}}-{{slug}}
**Design docs:**
**ADRs:**
**Depends on:**

## Sessions

## Objective
## Current state
## Approach
### Alternatives considered
### Risks
### Docs to update
## Tasks
- [ ] T1 — ... **Verify:** `command`
## Progress notes
## Verification log
```

## 8. Milestone template
```markdown
# M{{n}} — {{Title}}
**Status:** planned
**Goal:**
**Exit criteria:**
**Evidence of exit:**
**Depends on:**

## Features
- [ ] M{{n}}-01 — {{Title}}

## Notes
```

## 9. Every session, in order
1. Read `AGENTS.md`. 2. Open `docs/CURRENT.md`. 3. Claim or resume your feature. 4. Verify before ticking. 5. Run `python tools/check_docs.py --fix`. 6. Leave the plan true.

## 10. Roadmap review checklist
Run this when a milestone's last feature closes:
1. Check the milestone's exit criteria with evidence.
2. Promote the next `sketch` milestone to `planned` with a real exit.
3. Re-order or split milestones if what was learned demands it.
4. Record a reasoned re-order as an ADR.
5. Batch-accept proposed ADRs.

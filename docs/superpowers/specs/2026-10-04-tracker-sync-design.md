# Tracker sync — design (v2.10.0)

**Date:** 2026-10-04
**Status:** approved in brainstorm, awaiting spec review

## 1. Intent

Several people and agents work one project at once. Today a claim — plan `in progress` plus a
session stamp (`skills/project-bootstrap/references/core/parallel-agents.md §1`) — lives on the
claimer's feature branch, so nobody on another branch sees it until it merges. This release
mirrors every planned milestone and feature onto a GitHub Project and makes the board the lock
checked at claim time, so everyone sees who is working on what within seconds, and a merged PR
moves its card to Done with no manual step.

**Decided in the brainstorm (owner):**

1. The repo stays the single source of status (`references/core/layers.md §4`). The board is a
   generated mirror plus a visible claim lock; nothing on the board ever changes the repo.
2. GitHub Projects only in this release. The config key and the `(tracker: …)` link leave room
   for Linear or Jira later.
3. The claim lock is a hard stop: a feature whose issue is assigned to someone else is not
   claimed without a human's explicit say-so.
4. One board item per feature (`M<n>-<nn>`); plan tasks are not synced.
5. No CI workflow ships: Done comes from `Closes #N` in the PR body plus the project's built-in
   "item closed → Done" rule, so no secret or personal access token is needed
   (`references/core/economy.md §3` keeps saying the kit does not write a project's CI).

**Success criteria**

- `python -m pytest tests -q` passes; `check_docs.py --root .` reports 0 errors, 0 warnings.
- All existing eval assertions still pass; the new `tracker-claim` scenario passes in full.
- One live check on a throwaway GitHub repository: generation creates the project and issues,
  a claim assigns and moves to In Progress, a merged PR with `Closes #N` lands in Done.
- A project already on the kit with no `[tracker]` table gets no new finding on upgrade.

**Out of scope:** Linear, Jira, any two-way sync, syncing plan tasks, any CI workflow, lite tier.

## 2. The feature-line link

A feature line gains an optional trailing link, in one fixed position — last:

```
- [ ] M3-02 — Title — `docs/plans/M3/M3-02-slug.md` (depends on: M2-01) (tracker: #123)
```

Order is title, plan path, dependencies, tracker; every part after the title is optional.
`FEATURE_RE` in `scripts/check_docs.py` gains a final optional group
`(?: \(tracker: #(\d+)\))?`, and `Feature` gains `tracker: str | None`. Without this group a
link at the end is swallowed into the title and the plan path with it, so a ticked feature
would raise `E006`; this is the template-shape rule in the repository's `AGENTS.md`. The
brownfield form already in `references/core/adoption.md §2` step 6 (`(tracker: #123)`) is the
same link; that step is edited to say where on the line it goes.

## 3. `scripts/sync_tracker.py`

Standard library only; shells out to `gh`. Copied to `<project>/tools/sync_tracker.py` at
generation when the tracker is enabled. It imports the parsers from `check_docs.py`, which sits
beside it in both places, so milestones and features are parsed once, one way.

Structure, so it is testable offline:

- `plan_changes(project, board) -> list[Change]` — pure: repo state and board state in, the
  changes to make out.
- `GhBoard` — the only code that runs `gh`; reads issues, milestones and project items, applies
  `Change`s. Tests replace it with a fake.

### 3.1 `sync [--dry-run]`

For every feature in a `planned` or `in progress` milestone:

1. A GitHub milestone `M3 — <milestone title>` exists.
2. An issue `M3-02 — <feature title>` exists and is an item in the project. Found by the
   line's `(tracker: #N)` first; failing that, by searching the repo's issue titles for the
   `M3-02 — ` prefix; created only when neither finds one.
3. The item's Status follows the repo, per §3.2.
4. A feature line without a link gets `(tracker: #N)` written in (§2). This is the only write
   to the repo: a link, not a status. Generated files are never touched.

A dropped milestone closes its GitHub milestone and its open issues as *not planned*. A moved
feature's old issue is closed *not planned* with a comment naming the new ID. A changed title
in the repo renames the issue. `--dry-run` prints every change and applies none. Running `sync`
twice changes nothing the second time.

### 3.2 Status mapping and the branch caveat

| Repo, as checked out | Board |
|---|---|
| feature ticked | Done, issue closed |
| plan `in progress` or `blocked` | In Progress |
| no plan, or plan `grounding` / `planned` | Todo — **unless** the item is In Progress with an assignee |

The exception exists because `sync` sees only the checked-out tree: a claim made on another
branch is invisible to it, and its only trace is the board item (In Progress, assigned). `sync`
therefore never moves an assigned In Progress item back to Todo. Everything else follows the
repo: an issue closed on the board while its feature is unticked is reopened, and a card dragged
to Done early is moved back, each with a one-line reason in the output. `sync` is meant to run
from `main`; from a feature branch it is still safe, by the exception.

### 3.3 `claim <feature-id> [--take] [--release]`

Run at the claim step, before the plan file is written.

| Exit | Meaning | The agent then |
|---|---|---|
| 0 | claimed: issue assigned to the caller (`@me`), Status In Progress | writes the plan and stamp as today |
| 3 | held: assigned to someone else; prints who | stops and reports; claims only on a human's say-so, via `--take` |
| 2 | board not reached: `gh` missing, not logged in, or offline | claims in the repo, names it in the session report's Needs from you |
| 1 | usage error: unknown feature, no tracker configured | stops and reports |

A feature with no issue yet gets one created first. `--take` reassigns to the caller.
`--release` unassigns and sets Todo, for a claim abandoned without Close.

### 3.4 `check`

Read-only: every place the board disagrees with the checked-out repo, by the rules of §3.2,
plus duplicate issues for one feature ID. Exit 0 when none, 1 otherwise.

### 3.5 Failure handling

One item failing does not stop the rest; the run ends with a summary — created, updated,
reopened, failed with the reason. A `gh` error is reported as `gh`'s own message, one line.
At the lite tier, or with `kind = "none"`, `sync` and `check` print why and exit 0, and `claim`
exits 1 (no tracker configured); the procedure runs `claim` only when a tracker is configured,
so in practice an agent never sees that exit.

## 4. Configuration

A `[tracker]` table in `<project>/docs/.check_docs.toml`:

```toml
[tracker]
kind = "github-projects"   # or "none" (the default when the table is absent)
owner = "<user-or-org>"
project = 7                # the project number
```

`check_docs.py` reads and validates it (it stays offline): a `kind` outside the two, a missing
`owner` or a non-positive `project` with `github-projects`, or `github-projects` at the lite
tier, is `E012`, and the tracker is treated as `none`. `assets/templates/check_docs.toml`
documents the table, commented out.

## 5. Linter

- `W009` — a feature in a `planned` or `in progress` milestone has no `(tracker: #N)` while
  `kind = "github-projects"`. A warning, because the board lags the repo by design until the
  next `sync`. Not raised for sketches, `done` or `dropped` milestones, or struck-through moved
  lines.
- `CODES` and the module docstring list `W009`.

## 6. Procedure and template changes

- `skills/project-bootstrap/SKILL.md §4` — the generation gate message asks once, beside the
  hook question: "This repository has a GitHub remote. Create a GitHub Project and sync the
  milestones to it?" Only on a yes: `gh project create`, `gh project link` to the repo, write
  `[tracker]`, copy `sync_tracker.py`, run `sync`, commit the links. Without a GitHub remote the
  question is not asked. The five setup questions (§2) stay five.
- `SKILL.md §5` — the first claim runs `tools/sync_tracker.py claim M0-01` first, when a
  tracker is configured.
- `references/core/parallel-agents.md` — §1 states that, with a tracker, the claim runs `claim`
  first and an exit 3 is the 24-hour rule's hard stop; a new §7 *Tracker mirror* states the
  one-way rule and §3.2's branch caveat.
- `references/core/long-horizon.md §4` — promoting a sketch to `planned` runs `sync`.
- `references/core/lifecycle.md §5` — Close: the PR body carries `Closes #N` for the feature's
  issue.
- `assets/templates/WORKFLOW.md` — the claim and Close steps in the project's words, and one
  line: the board never changes the repo; a card moved by hand is moved back.
- `assets/templates/AGENTS.md` — the `sync` and `claim` commands, under the commands block,
  only when a tracker is configured (a template instruction line, replaced at generation).
- `references/core/adoption.md §2` step 6 — the link's place on the line (§2).
- `README.md` — a short *Tracker sync* section.

## 7. Tests and evals

**`tests/test_sync_tracker.py`** (new), against a fake `GhBoard`:

- each row of §3.2, including the assigned-In-Progress exception and a claim invisible on the
  checked-out branch;
- lookup by link, then by title, with no duplicate created; brownfield links adopted;
- dropped milestone and moved feature close as *not planned*; a renamed feature renames its
  issue;
- repo wins: closed issue reopened, early Done moved back;
- `claim` exits 0, 1, 2, 3, `--take`, `--release`;
- `--dry-run` writes nothing; a second `sync` is a no-op; one failing item does not stop the
  rest;
- links written in the fixed position; no generated file touched.

**`tests/test_check_docs.py`:** `W009` raised and not raised per §5; each `E012` case of §4;
`FEATURE_RE` parses every combination of plan path, dependencies and tracker, and a ticked
feature with all three raises no `E006`. `tests/fixture/full/` gains a `[tracker]` table and
links, so the full fixture lints clean with them.

**`tests/test_kit_consistency.py`:** the config-template test reads nested tables, so it
covers `[tracker]`; the `WORKFLOW.md` template carries `Closes #`.

**Evals:** a new `tracker-claim` scenario on the `generated` fixture with `[tracker]`
configured; the harness puts a fake `gh` first on `PATH` that logs calls and answers from a
script. Assertions: `claim M0-01` runs before the plan file exists; a scripted "held by alice"
stops the claim with no plan written; the plan and milestone edits match the `first-session`
assertions on the free path. The `generation` scenario gains one assertion: with a GitHub
remote in the fixture, the gate message asks about the project.

**Live check:** once, before release, on a throwaway repository under the owner's account,
created only after the owner says yes in that session. It proves what the fake cannot: that the
project's built-in "item closed → Done" rule fires on a merge with `Closes #N`.

## 8. Release

Version 2.10.0 in `skills/project-bootstrap/SKILL.md`, `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json` and the repository's `AGENTS.md`. Results in
`evals/release-j-<date>.md`.

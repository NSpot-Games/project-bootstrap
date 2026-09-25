# Agent economy — design (release H, v2.9.0)

**Date:** 2026-09-25
**Status:** approved in brainstorm, awaiting spec review

## 1. Intent

Projects built on the kit are written by AI coding agents and managed by humans who orchestrate
them. The kit today optimises for correctness at every step: Ground runs the whole test suite,
every task is verified and its output pasted, Close runs the suite again. The result is slow,
token-heavy sessions, test suites that grow without a bar for what earns a place, and CI that
agents design freely from an open-ended "testing strategy" row.

This release makes speed and economy the **default for every project**, not an opt-in mode or a
profile: fewer, more useful tests; checks sized to the moment; one lean CI workflow; a working
loop that keeps the human's attention for decisions only; and model-agnostic instruction tips
distilled from "Getting the most out of Opus 5.5" (claude.dev blog). The docs-as-contract idea
is unchanged — this lightens process, it does not remove it.

**Success criteria**

- Every rule below exists in the skill, cited from the lifecycle and templates.
- `python -m pytest tests -q` passes; `check_docs.py --root .` reports 0 errors, 0 warnings.
- Eval scenarios 61/61 (57 existing plus 4 new).
- One real-repository run from a seed shows one full-suite run per feature (at Close), not one
  at Ground plus per task plus Close.
- No project already on the kit gets a new error on upgrade.

**Out of scope:** the six release-H candidates already in the backlog ship separately. Opus- or
app-specific tips from the blog post (fast mode, image attachment, model-switch flag handling)
are not carried over.

## 2. New core page: `references/core/economy.md`

Five numbered sections; their numbers become contracts once cited.

### 2.1 §1 Tests that earn their place

A test is written only when it does at least one of:

- pins behaviour a user or a contract depends on (public API, a primary journey, a schema);
- reproduces a bug that actually happened;
- guards an invariant that is expensive to debug when broken (concurrency, money, data loss,
  security).

Named as not earning a place: tests that restate the implementation; trivial accessors and
constructors; mocks asserting on mocks; blanket snapshots; a second test for a path already
covered; tests written to raise a coverage number.

Pruning is allowed: an agent may delete a redundant or brittle test in the same commit, with one
line in the plan's Progress notes saying why.

Profiles may raise the bar and say so in one line (see §4.3 of this spec). Every full plan lists
its tests up front in a **Tests this feature adds** section, one line each, so the human reviews
test scope once, in the plan.

### 2.2 §2 When checks run

| When | What runs |
|---|---|
| Inner loop, while editing | typecheck or lint, plus the test file for the module being edited |
| Task boundary | the task's named check — affected package tests, one test, or a run command, whichever is cheapest and still proves the task |
| Close | the full suite, once |
| CI | full suite plus slow and end-to-end tests (§3) |

Ground changes from "run the test suite" to "run the tests for the packages this feature will
touch"; the full suite already ran at the previous Close and in CI.

Evidence is the summary line (`142 passed, 0 failed in 3.1s`) or the one assertion that matters —
never full output. On a failure, paste only the failing excerpt.

Considered and dropped: a recorded "last green" result that Ground reads instead of running
tests. `CURRENT.md` is generated and cannot hold it; a hand-kept record would drift.

### 2.3 §3 CI

The kit does not write project CI; agents build it in feature work. This section is the default
they follow:

- One workflow file with two jobs: a **fast job** on every PR (lint, typecheck, fast tests, docs
  linter) with a budget of under 5 minutes, and a **slow job** on merge to main or nightly
  (end-to-end, integration, load).
- A path filter: docs-only changes run only the docs linter.
- No test matrix unless the profile needs one.
- No deploy or release pipeline until the milestone that actually ships.
- Dependencies are cached.
- One local `check` command runs exactly what the fast job runs; agents run it before pushing,
  never push to find out.
- A profile or an ADR may raise any limit, with its reason written down.

### 2.4 §4 Working for a human

- **Stopping rules.** Keep going when a step needs no input; put status in the same message as
  the next action. Stop before anything destructive (deleting data, force-pushing, rewriting
  history), anything outside the repository, or anything that spends money.
- **Done when / Stop and ask if.** Every plan, full or lite, states checkable end states and the
  conditions that bring the human in.
- **Questions.** A non-blocking question goes to `<project>/docs/OPEN-QUESTIONS.md` with the
  default the agent chose, and work continues. Only a blocking question stops the session.
- **Self-review before human review.** At Close, review the diff against main and list only
  blocking problems, each with file, line, why it is wrong, and how to demonstrate the failure.
  Fix each or record it in the plan before asking for review.
- **Session-end report order.** Needs from you → Done (with evidence summary lines) →
  Findings → Next.

### 2.5 §5 Instruction hygiene

Rules for what agents write into `AGENTS.md`, plans and prompts:

- No "think carefully" / "think step by step" filler.
- Concrete anti-patterns over adjectives: "don't use X, Y, Z", not "keep it clean".
- In Ground bullets and research, mark anything unconfirmed and say where you looked.
- Independent work fans out to subagents, one per package or service; check each one's evidence
  before accepting it.
- Working lists live in files (the plan): context gets summarised, files survive.

## 3. Plan-lite: `references/core/lifecycle.md §3a`

A lettered section, so no existing number moves.

- **Eligible:** a feature the agent expects to take three commits or fewer.
- **Shape:** the same header fields plus `**Shape:** lite`; `## Sessions`; `## Objective`;
  `## Current state` (at most three bullets — Ground still happens); `## Done when`;
  `## Stop and ask if`; `## Tasks` with a verification per task; `## Verification log`. No
  Approach, Alternatives, Risks, Docs to update or Tests this feature adds; tests the feature
  needs are named in its task lines.
- **Promotion:** a fourth task makes it a full plan — add the missing sections and remove the
  Shape line before continuing. Mirrors the small-change rule in `lifecycle.md §3`.
- **Unchanged:** status vocabulary, claiming, Close.

## 4. File changes

### 4.1 New files

- `skills/project-bootstrap/references/core/economy.md` — §2 of this spec.
- `skills/project-bootstrap/assets/templates/plan-lite.md` — the shape in §3, using the field
  formats `check_docs.py` already parses (status line, `## Sessions` stamps, `## Tasks`
  checkboxes).

### 4.2 Edits inside the skill

- `references/core/lifecycle.md` — Ground: package-scoped tests. Plan: Done when, Stop and ask
  if, Tests this feature adds; cite `economy.md §1`. Execute: check cadence and summary-line
  evidence, cite `economy.md §2`. Close (§5): a lettered step for the blocking-only self-review,
  existing steps keep their numbers. New §3a.
- `assets/templates/plan.md` — add `## Done when`, `## Stop and ask if`,
  `## Tests this feature adds`.
- `assets/templates/WORKFLOW.md` — Ground, Execute and Close in the project's words; new §5b
  plan-lite; new §3a session-end report order.
- `assets/templates/AGENTS.md` — a three-line **Stopping rules** block; the Tests convention
  points to the admission rule; Commands must include the single `check` command. Stays under
  120 lines.
- `assets/templates/README.md` — a row for `plan-lite.md`.
- `SKILL.md` — bootstrap copies `plan-lite.md` beside `plan.md`; the commands-token guidance
  requires a `check` command or names the milestone that adds it; version 2.9.0.
- `references/core/lessons.md` — one lesson: why the kit moved from "verify everything, every
  time" to checks sized to the moment.

### 4.3 Profiles

All seven: the architecture row's "testing strategy" becomes "testing strategy and CI budget
(`references/core/economy.md §3`)". Profiles with a reason to raise the bar add one line:
infra-platform keeps failure-injection tests; library-sdk-cli keeps golden examples as tests and
a supported-version matrix; data-ml runs eval runs in the slow job.

### 4.4 Repository root

- `BOOTSTRAP.md §2` — an **Economy** paragraph pointing to the new page.
- `README.md` — mention the new page if it lists core pages.
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — version 2.9.0.

## 5. Linter

- **W008** (new warning): a plan whose `**Shape:**` is `lite` has more than three task
  checkboxes — "promote to a full plan".
- **`**Shape:**` vocabulary:** any value other than `lite` is E013. A missing Shape line means a
  full plan.
- Existing projects: plans without a Shape line are untouched; no new errors.
- The module docstring's code table gains W008.

## 6. Tests and evals

`tests/test_check_docs.py`:

- W008 fires on a lite plan with four tasks; not with three.
- A lite plan with no Approach section lints clean.
- An unknown Shape value raises E013.
- `tests/fixture/` gains one lite plan.

`evals/`: four new scenarios (57 → 61):

1. A two-commit feature gets a lite plan; a fourth task promotes it.
2. The agent declines a coverage-only test and prunes a duplicate with a note.
3. The agent writes CI as one workflow with fast and slow jobs — no matrix, no deploy pipeline.
4. The session-end report opens with Needs from you; a non-blocking question is logged with its
   default.

Then one real-repository run from a seed, as in releases F and G, recording full-suite runs per
feature.

## 7. Release

Branch `procedure/release-h`; version 2.9.0 in all three places; gate is pytest green plus
`check_docs.py --root .` at 0 errors and 0 warnings; evals results committed as in earlier
releases.

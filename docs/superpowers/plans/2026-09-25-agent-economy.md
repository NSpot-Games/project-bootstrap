# Agent Economy (Release H, v2.9.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make lean tests, checks sized to the moment, one CI workflow, a human-orchestrator loop and plan-lite the default for every project the kit bootstraps.

**Architecture:** One new core page (`references/core/economy.md`) holds the policy; lifecycle, templates and profiles carry short lines that cite it (kit docs) or restate it in project words (templates — project docs never cite kit paths). The linter learns one field (`**Shape:** lite`) and one warning (W008). Evals gain assertions in two scenarios and one new scenario.

**Tech Stack:** Markdown, Python 3.11+ (stdlib only), pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-agent-economy-design.md`

## Global Constraints

- Version `2.9.0` in `skills/project-bootstrap/SKILL.md` metadata, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — all three together.
- Inside `skills/project-bootstrap/`, kit paths are relative to the skill root (`references/core/economy.md §3`); at the repo root they are full; project paths are `<project>/...`.
- Templates never cite kit paths (`references/...`): a bootstrapped project does not carry the kit. Templates restate rules in the project's words.
- Section numbers are contracts once cited: append lettered sections (`§3a`, `2a.`), never renumber.
- No double-brace placeholders outside `skills/project-bootstrap/assets/templates/`.
- `SKILL.md` stays under 500 lines; the `AGENTS.md` template stays under 120 lines.
- Gate before every commit: `python -m pytest tests -q` passes and `python skills/project-bootstrap/scripts/check_docs.py --root .` prints `0 error(s), 0 warning(s)`.
- Commit messages end with:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01PxkgM8j4J4RCz9jdFxKsaH
  ```
- Branch: `procedure/release-h` (already checked out).

## Spec amendments (applied in Task 1)

Found while planning; the spec is corrected so plan and spec agree:

1. **Evals.** "57/57" counts *assertions* across six bootstrap-step scenarios, not scenarios. The scenarios test bootstrap steps, not feature work, so "a lite plan promoted at a fourth task" and "declines a coverage-only test" cannot be exercised by the harness; W008 promotion is covered by linter tests instead. New eval work: +3 assertions in `generation`, +2 in `first-session`, and one new scenario `ci-default` with 7 assertions — 57 → 69 assertions, 6 → 7 scenarios.
2. **Real-repository run.** A seed run is a bootstrap, not feature work, so it cannot count full-suite runs per feature. It checks instead that the bootstrap still scores at the G level (23/1/0 or better) and that the generated `AGENTS.md` and `WORKFLOW.md` carry the new rules.
3. **Fixture.** Linter tests write the lite plan into a temporary copy of `tests/fixture/valid/` rather than adding it to the fixture, so the generated indexes in the fixture do not churn.
4. **Profiles.** Six profiles have an architecture row; `research-prototype` has none and is unchanged.
5. **Plan-lite keeps `## Progress notes`**: the linter reads the last note into `CURRENT.md`.
6. **Templates restate rather than cite** economy.md (Global Constraints).

## Review Focus

- An existing project upgrading to 2.9.0 whose plans have no `**Shape:**` line must get no new finding — pinned in Task 2 (full plan with five tasks, no W008).
- A lite plan whose tasks are all ticked (four ticked tasks) is still a lite plan over the cap — W008 counts all task checkboxes, open or ticked; pinned in Task 2.
- `**Shape:** Lite` (capitalised) or `**Shape:** lite ` (trailing space) must parse as lite, not E013 — pinned in Task 2.
- `**Shape:**` with an empty value (template left half-edited) must behave as a full plan, not E013 — pinned in Task 2.
- The plan-lite template itself, once its tokens are filled, must lint clean with no W008 — pinned in Task 3.

---

### Task 1: Correct the spec

**Files:**
- Modify: `docs/superpowers/specs/2026-09-25-agent-economy-design.md`

- [ ] **Step 1: Apply the six amendments**

In §1 Success criteria, replace:
```
- Eval scenarios 61/61 (57 existing plus 4 new).
- One real-repository run from a seed shows one full-suite run per feature (at Close), not one
  at Ground plus per task plus Close.
```
with:
```
- Eval assertions 69/69 (57 existing, plus 5 in existing scenarios and 7 in the new
  `ci-default` scenario).
- One real-repository run from a seed scores 23/1/0 or better, and the generated `AGENTS.md`
  and `WORKFLOW.md` carry the stopping rules, the check cadence and plan-lite.
```

In §3 Shape, after `## Tasks` with a verification per task;` insert `` `## Progress notes`; `` so the line reads `` ... `## Tasks` with a verification per task; `## Progress notes`; `## Verification log`. ``

In §4.2, add as the first bullet:
```
- Templates restate the rules in the project's words and never cite `references/...`: a
  bootstrapped project does not carry the kit.
```

In §4.3, replace `All seven:` with `The six profiles with an architecture row (research-prototype has none):`.

Replace §6 entirely with:
```
## 6. Tests and evals

`tests/test_check_docs.py` (lite plans are written into a temporary copy of the valid fixture,
so the fixture's generated indexes do not churn):

- W008 fires on a lite plan with four tasks, ticked or not; not with three.
- A lite plan with no Approach section lints clean.
- A full plan (no Shape line, or an empty one) with five tasks raises nothing new.
- `Lite` in any case parses as lite; an unknown Shape value raises E013.
- The plan-lite template, tokens filled, lints clean.

`evals/`: the harness tests bootstrap steps, not feature work, so promotion and test admission
are covered by the linter tests above. Eval additions, 57 → 69 assertions:

- `generation` (+3): `tools/templates/plan-lite.md` copied; `AGENTS.md` carries the stopping
  rules; `AGENTS.md` Commands names a `check` command or the milestone that adds it.
- `first-session` (+2): the claimed plan carries `## Done when`; the final message opens with
  Needs from you.
- New scenario `ci-default` (7): one workflow file; a PR trigger; a slow job gated to main or a
  schedule; a path filter; no deploy or publish step; `AGENTS.md` names the `check` command;
  the project lints clean.

Then one real-repository run from a seed, as in releases F and G: the bootstrap still scores
23/1/0 or better, and the generated process files carry the new rules.
```

- [ ] **Step 2: Lint and commit**

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .`
Expected: `0 error(s), 0 warning(s)`

```bash
git add docs/superpowers/specs/2026-09-25-agent-economy-design.md docs/superpowers/plans/2026-09-25-agent-economy.md
git commit -m "Spec: correct eval counts, real-run measure, profiles and plan-lite sections; add the plan"
```
(with the trailer lines from Global Constraints)

---

### Task 2: Linter — `**Shape:**` and W008

**Files:**
- Modify: `skills/project-bootstrap/scripts/check_docs.py` (docstring lines 8-19, `CODES` ~line 56, constants ~line 70, `Plan` dataclass ~line 275, `parse_plan` ~line 402, `check_vocabulary` ~line 735, `check_sizes` ~line 799)
- Test: `tests/test_check_docs.py`

**Interfaces:**
- Produces: `Plan.shape: str` (lower-cased, `""` when absent or empty), `Plan.tasks_total: int`; constants `PLAN_SHAPES = ("lite",)`, `LITE_MAX_TASKS = 3`; finding code `W008`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_check_docs.py`:

```python
LITE_PLAN = """# M1-03 — Third thing
**Status:** planned
**Shape:** lite
**Milestone:** M1
**Branch:** feat/M1-03-third-thing
**Design docs:**
**ADRs:**
**Depends on:**

## Sessions

## Objective
Do the third thing.

## Done when
- The third thing runs on the example instance.

## Stop and ask if
- The third thing needs a schema change.

## Current state
- Nothing exists yet; checked `src/`.

## Tasks
{tasks}
## Progress notes

## Verification log
"""


def write_lite_plan(root: Path, n_tasks: int, shape_line: str = "**Shape:** lite\n", ticked: bool = False) -> None:
    box = "x" if ticked else " "
    tasks = "".join(f"- [{box}] T{i} — Step {i}. **Verify:** `pytest tests/test_third.py`\n" for i in range(1, n_tasks + 1))
    text = LITE_PLAN.format(tasks=tasks).replace("**Shape:** lite\n", shape_line)
    p = root / "docs" / "plans" / "M1" / "M1-03-third-thing.md"
    p.write_text(text, encoding="utf-8", newline="\n")


def test_lite_plan_with_three_tasks_lints_clean(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 3)
    found = cd.run(root)
    assert errors(found) == []
    assert "W008" not in codes(found)


def test_w008_lite_plan_over_three_tasks(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 4)
    found = cd.run(root)
    assert "W008" in codes(found)
    assert errors(found) == []


def test_w008_counts_ticked_tasks_too(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 4, ticked=True)
    assert "W008" in codes(cd.run(root))


def test_w008_not_raised_for_full_plan_with_many_tasks(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 5, shape_line="")
    found = cd.run(root)
    assert "W008" not in codes(found) and "E013" not in codes(found)


def test_empty_shape_value_is_a_full_plan(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 5, shape_line="**Shape:**\n")
    found = cd.run(root)
    assert "W008" not in codes(found) and "E013" not in codes(found)


def test_shape_is_case_and_space_insensitive(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 4, shape_line="**Shape:** Lite  \n")
    found = cd.run(root)
    assert "W008" in codes(found) and "E013" not in codes(found)


def test_e013_unknown_plan_shape(tmp_path):
    root = make_project(tmp_path)
    write_lite_plan(root, 2, shape_line="**Shape:** tiny\n")
    assert "E013" in codes(cd.run(root))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_check_docs.py -q -k "lite or shape or w008"`
Expected: `test_w008_*`, `test_shape_is_case_and_space_insensitive` and `test_e013_unknown_plan_shape` FAIL (no W008, no shape check); the two "clean"/"full plan" tests may already pass.

- [ ] **Step 3: Implement**

Docstring — after the line `  W003 generated file differs          W006 AGENTS.md over 120 lines` replace the W007 line with:
```
  W007 cited project file not written yet (no CURRENT.md, bootstrap in progress)
  W008 lite plan over 3 tasks (promote to a full plan)
```

`CODES` — after the `"W007": ...` entry add:
```python
    "W008": "lite plan over 3 tasks; promote to a full plan",
```

Constants — after `PLAN_STATUSES = (...)` add:
```python
PLAN_SHAPES = ("lite",)  # no Shape line, or an empty one, means a full plan
LITE_MAX_TASKS = 3
```

`Plan` dataclass — after `tasks_open: int` add:
```python
    shape: str = ""
    tasks_total: int = 0
```

`parse_plan` — replace the `tasks_open = ...` line and the `return Plan(...)` statement with:
```python
    task_boxes = [m.group(1) for m in TASK_RE.finditer(section_body(text, "Tasks"))]
    tasks_open = sum(1 for b in task_boxes if b == " ")
    milestone = field_value(text, "Milestone") or pid.split("-")[0]
    shape = (field_value(text, "Shape") or "").lower()
    return Plan(pid, path, title, status, moved_to, milestone, parse_ids(field_value(text, "Depends on")),
                stamps, notes[-1] if notes else "", tasks_open, shape, len(task_boxes))
```
(the existing `milestone = ...` line moves above; delete the old copy.)

`check_vocabulary` — inside the `for pl in project.plans.values():` loop, after the status check, add:
```python
        if pl.shape and pl.shape not in PLAN_SHAPES:
            out.append(Finding("E013", rel(cfg, pl.path), 1,
                               f"plan shape {pl.shape!r} is not one of: {', '.join(PLAN_SHAPES)} (omit the line for a full plan)"))
```

`check_sizes` — update the docstring to `"""W004: a planned or in-progress milestone holds 3-10 features (layers.md §5). W006: AGENTS.md stays under 120 lines (lessons.md §1.17). W008: a lite plan holds at most three tasks (lifecycle.md §3a)."""` and, before the `agents = cfg.root / "AGENTS.md"` line, add:
```python
    for pl in project.plans.values():
        if pl.shape == "lite" and pl.tasks_total > LITE_MAX_TASKS:
            out.append(Finding("W008", rel(cfg, pl.path), 1,
                               f"{pl.id} is a lite plan with {pl.tasks_total} tasks; promote it to a full plan"))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests -q`
Expected: all pass (the new seven included). `tests/test_kit_consistency.py::test_every_finding_code_cited_in_the_docs_exists_in_the_linter` must still pass.

- [ ] **Step 5: Lint and commit**

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`. (`lifecycle.md §3a` is cited only inside a Python docstring, which the linter does not read; the section is written in Task 4.)

```bash
git add skills/project-bootstrap/scripts/check_docs.py tests/test_check_docs.py
git commit -m "Linter: **Shape:** lite on plans, W008 for a lite plan over three tasks, E013 for an unknown shape"
```

---

### Task 3: The economy page

**Files:**
- Create: `skills/project-bootstrap/references/core/economy.md`

- [ ] **Step 1: Write the page**

Create `skills/project-bootstrap/references/core/economy.md` with exactly:

````markdown
# Economy

Agents write the code; humans direct the work. Every check an agent runs costs time and tokens,
and every test it adds is a test every later session runs and reads. This page is how the kit
keeps that cost proportional: tests that earn their place, checks sized to the moment, one lean
CI workflow, a working loop that spends the human's attention on decisions only, and
instructions free of filler. It is the default for every project; a profile or an ADR may raise
any bar here, with its reason written down. Each project states these rules in its own words in
`<project>/AGENTS.md` and `<project>/docs/WORKFLOW.md`; this page is where the reasons live.

## 1. Tests that earn their place

A test is written only when it does at least one of three things:

- pins behaviour a user or a contract depends on — a public API, a primary journey, a schema;
- reproduces a bug that actually happened;
- guards an invariant that is expensive to debug when broken — concurrency, money, data loss,
  security.

These do not earn a place: tests that restate the implementation; trivial accessors and
constructors; mocks asserting on mocks; blanket snapshots; a second test for a path already
covered; tests written to raise a coverage number.

Pruning is allowed. An agent may delete a redundant or brittle test in the same commit as the
change that exposed it, with one line in the plan's Progress notes saying why.

Every full plan lists its tests up front under **Tests this feature adds**, one line each, so the
human reviews test scope once, in the plan, instead of discovering it in the diff. A lite plan
(`references/core/lifecycle.md §3a`) names its tests in its task lines.

## 2. When checks run

| When | What runs |
|---|---|
| While editing | typecheck or lint, plus the test file for the module being edited |
| At a task's end | the task's named check — the affected packages' tests, one test, or a run command, whichever is cheapest and still proves the task |
| At Close | the full suite, once |
| In CI | the full suite plus slow and end-to-end tests (`§3`) |

Ground runs the tests for the packages the feature will touch, not the full suite: the full suite
ran at the previous feature's Close and runs in CI.

Evidence is the summary line — `142 passed, 0 failed in 3.1s` — or the one assertion that
matters, never the full output. On a failure, paste only the failing excerpt. A plan is read by
every later session that touches the area; pasted logs are a cost each of them pays.

## 3. CI

The kit does not write a project's CI; agents build it during feature work, from the testing
strategy and CI budget in `<project>/docs/design/architecture.md`. The default they follow:

- **One workflow file, two jobs.** A fast job on every pull request — lint, typecheck, fast
  tests, the docs linter — with a budget of under five minutes. A slow job on merge to `main` or
  nightly — end-to-end, integration, load.
- **A path filter.** A change that touches only docs runs only the docs linter.
- **No matrix** unless the profile needs one.
- **No deploy or release pipeline** until the milestone that actually ships something.
- **Dependencies cached.**
- **One local `check` command** runs exactly what the fast job runs. Agents run it before
  pushing and never push to find out.

A budget raised by a profile or an ADR says why in the same place.

## 4. Working for a human

- **Stopping rules.** Keep going when a step needs no input, and put the status in the same
  message as the next action. Stop before anything destructive — deleting data, force-pushing,
  rewriting history — anything outside the repository, or anything that spends money.
- **Done when and Stop and ask if.** Every plan, full or lite, states checkable end states and
  the conditions that bring the human in, before work starts.
- **Questions.** A question that does not block the next step goes to
  `<project>/docs/OPEN-QUESTIONS.md` with the default the agent chose, and work continues on that
  default. Only a question that blocks stops the session.
- **Self-review before human review.** At Close, review the diff against `main` and list only
  blocking problems, each with the file, the line, why it is wrong, and how to show it failing.
  Fix each, or record it in the plan, before asking a human to review.
- **The session-end report**, in this order: Needs from you (decisions, approvals, answers) →
  Done (with evidence summary lines) → Findings → Next. The human reads the first part first.

## 5. Instruction hygiene

What agents write into `<project>/AGENTS.md`, plans and prompts:

- No "think carefully" or "think step by step". Current models reason before they answer;
  the line costs every session and buys nothing.
- Concrete anti-patterns over adjectives: "don't use X, Y or Z", not "keep it clean". An
  adjective swaps one default for another; a list removes the defaults named.
- In Ground bullets and research, mark anything unconfirmed and say where you looked.
- Independent work fans out to subagents, one per package or service; check each one's evidence
  before accepting its result.
- Working lists live in files — the plan — because a long session's context is summarised and
  a file survives it.
````

- [ ] **Step 2: Lint**

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .`
Expected: E002 on `references/core/lifecycle.md §3a` (written in Task 4). If that is the only finding, continue; Task 4 clears it before the next commit. Do not commit yet — Task 3 and Task 4 commit together.

---

### Task 4: Lifecycle, plan templates, plan-lite

**Files:**
- Modify: `skills/project-bootstrap/references/core/lifecycle.md`
- Modify: `skills/project-bootstrap/assets/templates/plan.md`
- Create: `skills/project-bootstrap/assets/templates/plan-lite.md`
- Modify: `skills/project-bootstrap/assets/templates/README.md`
- Modify: `tests/test_kit_consistency.py`, `tests/test_check_docs.py`

**Interfaces:**
- Consumes: `Plan.shape`, W008 (Task 2); `references/core/economy.md §1–§5` (Task 3).
- Produces: `references/core/lifecycle.md §3a`; `assets/templates/plan-lite.md` with `**Shape:** lite`; plan sections `## Done when`, `## Stop and ask if`, `### Tests this feature adds`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_check_docs.py`:
```python
def test_plan_lite_template_filled_lints_clean(tmp_path):
    root = make_project(tmp_path)
    tpl = (Path(__file__).resolve().parents[1] / "skills" / "project-bootstrap" / "assets" / "templates" / "plan-lite.md").read_text(encoding="utf-8")
    text = (tpl.replace("{{n}}", "1").replace("{{nn}}", "03").replace("{{Title}}", "Third thing")
               .replace("{{slug}}", "third-thing").replace("**Status:** grounding", "**Status:** planned"))
    (root / "docs" / "plans" / "M1" / "M1-03-third-thing.md").write_text(text, encoding="utf-8", newline="\n")
    found = cd.run(root)
    assert errors(found) == []
    assert "W008" not in codes(found)
    assert cd.parse_plan(root / "docs" / "plans" / "M1" / "M1-03-third-thing.md").shape == "lite"
```

In `tests/test_kit_consistency.py`, add:
```python
def test_plan_templates_carry_the_orchestrator_sections():
    full = (TEMPLATES / "plan.md").read_text(encoding="utf-8")
    lite = (TEMPLATES / "plan-lite.md").read_text(encoding="utf-8")
    for heading in ("## Done when", "## Stop and ask if", "## Tasks", "## Sessions", "## Progress notes"):
        assert heading in full and heading in lite, heading
    assert "### Tests this feature adds" in full
    assert "**Shape:** lite" in lite and "**Shape:**" not in full
    assert "## Approach" not in lite
```

Run: `python -m pytest tests -q -k "plan_lite_template or orchestrator_sections"`
Expected: FAIL (`plan-lite.md` does not exist).

- [ ] **Step 2: Write `assets/templates/plan-lite.md`**

```markdown
# M{{n}}-{{nn}} — {{Title}}
**Status:** grounding
**Shape:** lite
**Milestone:** M{{n}}
**Branch:** feat/M{{n}}-{{nn}}-{{slug}}
**Design docs:**
**ADRs:**
**Depends on:**

## Sessions

## Objective
## Done when
## Stop and ask if
## Current state
## Tasks
- [ ] T1 — ... **Verify:** `command`
## Progress notes
## Verification log
```

- [ ] **Step 3: Edit `assets/templates/plan.md`**

Replace:
```
## Objective
## Current state
## Approach
### Alternatives considered
### Risks
### Docs to update
## Tasks
```
with:
```
## Objective
## Done when
## Stop and ask if
## Current state
## Approach
### Alternatives considered
### Risks
### Docs to update
### Tests this feature adds
## Tasks
```

- [ ] **Step 4: Edit `assets/templates/README.md`**

In the final paragraph, replace ``the object templates `plan.md`, `milestone.md`, `adr.md` and
`evidence.md` are copied`` with ``the object templates `plan.md`, `plan-lite.md`, `milestone.md`, `adr.md` and
`evidence.md` are copied``. In the `{{commands}}` row, replace the meaning with:
`Build, test, lint, run commands, always including one `check` command that runs exactly what CI's fast job runs; before code exists, the linter command plus a line naming the milestone that adds the rest`.

- [ ] **Step 5: Edit `references/core/lifecycle.md`**

§1 Ground — replace `run the test suite to see what currently passes and what does not,` with `run the tests for the packages the feature will touch (the full suite ran at the previous Close and runs in CI, `references/core/economy.md §2`),`. After the sentence ending `before brainstorming starts.` insert: ` Mark any bullet you could not confirm and say where you looked.`

§1 Plan — replace the whole paragraph with:
```
**Plan.** Break the approach into tasks, each sized to one commit and each naming how it will be verified — the cheapest check that still proves the task (`references/core/economy.md §2`): a command, a manual check, a specific assertion, not "test it works." State **Done when** (checkable end states) and **Stop and ask if** (the conditions that bring the human in). List every test the feature adds under **Tests this feature adds**, one line each; a test earns its place only by the rule in `references/core/economy.md §1`. Order tests before the code they check where tests apply to the change. A feature expected to take three commits or fewer may use a lite plan instead (`§3a`). Set the plan's status to `planned` and link it from the milestone's feature line, so the milestone always points at real, current work.
```

§1 Execute — replace `do the work, run the verification, paste the evidence into the plan,` with `do the work, run the task's check, paste its summary line into the plan as evidence (never the full output),`.

§1 Close — replace `**Close.** All tasks ticked with evidence, the suite green` with `**Close.** A self-review of the diff against `main` for blocking problems only, all tasks ticked with evidence, the full suite run once and green`.

After §3's last paragraph, before `## 4. Experiments`, insert:
```
## 3a. Plan-lite

A feature expected to take three commits or fewer may use `<project>/tools/templates/plan-lite.md`
instead of the full plan: the same header plus `**Shape:** lite`, Sessions, Objective, Done when,
Stop and ask if, Current state (at most three bullets — Ground still happens), Tasks with a check
each, Progress notes and a verification log. No Approach, alternatives, risks, docs to update or
separate test list; any test the feature needs is named in its task line. Status, claiming and
Close are unchanged.

The promotion rule mirrors `§3`: a fourth task makes it a full plan. Copy the missing sections
from `<project>/tools/templates/plan.md`, delete the Shape line, and continue; the linter warns
(`W008`) on a lite plan holding more than three tasks. Lite and standard projects differ here:
a lite-tier project keeps its checkboxes on the roadmap and writes no plans at all
(`references/core/tiers.md §2`).
```

§5 — after item 2, insert:
```
2a. Before asking for review, review the diff against `main` and list only blocking problems — each with the file, the line, why it is wrong, and how to show it failing — then fix each or record it in the plan (`references/core/economy.md §4`).
```
and replace item 2's opening `The test suite is green` with `The full suite, run once at Close, is green`.

- [ ] **Step 6: Run tests and lint**

Run: `python -m pytest tests -q` → all pass.
Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

- [ ] **Step 7: Commit (Tasks 3 and 4 together)**

```bash
git add skills/project-bootstrap/references/core/economy.md skills/project-bootstrap/references/core/lifecycle.md skills/project-bootstrap/assets/templates/plan.md skills/project-bootstrap/assets/templates/plan-lite.md skills/project-bootstrap/assets/templates/README.md tests/test_check_docs.py tests/test_kit_consistency.py
git commit -m "Economy page, plan-lite (lifecycle §3a) and the orchestrator sections in the plan templates"
```

---

### Task 5: Project templates — WORKFLOW.md and AGENTS.md

**Files:**
- Modify: `skills/project-bootstrap/assets/templates/WORKFLOW.md`
- Modify: `skills/project-bootstrap/assets/templates/AGENTS.md`
- Modify: `tests/test_kit_consistency.py`

- [ ] **Step 1: Write the failing test**

In `tests/test_kit_consistency.py`, add:
```python
def test_project_templates_carry_the_economy_rules_without_citing_the_kit():
    workflow = (TEMPLATES / "WORKFLOW.md").read_text(encoding="utf-8")
    agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
    assert "tools/templates/plan-lite.md" in workflow
    assert "## 5b. Plan-lite" in workflow and "## 3a. Working for a human" in workflow
    assert "Needs from you" in workflow
    assert "## Stopping rules" in agents and "Stop and ask before" in agents
    assert "`check`" in agents
    for text in (workflow, agents):
        assert "references/" not in text
    assert len(agents.rstrip("\n").split("\n")) < 120
```
Also in `test_workflow_template_points_at_the_object_templates_and_carries_no_tokens`, add a line `assert "tools/templates/plan-lite.md" in workflow` next to the `plan.md` assertion.

Run: `python -m pytest tests/test_kit_consistency.py -q` → FAIL.

- [ ] **Step 2: Edit `assets/templates/WORKFLOW.md`**

§2 — replace the Ground, Plan, Execute and Close lines with:
```
**Ground** — read `docs/CURRENT.md`, then AGENTS/CLAUDE, the milestone, the cited design docs; grep `decisions/`; run the tests for the packages the feature will touch (the full suite ran at the last Close and runs in CI); inspect the packages touched; read the previous feature's plan. Write 3–10 concrete bullets into **Current state**, marking anything you could not confirm and where you looked. If the feature is done, mis-scoped, or blocked: stop and say so.
```
```
**Plan** — tasks, each one commit, each naming its verification: the cheapest check that still proves it. Fill **Done when** and **Stop and ask if**. List every new test under **Tests this feature adds**; a test earns its place only if it pins behaviour a user or contract depends on, reproduces a real bug, or guards an invariant that is expensive to debug — not implementation restatements, trivial accessors, mocks of mocks, blanket snapshots, or coverage padding. Tests first where tests apply. Three commits or fewer: a lite plan (§5b). Set plan status `planned`; link it from the milestone.
```
```
**Execute** — task by task: do, run the task's check (while editing: typecheck plus the test file you touch), paste its summary line as evidence — never full output — tick, commit `M1-03: ...`, note anything learned. A redundant or brittle test may be deleted with a one-line note. Plan wrong? Fix the plan first.
```
```
**Close** — review the diff against `main`: blocking problems only, each with file, line, why, and how to show it failing; fix or record each. Then the full suite, once, green; all tasks ticked; docs updated; ADRs reviewed: accepted by a human, or left `proposed` (non-blocking unless `**Blocking:** yes`); feature ticked in the milestone; plan `done`. Run `python tools/check_docs.py --fix`. If this is the milestone's last feature, run the roadmap review checklist (§10).
```

After §3, before `## 4. Branches and commits`, insert:
```
## 3a. Working for a human
A question that doesn't block the next step goes to `docs/OPEN-QUESTIONS.md` with the default you chose; carry on with that default. Only a blocking question stops the session. End every session with a report in this order: **Needs from you** (decisions, approvals, answers) → **Done** (with evidence summary lines) → **Findings** → **Next**.
```

After §5a, before `## 6. When things don't fit`, insert:
```
## 5b. Plan-lite
A feature you expect to take three commits or fewer may use `tools/templates/plan-lite.md`: header with `**Shape:** lite`, Objective, Done when, Stop and ask if, up to three Current state bullets, Tasks, Progress notes, Verification log. Tests go in the task lines. A fourth task makes it a full plan: copy the missing sections from `tools/templates/plan.md` and delete the Shape line. The linter warns (W008) on a lite plan over three tasks.
```

§7 — replace with:
```
## 7. Plan template
Copy `tools/templates/plan.md` (or `tools/templates/plan-lite.md`, §5b) to `docs/plans/M<n>/M<n>-<nn>-<slug>.md` and fill every double-brace token; none may remain.
```

- [ ] **Step 3: Edit `assets/templates/AGENTS.md`**

After the `## How to work` section's last line (`Small fixes skip the plan (`docs/WORKFLOW.md` §5).`) insert:
```

## Stopping rules
- Keep going when a step needs no input; put the status in the same message as the next action.
- Stop and ask before anything destructive (deleting data, force-pushing, rewriting history), anything outside this repository, or anything that spends money.
- A question that doesn't block goes to `docs/OPEN-QUESTIONS.md` with the default you chose; continue on it.
- End each session with the report `docs/WORKFLOW.md` §3a orders: Needs from you first.
```

Under `## Commands`, after `{{commands}}` add the line:
```
`check` runs exactly what CI's fast job runs; run it before pushing, never push to find out.
```

In `## Conventions`, replace `- Tests: note what is test-first for this project.` with:
```
- Tests: only tests that pin a contract, reproduce a real bug, or guard an expensive invariant (`docs/WORKFLOW.md` §2). Note what is test-first for this project.
```

In `## Don't`, after `- Don't tick a box without running the verification.` add:
```
- Don't run the full suite after every change: the task's check while working, the full suite once at Close.
- Don't paste full test output as evidence; paste the summary line.
```

- [ ] **Step 4: Run tests and lint**

Run: `python -m pytest tests -q` → all pass.
Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

- [ ] **Step 5: Commit**

```bash
git add skills/project-bootstrap/assets/templates/WORKFLOW.md skills/project-bootstrap/assets/templates/AGENTS.md tests/test_kit_consistency.py
git commit -m "Templates: check cadence, test admission, stopping rules, session report order and plan-lite in project words"
```

---

### Task 6: Profiles

**Files:**
- Modify: `skills/project-bootstrap/references/profiles/{curated-directory,data-driven-product,data-ml,infra-platform,library-sdk-cli,web-app-saas}.md` (the architecture row in §2)
- Modify: `tests/test_kit_consistency.py`

- [ ] **Step 1: Write the failing test**

```python
def test_every_architecture_row_names_the_ci_budget():
    for p in sorted((SKILL_DIR / "references" / "profiles").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        row = next((ln for ln in text.splitlines() if ln.startswith("| `<project>/docs/design/architecture.md`")), None)
        if row is None:
            continue  # research-prototype writes no architecture doc
        assert "CI budget (`references/core/economy.md §3`)" in row, p.name
```
Run: `python -m pytest tests/test_kit_consistency.py -q -k ci_budget` → FAIL.

- [ ] **Step 2: Edit the six rows** (exact replacements inside each architecture row):

- `curated-directory.md`: `hosting shape; testing strategy;` → `hosting shape; testing strategy and CI budget (`references/core/economy.md §3`);`
- `data-driven-product.md`: `offline and failure behaviour; testing strategy; security` → `offline and failure behaviour; testing strategy and CI budget (`references/core/economy.md §3`); security`
- `data-ml.md`: `persistence (artifacts, checkpoints); testing strategy |` → `persistence (artifacts, checkpoints); testing strategy and CI budget (`references/core/economy.md §3`), with eval runs in the slow job |`
- `infra-platform.md`: `testing strategy, including failure injection |` → `testing strategy, including failure injection, and CI budget (`references/core/economy.md §3`) |`
- `library-sdk-cli.md`: `testing strategy (unit, integration, golden examples) |` → `testing strategy (unit, integration, golden examples) and CI budget (`references/core/economy.md §3`), with the supported-version matrix in the slow job |`
- `web-app-saas.md`: `persistence and caching; testing strategy |` → `persistence and caching; testing strategy and CI budget (`references/core/economy.md §3`) |`

- [ ] **Step 3: Run tests and lint, commit**

Run: `python -m pytest tests -q` → pass. Lint → `0 error(s), 0 warning(s)`.
```bash
git add skills/project-bootstrap/references/profiles tests/test_kit_consistency.py
git commit -m "Profiles: the architecture doc states a CI budget; infra, library and data-ml say where they raise it"
```

---

### Task 7: SKILL.md, lessons, BOOTSTRAP, README, version

**Files:**
- Modify: `skills/project-bootstrap/SKILL.md` (§4 step 1, §4 step 3, §5, metadata version)
- Modify: `skills/project-bootstrap/references/core/lessons.md`
- Modify: `BOOTSTRAP.md` (§2), `README.md` (core list)
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] **Step 1: SKILL.md**

§4 step 1: replace ``Copy the object templates `assets/templates/plan.md`,`` with ``Copy the object templates `assets/templates/plan.md`, `assets/templates/plan-lite.md`,``.

§4 step 3: replace `` Before any code exists, `{{commands}}` is the linter command plus one line naming the
   milestone that adds the rest;`` with `` Before any code exists, `{{commands}}` is the linter command plus one line naming the
   milestone that adds the rest, including the one `check` command that runs what CI's fast job
   runs (`references/core/economy.md §3`);``.

§5: before the sentence `The bootstrap ends here;` insert `End with the session report `references/core/economy.md §4` orders, Needs from you first. `.

Metadata: `version: 2.8.0` → `version: 2.9.0` (check the exact key spelling in the frontmatter).

- [ ] **Step 2: lessons.md** — append at the end:
```

## 4. Sized to the agent

1. **Verifying everything, every time, is not rigour.** Through v2.8 the lifecycle ran the whole suite at Ground, a check per task with its output pasted, and the suite again at Close, and said nothing about which tests were worth writing. Projects built by agents grew slow sessions, long plans full of logs, and test suites no one had chosen. What changed: `references/core/economy.md` — tests that earn their place, checks sized to the moment, one lean CI workflow, stopping rules and a session report that puts the human's decisions first — and plan-lite for features of three commits or fewer (`references/core/lifecycle.md §3a`).
```

- [ ] **Step 3: BOOTSTRAP.md §2** — after the **Tiers** paragraph, insert:
```

**Economy** (`skills/project-bootstrap/references/core/economy.md`) — tests that earn their place,
checks sized to the moment (the full suite once, at Close), one CI workflow with a fast and a slow
job, stopping rules and a session report that opens with what the human must decide.
```

- [ ] **Step 4: README.md** — replace `long-horizon rules, parallel agents, tiers, adoption, lessons.` with `long-horizon rules, parallel agents, tiers, economy, adoption, lessons.`

- [ ] **Step 5: Version** — in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` change `"2.8.0"` to `"2.9.0"`; update `AGENTS.md` (repo root) `The version is `2.8.0`` → `2.9.0`.

- [ ] **Step 6: Tests, lint, commit**

Run: `python -m pytest tests -q` → pass (`test_version_agrees_across_skill_and_manifests`, `test_skill_md_is_under_500_lines`, `test_every_skill_relative_path_in_skill_md_exists` included). Lint → `0 error(s), 0 warning(s)`.
```bash
git add skills/project-bootstrap/SKILL.md skills/project-bootstrap/references/core/lessons.md BOOTSTRAP.md README.md AGENTS.md .claude-plugin
git commit -m "Release H (v2.9.0): SKILL.md copies plan-lite and asks for a check command; lessons, BOOTSTRAP and README name the economy page"
```

---

### Task 8: Evals — fixture refresh, assertions, `ci-default`

**Files:**
- Modify: `evals/fixtures/generated/tools/templates/plan.md`, create `evals/fixtures/generated/tools/templates/plan-lite.md`
- Modify: `evals/fixtures/generated/AGENTS.md`, `evals/fixtures/generated/docs/WORKFLOW.md`
- Modify: `evals/evals.json`, `evals/README.md`

- [ ] **Step 1: Refresh the `generated` fixture** (it represents a project the moment generation finished, so it must match 2.9.0 generation):

- Copy `skills/project-bootstrap/assets/templates/plan.md` and `plan-lite.md` over/into `evals/fixtures/generated/tools/templates/` unchanged.
- In `evals/fixtures/generated/AGENTS.md`, add the `## Stopping rules` block from Task 5 Step 3 after the How to work section, the `check` line under Commands, and the two Don't lines — worded exactly as in the template (there are no tokens in them). Do not add a concrete `check` command to the fixture: the `ci-default` scenario asserts the agent adds one.
- In `evals/fixtures/generated/docs/WORKFLOW.md`, apply the Task 5 Step 2 edits (§2 four lines, new §3a, new §5b, §7).

Run: `python skills/project-bootstrap/scripts/check_docs.py --root evals/fixtures/generated` → `0 error(s)` (warnings the fixture had before are acceptable; compare against `git stash`-free baseline by running it on `main`'s copy if unsure).

- [ ] **Step 2: Add assertions** — in `evals/evals.json`:

Append to scenario 6 (`generation`) `assertions`:
```json
{"text": "The plan-lite object template was copied", "check": "file_exists", "path": "tools/templates/plan-lite.md"},
{"text": "AGENTS.md carries the stopping rules", "check": "grep", "path": "AGENTS.md", "pattern": "(?m)^## Stopping rules"},
{"text": "AGENTS.md names a check command, or the milestone that adds it", "check": "grep", "path": "AGENTS.md", "pattern": "(?is)## Commands.*?`[^`\\n]*\\bcheck\\b[^`\\n]*`"}
```

Append to scenario 2 (`first-session`) `assertions`:
```json
{"text": "The claimed plan carries a Done when section", "check": "grep_any", "glob": "docs/plans/M0/M0-01-*.md", "pattern": "(?m)^## Done when"},
{"text": "The final message opens with what the human must decide", "check": "final_contains", "pattern": "(?is)\\A\\W{0,10}(#+\\s*)?\\**needs from you"}
```

Append a new scenario:
```json
{
  "id": 7,
  "name": "ci-default",
  "fixture": "generated",
  "setup": {"git": false, "copy_linter": true},
  "prompt": "The bootstrap of this project is complete and reviewed. Before M0 starts, the owner asks for the project's CI and its local check command, following the kit's defaults for this profile. Write them, record the command in AGENTS.md, and stop. Write no implementation code.",
  "expected_output": "One workflow file with a fast job on pull requests (lint, typecheck, fast tests, docs linter) and a slow job gated to main or a schedule; a path filter so docs-only changes run only the docs linter; no deploy or publish step; a local check command that runs what the fast job runs, named in AGENTS.md; the project still lints clean; the final message opens with Needs from you.",
  "assertions": [
    {"text": "Exactly one CI workflow file", "check": "count_glob", "glob": ".github/workflows/*.y*ml", "min": 1, "max": 1},
    {"text": "The fast job runs on pull requests", "check": "grep_any", "glob": ".github/workflows/*", "pattern": "pull_request"},
    {"text": "The slow job is gated to main or a schedule", "check": "grep_any", "glob": ".github/workflows/*", "pattern": "(?s)(schedule:|refs/heads/main|github\\.ref\\s*==\\s*'refs/heads/main'|branches:\\s*\\[?\\s*-?\\s*['\"]?main)"},
    {"text": "A path filter keeps docs-only changes off the test jobs", "check": "grep_any", "glob": ".github/workflows/*", "pattern": "(paths-ignore:|paths:|paths-filter)"},
    {"text": "No deploy or publish step before the milestone that ships", "check": "none_grep", "glob": ".github/workflows/*", "pattern": "(?im)^\\s*-?\\s*(name|uses|run):.*(deploy|pypi|twine|gh-pages|publish)"},
    {"text": "AGENTS.md names a concrete check command, more than the bare word", "check": "grep", "path": "AGENTS.md", "pattern": "(?is)## Commands.*?`(?=[^`\\n]*\\s)(?=[^`\\n]*\\bcheck\\b)[^`\\n]+`"},
    {"text": "The project lints with zero errors", "check": "lint", "max_errors": 0}
  ]
}
```

Run: `python -c "import json; d=json.load(open('evals/evals.json', encoding='utf-8')); print(len(d['evals']), sum(len(e['assertions']) for e in d['evals']))"`
Expected: `7 69`

- [ ] **Step 3: `evals/README.md`** — change "the six scenarios" to "the seven scenarios" in the Layout bullet and the `## The six scenarios` heading to `## The seven scenarios`, and add the table row:
```
| `ci-default` | CI written in feature work | one workflow, a fast job on PRs and a slow one on main or a schedule, a path filter, no deploy step, a local `check` command in AGENTS.md |
```
(`## The six scenarios` is not cited by number anywhere; confirm with `grep -rn "six scenarios" --include=*.md .` and update any other hit.)

- [ ] **Step 4: Harness smoke test and commit**

Run: `python evals/harness.py prepare ci-default evals/runs --label smoke` → a prepared run directory under `evals/runs/ci-default/smoke/` (runs/ is gitignored). Then `python evals/harness.py grade ci-default evals/runs --label smoke` → grades without a crash (assertions fail, since no agent ran — that is expected).
Run: `python -m pytest tests -q` → pass. Lint → `0 error(s), 0 warning(s)`.
```bash
git add evals
git commit -m "Evals: generated fixture at 2.9.0, five assertions in generation and first-session, new ci-default scenario (69 assertions)"
```

---

### Task 9: Run the evals and record results

**Files:**
- Create: `evals/release-h-2026-09-25.md`

- [ ] **Step 1: Prepare all scenarios** — `python evals/harness.py prepare all evals/runs --label release-h`.

- [ ] **Step 2: Run each scenario** — for each `evals/runs/<scenario>/release-h/prompt.md`, dispatch one fresh subagent with the prompt, working inside that run's `project/`, writing `project/final_message.md` before it stops. Seven independent runs; dispatch them in parallel. Save `timing.json` from each agent's reported usage.

- [ ] **Step 3: Grade** — `python evals/harness.py grade all evals/runs --label release-h` then `python evals/harness.py report evals/runs`. Target: 69/69. Any failure: read the run's output, decide whether the skill text or the assertion is wrong, fix the one that is, re-run that scenario only.

- [ ] **Step 4: Real-repository run** — `python evals/harness.py seed list`, then `seed prepare` the seed used in releases F and G, and run the full bootstrap with one fresh agent as in `evals/release-g-2026-09-22.md`. Score fine/stretched/violated against the same principle rows; target 23/1/0 or better. Check the generated `AGENTS.md` has `## Stopping rules` and a `check` line, and `docs/WORKFLOW.md` has §3a and §5b.

- [ ] **Step 5: Write `evals/release-h-2026-09-25.md`** in the shape of `evals/release-g-2026-09-22.md`: what changed, scenario table with per-scenario pass counts, tokens and time, the real-repo score, gaps found (as candidates for the next release), and "where this leaves the kit". No client or seed content quoted beyond the scores and gap descriptions.

- [ ] **Step 6: Final gate and commit**

Run: `python -m pytest tests -q` → pass. Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.
```bash
git add evals/release-h-2026-09-25.md
git commit -m "Evals: release H results"
```

- [ ] **Step 7: Hand back** — push the branch and open a PR only if the user asks; report results with Needs from you first.

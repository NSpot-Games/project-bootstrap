# idea-to-design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a second skill, `skills/idea-to-design/`, that turns a raw idea into a design in `<project>/docs/vision/`, with evals measured against a no-skill baseline, released as kit v2.11.0.

**Architecture:** The skill is Markdown only: `SKILL.md` (nine steps), two references, three templates. The package tests are generalised from one skill to every directory under `skills/`. The eval harness learns a per-scenario skill, a no-skill baseline mode and one new check; six scenarios on four invented fixtures measure the skill. The baseline runs before `SKILL.md` exists.

**Tech Stack:** Markdown; Python 3.11+ standard library (`evals/harness.py`); pytest.

**Spec:** `docs/superpowers/specs/2026-10-13-idea-to-design-design.md`

## Global Constraints

- Version `2.11.0` in `skills/project-bootstrap/SKILL.md`, `skills/idea-to-design/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and `AGENTS.md`; all bumped together.
- Inside a skill, kit paths are relative to that skill's root (`references/questions.md`); at the repo root they are full (`skills/idea-to-design/references/questions.md`); project paths are written `<project>/...`.
- No double-brace placeholders outside `skills/project-bootstrap/assets/templates/`; elsewhere an unfixed name is `<angle-bracketed>`.
- Every eval fixture is invented; no content from a real project (`evals/README.md`).
- `python -m pytest tests -q` passes and `python skills/project-bootstrap/scripts/check_docs.py --root .` reports 0 errors, 0 warnings at the end of every task.
- `SKILL.md` under 500 lines; `description` 1–1024 characters; `name` matches its folder.
- Work happens on branch `design/idea-to-design` (it already holds the spec commit). Nothing is pushed and no PR is opened without the owner's yes.
- The skill is written test-first under superpowers:writing-skills: baseline without the skill (Task 4), the skill written against the observed failures (Task 5), loopholes closed on re-runs (Task 7). Its `description` states only when to use the skill, starting "Use when…", and never summarizes the procedure.

## Review Focus

1. **A second skill silently skipped by the package tests** — a typo'd reference path in `skills/idea-to-design/SKILL.md` must fail `tests/test_skill_package.py`; Task 1 proves the generalised test fails on a broken copy.
2. **Existing project-bootstrap evals changing behaviour through the harness edit** — `prepare` with no `--skill` must still produce the same project-bootstrap prompt; Task 2 pins the default prompt's skill path and wording.
3. **The linter breaking on the new skill's files** — citation roots and template exclusions for `skills/idea-to-design/` must be configured, or every `references/...` citation in its `SKILL.md` becomes E001; Task 5 runs `check_docs.py --root .` after adding the files.
4. **An agent with the skill writing code or choosing a stack during design** — the `tech-drift` and `raw-idea` scenarios assert no stack words in the design files or the first message.
5. **A consistency pass that invents problems in a clean design** — the `handoff` scenario asserts no area file changes on the consistent fixture.

---

### Task 1: Generalise the package tests to every skill

**Files:**
- Modify: `tests/test_skill_package.py:1-93`

**Interfaces:**
- Produces: `SKILLS: list[Path]` (every directory under `skills/` holding a `SKILL.md`); `frontmatter(skill_md: Path) -> dict[str, str]`; `missing_skill_paths(skill_dir: Path) -> list[str]`. Tests parametrised over `SKILLS` with `ids=[d.name for d in SKILLS]`.

- [ ] **Step 1: Write the failing test for the helper**

Add after `_text` in `tests/test_skill_package.py`:

```python
def test_missing_skill_paths_finds_a_broken_reference(tmp_path):
    broken = tmp_path / "broken-skill"
    (broken / "references").mkdir(parents=True)
    (broken / "references" / "real.md").write_text("# Real\n", encoding="utf-8")
    (broken / "SKILL.md").write_text(
        "---\nname: broken-skill\ndescription: x\n---\n\nSee `references/real.md` and `references/gone.md §2`.\n",
        encoding="utf-8",
    )
    assert missing_skill_paths(broken) == ["references/gone.md"]
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_skill_package.py::test_missing_skill_paths_finds_a_broken_reference -q`
Expected: FAIL with `NameError: name 'missing_skill_paths' is not defined`

- [ ] **Step 3: Generalise the module**

Replace lines 1–93 of `tests/test_skill_package.py` (the docstring through `test_plugin_and_marketplace_name_the_skill`) with:

```python
"""Checks that every skill under skills/ is a valid, self-contained Agent Skill and that the
Claude plugin manifests agree with them."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(d for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").is_file())
SKILL_DIR = ROOT / "skills" / "project-bootstrap"
SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
HOOKS = ROOT / "hooks" / "hooks.json"
STOP_SH = ROOT / "hooks" / "stop.sh"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Backticked skill-relative paths: `references/...`, `assets/...`, `scripts/...`, with an
# optional ` §N.M` anchor before the closing backtick.
SKILL_PATH_RE = re.compile(r"`((?:references|assets|scripts)/[A-Za-z0-9_./<>-]*)(?:\s*§[\d.a-z]+)?`")

skill_param = pytest.mark.parametrize("skill_dir", SKILLS, ids=[d.name for d in SKILLS])


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def frontmatter(skill_md: Path = SKILL_MD) -> dict[str, str]:
    text = _text(skill_md)
    assert text.startswith("---\n"), f"{skill_md} must start with YAML frontmatter"
    block = text.split("---\n", 2)[1]
    out: dict[str, str] = {}
    parent = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and parent:
            k, v = line.strip().split(":", 1)
            out[f"{parent}.{k.strip()}"] = v.strip().strip('"')
        else:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v:
                out[k] = v.strip('"')
                parent = None
            else:
                parent = k
    return out


def missing_skill_paths(skill_dir: Path) -> list[str]:
    """Backticked skill-relative paths in SKILL.md that do not exist inside the skill."""
    missing = []
    for m in SKILL_PATH_RE.finditer(_text(skill_dir / "SKILL.md")):
        p = m.group(1)
        if "<" in p:
            continue  # generic name such as references/profiles/<name>.md
        if not (skill_dir / p.rstrip("/")).exists():
            missing.append(p)
    return missing


def test_missing_skill_paths_finds_a_broken_reference(tmp_path):
    broken = tmp_path / "broken-skill"
    (broken / "references").mkdir(parents=True)
    (broken / "references" / "real.md").write_text("# Real\n", encoding="utf-8")
    (broken / "SKILL.md").write_text(
        "---\nname: broken-skill\ndescription: x\n---\n\nSee `references/real.md` and `references/gone.md §2`.\n",
        encoding="utf-8",
    )
    assert missing_skill_paths(broken) == ["references/gone.md"]


def test_skills_directory_holds_project_bootstrap():
    assert SKILL_DIR in SKILLS


@skill_param
def test_name_matches_directory_and_spec_rules(skill_dir):
    fm = frontmatter(skill_dir / "SKILL.md")
    assert fm["name"] == skill_dir.name
    assert 1 <= len(fm["name"]) <= 64
    assert NAME_RE.match(fm["name"])


@skill_param
def test_description_is_present_and_bounded(skill_dir):
    fm = frontmatter(skill_dir / "SKILL.md")
    assert 1 <= len(fm["description"]) <= 1024


@skill_param
def test_skill_md_is_under_500_lines(skill_dir):
    assert len(_text(skill_dir / "SKILL.md").splitlines()) < 500


@skill_param
def test_every_skill_relative_path_in_skill_md_exists(skill_dir):
    assert missing_skill_paths(skill_dir) == []


@skill_param
def test_version_agrees_across_skill_and_manifests(skill_dir):
    fm = frontmatter(skill_dir / "SKILL.md")
    plugin = json.loads(_text(PLUGIN))
    market = json.loads(_text(MARKETPLACE))
    assert fm["metadata.version"] == plugin["version"] == market["plugins"][0]["version"]


@skill_param
def test_skill_paths_resolve_when_copied_alone(skill_dir, tmp_path):
    copy = tmp_path / skill_dir.name
    shutil.copytree(skill_dir, copy, ignore=shutil.ignore_patterns("__pycache__"))
    assert missing_skill_paths(copy) == []


def test_plugin_and_marketplace_name_the_skill():
    plugin = json.loads(_text(PLUGIN))
    market = json.loads(_text(MARKETPLACE))
    assert plugin["name"] == "project-bootstrap"
    assert market["plugins"][0]["name"] == "project-bootstrap"
    assert market["plugins"][0]["source"] == "./"
```

Everything from `def test_hooks_json_registers_the_stop_script` to the end of the file stays as it is: it is about project-bootstrap's hooks and linter, and uses `SKILL_DIR` / `SKILL_MD`, which still exist.

- [ ] **Step 4: Run the whole file**

Run: `python -m pytest tests/test_skill_package.py -q`
Expected: PASS (one skill today; every parametrised test runs once, id `project-bootstrap`).

- [ ] **Step 5: Prove the generalised check catches a broken second skill**

Run:
```bash
mkdir -p skills/zz-broken && printf -- '---\nname: zz-broken\ndescription: x\nmetadata:\n  version: "2.10.1"\n---\n\nSee `references/gone.md`.\n' > skills/zz-broken/SKILL.md
python -m pytest tests/test_skill_package.py -q -k zz-broken
rm -rf skills/zz-broken
```
Expected: `test_every_skill_relative_path_in_skill_md_exists[zz-broken]` and `test_skill_paths_resolve_when_copied_alone[zz-broken]` FAIL listing `references/gone.md`; then the directory is removed. Run `git status --short skills/` and confirm it prints nothing.

- [ ] **Step 6: Full suite and lint**

Run: `python -m pytest tests -q` → all pass. Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

- [ ] **Step 7: Commit**

```bash
git add tests/test_skill_package.py
git commit -m "Tests: package checks run over every skill under skills/

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Harness — per-scenario skill, no-skill baselines, `final_count`

**Files:**
- Modify: `evals/harness.py` (docstring, constants at 32 and 38–53, `prepare` at 113–147, `check` at 179–267, `main` at 426 and 450)
- Create: `tests/test_harness.py`

**Interfaces:**
- Produces: `prepare(name: str, runs: Path, label: str, skill: Path | None = None, no_skill: bool = False) -> Path`; `skill_for(ev: dict) -> Path`; check kind `final_count` with keys `pattern`, optional `min` (default 0), optional `max` (default unbounded); CLI `prepare ... [--skill PATH] [--no-skill]`.
- Consumes: scenarios may carry `"skill": "<name>"`; absent means `project-bootstrap`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_harness.py`:

```python
"""The eval harness: which skill a scenario's prompt names, the no-skill baseline prompt, and
the final_count check."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import harness  # noqa: E402


@pytest.fixture
def evals(tmp_path, monkeypatch):
    fixtures = tmp_path / "fixtures"
    (fixtures / "tiny").mkdir(parents=True)
    (fixtures / "tiny" / "README.md").write_text("# tiny\n", encoding="utf-8")
    data = {
        "skill_name": "project-bootstrap", "answers": "A", "brainstorm": "B",
        "evals": [
            {"id": 1, "name": "plain", "fixture": "tiny", "prompt": "Do it. {answers}", "assertions": []},
            {"id": 2, "name": "ideas", "skill": "idea-to-design", "fixture": "tiny", "prompt": "Design it.", "assertions": []},
        ],
    }
    path = tmp_path / "evals.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(harness, "EVALS", path)
    monkeypatch.setattr(harness, "FIXTURES", fixtures)
    return tmp_path / "runs"


def _prompt(rd: Path) -> str:
    return (rd / "prompt.md").read_text(encoding="utf-8")


def test_default_scenario_prompt_names_project_bootstrap(evals):
    p = _prompt(harness.prepare("plain", evals, "t"))
    assert "exercising the project-bootstrap skill" in p
    assert "skills/project-bootstrap/SKILL.md" in p
    assert "Do it. A" in p


def test_scenario_skill_key_picks_the_skill(evals):
    p = _prompt(harness.prepare("ideas", evals, "t"))
    assert "exercising the idea-to-design skill" in p
    assert "skills/idea-to-design/SKILL.md" in p


def test_explicit_skill_path_wins(evals, tmp_path):
    snap = tmp_path / "snapshot" / "project-bootstrap"
    p = _prompt(harness.prepare("plain", evals, "t", snap))
    assert snap.resolve().as_posix() + "/SKILL.md" in p


def test_no_skill_prompt_names_no_skill(evals):
    rd = harness.prepare("ideas", evals, "baseline", no_skill=True)
    p = _prompt(rd)
    assert "SKILL.md" not in p and "exercising" not in p
    assert "Design it." in p
    assert json.loads((rd / "eval_metadata.json").read_text(encoding="utf-8"))["skill"] is None


@pytest.mark.parametrize("text,a,expected", [
    ("Which one?\n", {"pattern": r"(?m)\?\s*$", "min": 1, "max": 1}, True),
    ("Which one?\nAnd this?\n", {"pattern": r"(?m)\?\s*$", "max": 1}, False),
    ("No question.\n", {"pattern": r"(?m)\?\s*$", "min": 1}, False),
    ("- a\n- b\n", {"pattern": r"(?m)^- ", "min": 2}, True),
])
def test_final_count(tmp_path, text, a, expected):
    (tmp_path / "final_message.md").write_text(text, encoding="utf-8")
    ok, evidence = harness.check({"check": "final_count", **a}, tmp_path / "project", tmp_path, {})
    assert ok is expected, evidence
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest tests/test_harness.py -q`
Expected: FAIL — `prepare()` missing argument `skill` / unknown `no_skill` keyword; `final_count` returns `unknown check`.

- [ ] **Step 3: Implement**

In `evals/harness.py`:

Docstring first line becomes `"""Behavioural evals for the kit's skills: one step per scenario, run by`, and its usage line for prepare becomes
`    python evals/harness.py prepare <scenario|all> <runs_dir> [--label with_skill] [--skill PATH | --no-skill]`.

Replace line 32 (`DEFAULT_SKILL = ...`) with:

```python
SKILLS_DIR = ROOT / "skills"
DEFAULT_SKILL = SKILLS_DIR / "project-bootstrap"
```

Replace `PROMPT = """...` (lines 38–53) with:

```python
SKILL_LINES = """You are exercising the {skill_name} skill exactly as an agent would use it.

Skill: read `{skill}/SKILL.md` first and follow it. Its references, templates and scripts live
under `{skill}/`. Never modify anything under `{skill}`.

"""

PROMPT = """{skill_lines}Project: `{project}`. Work only inside this directory; it is a scratch copy and nothing
outside it matters. Paths written as `<project>/...` mean this directory.

Task: {task}

The user is not available. Every answer they would give is stated above. If the work
requires a human reply that is not given above, stop at that point. Before you finish, write
`{project}/final_message.md` containing exactly the message you would post to the user at the
point you stopped, and nothing else. Then reply with a short report: which steps you
followed, which files you wrote, and where you stopped and why.
"""
```

Add above `prepare`:

```python
def skill_for(ev: dict) -> Path:
    """The skill a scenario exercises: its "skill" key, or project-bootstrap."""
    return SKILLS_DIR / ev.get("skill", "project-bootstrap")
```

In `prepare`, change the signature to `def prepare(name: str, runs: Path, label: str, skill: Path | None = None, no_skill: bool = False) -> Path:` and replace the two lines that build `prompt` (line 141) and the `"skill": skill.resolve().as_posix()` entry (line 144) so the end of the function reads:

```python
    data = load_evals()
    task = ev["prompt"].format(answers=data["answers"], brainstorm=data["brainstorm"])
    skill = None if no_skill else (skill or skill_for(ev))
    skill_lines = "" if skill is None else SKILL_LINES.format(
        skill_name=ev.get("skill", "project-bootstrap"), skill=skill.resolve().as_posix())
    prompt = PROMPT.format(skill_lines=skill_lines, project=project.resolve().as_posix(), task=task)
    (rd / "prompt.md").write_text(prompt, encoding="utf-8", newline="\n")
    (rd / "eval_metadata.json").write_text(json.dumps({
        "eval_id": ev["id"], "eval_name": name, "label": label,
        "skill": None if skill is None else skill.resolve().as_posix(),
        "prompt": task, "assertions": [a["text"] for a in ev["assertions"]],
    }, indent=2), encoding="utf-8", newline="\n")
    return rd
```

In `check`, insert before `return False, f"unknown check {kind!r}"`:

```python
    if kind == "final_count":
        p = rd / "final_message.md"
        if not p.is_file():
            return False, "final_message.md missing"
        n = len(re.findall(a["pattern"], _read(p)))
        ok = a.get("min", 0) <= n <= a.get("max", 10**9)
        return ok, f"{n} match(es)"
```

In `main`, replace the `prepare` parser line (426) with:

```python
    p = sub.add_parser("prepare"); p.add_argument("scenario"); p.add_argument("runs"); p.add_argument("--label", default="with_skill")
    p.add_argument("--skill", default=None, help="skill directory; default: the scenario's skill under skills/")
    p.add_argument("--no-skill", action="store_true", help="a prompt with no skill at all, for baselines")
```

and the call at line 450 with `rd = prepare(n, Path(args.runs), args.label, Path(args.skill) if args.skill else None, args.no_skill)`.

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_harness.py tests/test_sync_tracker.py -q`
Expected: PASS (`test_harness_prepares_tracker_scenarios` still passes an explicit skill path).

- [ ] **Step 5: Document the check and the flag in `evals/README.md`**

In "Running" step 1, replace the second command with:

```
   python evals/harness.py prepare all evals/runs --label baseline --skill <path to a snapshot of the old skill>
   python evals/harness.py prepare <scenario> evals/runs --label baseline --no-skill
   ```

and add after the code block: "A scenario names the skill it exercises with an optional `"skill"` key (default `project-bootstrap`); `--no-skill` writes a prompt with no skill at all, the baseline for a new skill." In "Adding a scenario", add `final_count` to the list of checks, after `final_not_contains`.

- [ ] **Step 6: Full suite and lint**

Run: `python -m pytest tests -q` → all pass. Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

- [ ] **Step 7: Commit**

```bash
git add evals/harness.py evals/README.md tests/test_harness.py
git commit -m "Evals harness: a scenario names its skill; --no-skill baselines; final_count check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The four fixtures and six scenarios

**Files:**
- Create: `evals/fixtures/idea-only/README.md`
- Create: `evals/fixtures/vision-in-progress/README.md`, `.../docs/vision/README.md`, `.../docs/vision/lending.md`, `.../docs/vision/alternatives.md`
- Create: `evals/fixtures/vision-flawed/README.md`, `.../docs/vision/README.md`, `.../docs/vision/lending.md`, `.../docs/vision/trust.md`, `.../docs/vision/pricing.md`, `.../docs/vision/alternatives.md`
- Create: `evals/fixtures/vision-clean/` — the same six files as `vision-flawed`, with the three contradictions fixed
- Modify: `evals/evals.json` (append ids 10–15), `evals/README.md` (scenario table and fixture list)
- Test: `tests/test_harness.py`

**Interfaces:**
- Consumes: `final_count`, `"skill"` key, `prepare(..., no_skill=True)` from Task 2.
- Produces: scenario names `raw-idea`, `tech-drift`, `against-recommendation`, `nothing-new`, `consistency`, `handoff`, each with `"skill": "idea-to-design"`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_harness.py`:

```python
IDEA_SCENARIOS = ["raw-idea", "tech-drift", "against-recommendation", "nothing-new", "consistency", "handoff"]
KNOWN_CHECKS = {"file_exists", "files_exist", "file_absent", "grep", "not_grep", "grep_any", "none_grep",
                "mentions_each", "unchanged", "count_glob", "no_tokens", "lint", "git_branch_prefix",
                "git_commits_min", "git_clean", "sha_recorded", "final_contains", "final_not_contains",
                "final_count"}


def test_every_scenario_has_a_fixture_and_known_checks():
    for ev in harness.load_evals()["evals"]:
        assert (harness.FIXTURES / ev["fixture"]).is_dir(), ev["name"]
        assert {a["check"] for a in ev["assertions"]} <= KNOWN_CHECKS, ev["name"]


def test_idea_to_design_scenarios_exist_and_prepare(tmp_path):
    names = {e["name"]: e for e in harness.load_evals()["evals"]}
    for n in IDEA_SCENARIOS:
        assert names[n].get("skill") == "idea-to-design", n
        rd = harness.prepare(n, tmp_path, "baseline", no_skill=True)
        assert (rd / "project").is_dir()


def test_flawed_and_clean_fixtures_differ_only_where_planted():
    flawed = harness.FIXTURES / "vision-flawed" / "docs" / "vision"
    clean = harness.FIXTURES / "vision-clean" / "docs" / "vision"
    assert sorted(p.name for p in flawed.iterdir()) == sorted(p.name for p in clean.iterdir())
    differ = sorted(p.name for p in flawed.iterdir() if p.read_text(encoding="utf-8") != (clean / p.name).read_text(encoding="utf-8"))
    assert differ == ["README.md", "trust.md"]
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_harness.py -q -k "scenario or fixtures"`
Expected: FAIL — `KeyError: 'raw-idea'` and missing fixture directories.

- [ ] **Step 3: Create `idea-only`**

`evals/fixtures/idea-only/README.md`:

```markdown
# new-idea

Nothing here yet.
```

- [ ] **Step 4: Create `vision-in-progress`**

`evals/fixtures/vision-in-progress/README.md`:

```markdown
# tidepool

Nothing here yet beyond the design in `docs/vision/`.
```

`evals/fixtures/vision-in-progress/docs/vision/README.md`:

```markdown
# Tidepool

## The hook

Neighbours already lend each other tools through group chats and noticeboard posts, and tool
libraries lend from a shed. Tidepool is new in one way: every lend is backed by a small deposit
the app holds, so lending to a stranger on your street is as safe as lending to a friend.

## Purpose

A free community app run by a non-profit and funded by grants. Success is the number of lends
per street per month.

## Pillars

1. Lending to a stranger feels as safe as lending to a friend.
2. Arranging a lend takes under a minute.
3. Nobody profits from a neighbour.

## Decided

| Area | Decision |
|---|---|
| [Lending](lending.md) | a lend is a request, an accept, a hand-over and a return, backed by a refundable deposit the app holds |

## Still to design

| Area | Status |
|---|---|
| Finding tools | open question |
| Trust and reputation | not started |
```

`evals/fixtures/vision-in-progress/docs/vision/lending.md`:

```markdown
# Lending

A lend is four steps, and the deposit makes the first lend between strangers safe.

## Rules

1. **Steps:** the borrower requests a tool for given days; the owner accepts; they meet to hand it
   over; the borrower returns it and the owner confirms.
2. **Deposit:** the borrower pays a refundable deposit when the owner accepts — 20% of the tool's
   stated value, at most £30. The app holds it and releases it when the owner confirms the
   return.
3. **Length:** a loan lasts up to 7 days.

## Still to design

- What happens when a tool comes back damaged.
```

`evals/fixtures/vision-in-progress/docs/vision/alternatives.md`:

```markdown
# Alternatives

Every design question, the option chosen, and the options not taken.

## 1. What is Tidepool for?

**Chosen: A — a free community app run by a non-profit**, funded by grants.

| Option | Notes |
|---|---|
| B — A commercial marketplace taking a fee per lend | Self-funding; breaks "nobody profits from a neighbour". |
| C — A feature inside an existing neighbourhood app | Instant audience; no control over trust or deposits. |

## Possible additions

None yet.
```

- [ ] **Step 5: Create `vision-clean`**

`evals/fixtures/vision-clean/README.md` — identical to `vision-in-progress/README.md`.

`evals/fixtures/vision-clean/docs/vision/README.md`:

```markdown
# Tidepool

## The hook

Neighbours already lend each other tools through group chats and noticeboard posts, and tool
libraries lend from a shed. Tidepool is new in one way: every lend is backed by a small deposit
the app holds, so lending to a stranger on your street is as safe as lending to a friend.

## Purpose

A free-to-borrow community app run by a non-profit, funded by grants and a small membership.
Success is the number of lends per street per month.

## Pillars

1. Lending to a stranger feels as safe as lending to a friend.
2. Arranging a lend takes under a minute.
3. Nobody profits from a neighbour.

## Decided

| Area | Decision |
|---|---|
| [Lending](lending.md) | request, accept, hand-over, return; a refundable deposit the app holds; at most 2 tools at once; loans up to 7 days |
| [Trust](trust.md) | a trust score from on-time returns; new members start with a 2-tool starter bundle |
| [Pricing](pricing.md) | membership £2 a month; borrowing and lending are free |

## Still to design

| Area | Status |
|---|---|
| Damaged tools | rules to design |
| Finding tools | the map's layout to design |
```

`evals/fixtures/vision-clean/docs/vision/lending.md`:

```markdown
# Lending

A lend is four steps, and the deposit makes the first lend between strangers safe.

## Rules

1. **Steps:** the borrower requests a tool for given days; the owner accepts; they meet to hand it
   over; the borrower returns it and the owner confirms.
2. **Deposit:** the borrower pays a refundable deposit when the owner accepts — 20% of the tool's
   stated value, at most £30. The app holds it and releases it when the owner confirms the
   return.
3. **Length:** a loan lasts up to 7 days.
4. **Limit:** a member can hold at most 2 tools at once.

## Still to design

- What happens when a tool comes back damaged.
```

`evals/fixtures/vision-clean/docs/vision/trust.md`:

```markdown
# Trust

Trust grows from returning things on time, so strangers can judge each other at a glance.

## Rules

1. **Trust score:** every on-time return adds 1; a late return subtracts 3. The score shows on the
   member's profile.
2. **Late:** a loan still open after its 7 days counts as late.
3. **Starter bundle:** a new member's first lend can be the starter bundle — 2 tools borrowed
   together, chosen from the tools nearby.

## Still to design

- Whether a very low score blocks borrowing.
```

`evals/fixtures/vision-clean/docs/vision/pricing.md`:

```markdown
# Pricing

The non-profit covers its costs without anyone profiting from a lend.

## Rules

1. **Membership:** £2 a month, paid by anyone who wants to borrow; lending is open to everyone.
2. **Lends are free:** no fee per lend; deposits are refunded in full on return.

## Still to design

- A hardship waiver for the membership.
```

`evals/fixtures/vision-clean/docs/vision/alternatives.md`:

```markdown
# Alternatives

Every design question, the option chosen, and the options not taken.

## 1. What is Tidepool for?

**Chosen: A — a free-to-borrow community app run by a non-profit**, funded by grants and a small
membership.

| Option | Notes |
|---|---|
| B — A commercial marketplace taking a fee per lend | Self-funding; breaks "nobody profits from a neighbour". |
| C — A feature inside an existing neighbourhood app | Instant audience; no control over trust or deposits. |

## 2. How do people find a tool to borrow?

**Chosen: A — a map of nearby tools.**

| Option | Notes |
|---|---|
| B — A searchable list | Faster for a known need; hides how close the tool is. |
| C — A request board | Finds tools nobody listed; slow, breaks "under a minute". |

## Possible additions

- Tool kits curated by the non-profit for common jobs (painting a room, clearing a garden).
```

- [ ] **Step 6: Create `vision-flawed`**

Copy `vision-clean` to `vision-flawed`, then plant the three contradictions:

```bash
cp -r evals/fixtures/vision-clean evals/fixtures/vision-flawed
```

In `evals/fixtures/vision-flawed/docs/vision/trust.md`, replace rule 2 and rule 3 with:

```markdown
2. **Late:** a loan open for more than 5 days counts as late.
3. **Starter bundle:** a new member's first lend can be the starter bundle — 3 tools borrowed
   together, chosen from the tools nearby.
```

In `evals/fixtures/vision-flawed/docs/vision/README.md`, replace the Trust and Pricing rows of the Decided table with:

```markdown
| [Trust](trust.md) | a trust score from on-time returns; new members start with a 3-tool starter bundle |
| [Pricing](pricing.md) | free for everyone |
```

The planted contradictions are: a 3-tool starter bundle against "at most 2 tools at once" (a rule that cannot happen); late after 5 days against loans of up to 7 days (a limit inside the normal case); "free for everyone" against a £2 membership (a stale summary).

- [ ] **Step 7: Add the six scenarios to `evals/evals.json`**

Append to the `evals` array (after id 9):

```json
    {
      "id": 10,
      "name": "raw-idea",
      "skill": "idea-to-design",
      "fixture": "idea-only",
      "setup": {"git": true},
      "prompt": "The user says: \"I have an idea: an app where neighbours lend each other tools — drills, ladders, lawnmowers. Help me turn it into something that could actually work.\" Respond as the first message of the conversation.",
      "expected_output": "The agent places the idea among existing products, names what is new, and asks one question — what the product is for — with options and a recommendation. No stack, no features yet.",
      "assertions": [
        {"text": "The message compares the idea with things that already exist", "check": "final_contains", "pattern": "(?i)(already exist|existing|apps? like|similar|services? like)"},
        {"text": "The message names what is new about the idea", "check": "final_contains", "pattern": "(?i)(what('s| is) new|the new (part|thing|angle)|hook|different from|sets? it apart|stand out)"},
        {"text": "The question is about purpose", "check": "final_contains", "pattern": "(?i)(what is it for|purpose|who is it for|the goal|commercial|non-?profit|side project|hobby)"},
        {"text": "Exactly one question is asked", "check": "final_count", "pattern": "(?m)\\?\\**\\s*$", "min": 1, "max": 1},
        {"text": "A recommendation is given", "check": "final_contains", "pattern": "(?i)recommend"},
        {"text": "No technology is chosen or discussed", "check": "final_not_contains", "pattern": "(?i)(react native|flutter|firebase|postgres|supabase|tech stack|database|backend)"}
      ]
    },
    {
      "id": 11,
      "name": "tech-drift",
      "skill": "idea-to-design",
      "fixture": "vision-in-progress",
      "setup": {"git": true},
      "prompt": "The design so far is in docs/vision/. Your last message asked: \"How do people find a tool to borrow? A) a map of nearby tools (recommended — it shows how close each tool is, which serves 'under a minute') B) a searchable list C) a request board.\" The user replies: \"Before that — which database should we use, Postgres or Firebase?\" Respond, and update the files as the design work requires.",
      "expected_output": "The agent answers the database question briefly, parks it in docs/vision/README.md under 'Parked for later', records no stack as design, and returns to the open question about finding tools.",
      "assertions": [
        {"text": "The database question is parked in the vision README", "check": "grep", "path": "docs/vision/README.md", "pattern": "(?is)parked for later.{0,800}(database|postgres|firebase)"},
        {"text": "No design area file records a database", "check": "none_grep", "glob": "docs/vision/*.md", "exclude": "docs/vision/README.md", "pattern": "(?i)(postgres|firebase)"},
        {"text": "The message returns to the open question about finding tools", "check": "final_contains", "pattern": "(?i)(map|searchable list|request board)"},
        {"text": "At most one question is asked", "check": "final_count", "pattern": "(?m)\\?\\**\\s*$", "max": 1}
      ]
    },
    {
      "id": 12,
      "name": "against-recommendation",
      "skill": "idea-to-design",
      "fixture": "vision-in-progress",
      "setup": {"git": true},
      "prompt": "The design so far is in docs/vision/. Your last message asked: \"How do people find a tool to borrow? A) a map of nearby tools (recommended — it shows how close each tool is, which serves 'under a minute') B) a searchable list C) a request board.\" The user replies: \"C.\" Respond, record the decision in the files as the procedure says, and commit.",
      "expected_output": "The agent accepts C without arguing, records it as chosen in alternatives.md with the map and the list as options not taken, commits, and moves to the next question.",
      "assertions": [
        {"text": "alternatives.md records the request board as chosen", "check": "grep", "path": "docs/vision/alternatives.md", "pattern": "(?i)chosen[^\\n]{0,80}request board"},
        {"text": "alternatives.md records the recommended map as not taken", "check": "grep", "path": "docs/vision/alternatives.md", "pattern": "(?is)chosen[^\\n]{0,80}request board.{0,1500}\\bmap\\b"},
        {"text": "The choice is accepted without counter-argument", "check": "final_not_contains", "pattern": "(?i)(are you sure|reconsider|i would still|i'd still|still recommend|second thoughts)"},
        {"text": "The decision is committed", "check": "git_commits_min", "n": 2}
      ]
    },
    {
      "id": 13,
      "name": "nothing-new",
      "skill": "idea-to-design",
      "fixture": "idea-only",
      "setup": {"git": true},
      "prompt": "The user says: \"I have an idea: an app where you post square photos with filters, follow your friends and like their photos.\" Respond as the first message of the conversation.",
      "expected_output": "The agent says plainly that this exists, names it, and offers at least two angles that would make it new.",
      "assertions": [
        {"text": "The existing product is named", "check": "final_contains", "pattern": "(?i)instagram"},
        {"text": "The message says plainly that it already exists", "check": "final_contains", "pattern": "(?i)(already exists|exists today|is essentially|that's instagram|is instagram|already built)"},
        {"text": "At least two angles are offered", "check": "final_count", "pattern": "(?m)^\\s*(?:[-*]|\\d+[.)]|\\*\\*[A-E][).])\\s+", "min": 2}
      ]
    },
    {
      "id": 14,
      "name": "consistency",
      "skill": "idea-to-design",
      "fixture": "vision-flawed",
      "setup": {"git": true},
      "prompt": "The design in docs/vision/ is finished; the user says: \"I think that's everything — do the final check.\" Run the consistency pass, fix what it finds in the files, commit, and report.",
      "expected_output": "All three planted contradictions are found, fixed in the files and reported: the 3-tool starter bundle against the 2-tool limit, late-after-5-days against 7-day loans, and the stale 'free for everyone' summary.",
      "assertions": [
        {"text": "The starter bundle against the tool limit is reported", "check": "final_contains", "pattern": "(?is)(starter|bundle).{0,300}(two|2|three|3)|(two|2|three|3).{0,300}(starter|bundle)"},
        {"text": "Late-after-5-days against 7-day loans is reported", "check": "final_contains", "pattern": "(?is)(late|overdue).{0,300}(5|five|7|seven)|(5|five|7|seven).{0,300}(late|overdue)"},
        {"text": "The stale pricing summary is reported", "check": "final_contains", "pattern": "(?i)(free for everyone|£2|membership)"},
        {"text": "The stale summary is fixed in the README", "check": "not_grep", "path": "docs/vision/README.md", "pattern": "(?i)free for everyone"},
        {"text": "The fixes are committed", "check": "git_commits_min", "n": 2}
      ]
    },
    {
      "id": 15,
      "name": "handoff",
      "skill": "idea-to-design",
      "fixture": "vision-clean",
      "setup": {"git": true},
      "prompt": "The design in docs/vision/ is finished; the user says: \"That's everything, I think. What now?\" Finish the procedure.",
      "expected_output": "The consistency pass finds nothing to change; the agent summarizes what is decided and what is still to design, and offers project-bootstrap as the next step. No code, no stack.",
      "assertions": [
        {"text": "The vision README still links every area file", "check": "grep", "path": "docs/vision/README.md", "pattern": "(?s)(?=.*\\(lending\\.md\\))(?=.*\\(trust\\.md\\))(?=.*\\(pricing\\.md\\))"},
        {"text": "alternatives.md exists", "check": "file_exists", "path": "docs/vision/alternatives.md"},
        {"text": "No area file is changed when nothing was wrong", "check": "unchanged", "glob": "docs/vision/[!R]*.md"},
        {"text": "What is still to design is named", "check": "final_contains", "pattern": "(?i)(still to design|left to design|damaged tools|open)"},
        {"text": "project-bootstrap is offered as the next step", "check": "final_contains", "pattern": "(?i)project-bootstrap"},
        {"text": "No code or stack is started", "check": "final_not_contains", "pattern": "(?i)(npm |pip install|scaffold|tech stack|postgres|firebase)"}
      ]
    }
```

(The `unchanged` glob `docs/vision/[!R]*.md` matches the area files and `alternatives.md` but not `README.md`, whose "Still to design" table may legitimately be touched. It excludes by first letter rather than by case because globbing is case-insensitive on Windows.)

- [ ] **Step 8: Update `evals/README.md`**

Change "the nine scenarios" (twice) to "the fifteen scenarios". Add to the fixture list in "Layout": "`idea-only` (a README), `vision-in-progress`, `vision-flawed` and `vision-clean` (Tidepool, an invented tool-lending app, at three points of an idea-to-design conversation; `vision-flawed` carries three planted contradictions)". Retitle "## The nine scenarios" to "## The fifteen scenarios" and append rows:

```markdown
| `raw-idea` | idea-to-design steps 1–3 | the idea placed among existing products, its hook named, one purpose question with a recommendation, no stack |
| `tech-drift` | idea-to-design step 7 | a technical question parked under "Parked for later", the conversation returned to design |
| `against-recommendation` | idea-to-design step 5 and conduct | a choice against the recommendation accepted without argument and recorded with the recommended option as not taken |
| `nothing-new` | idea-to-design step 1 | an idea that already exists named plainly, with angles offered |
| `consistency` | idea-to-design step 8 | three planted contradictions found, fixed and reported |
| `handoff` | idea-to-design steps 8–9 | a clean design left unchanged, a summary, project-bootstrap offered |
```

Add one sentence after the table: "The first nine exercise project-bootstrap; the last six exercise idea-to-design (`"skill": "idea-to-design"`), and their prompts give the user's turn of an ongoing conversation."

- [ ] **Step 9: Run tests and lint**

Run: `python -m pytest tests -q` → all pass. Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)` (fixtures are excluded by `docs/.check_docs.toml`).

- [ ] **Step 10: Commit**

```bash
git add evals/fixtures/idea-only evals/fixtures/vision-in-progress evals/fixtures/vision-flawed evals/fixtures/vision-clean evals/evals.json evals/README.md tests/test_harness.py
git commit -m "Evals: six idea-to-design scenarios on four invented Tidepool fixtures

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Baseline run, with no skill

**Files:**
- Create: `evals/baseline-idea-to-design-2026-10-13.md` (use the actual run date in the name)

**Interfaces:**
- Consumes: the six scenarios and `--no-skill` from Tasks 2–3.
- Produces: the list of failed assertions — the targets `SKILL.md` must turn green.

- [ ] **Step 1: Prepare**

Run, once per scenario name in `raw-idea tech-drift against-recommendation nothing-new consistency handoff`:

```bash
python evals/harness.py prepare <name> evals/runs --label baseline --no-skill
```

- [ ] **Step 2: Run each prompt with a fresh agent**

For each `evals/runs/<name>/baseline/prompt.md`, dispatch one fresh general-purpose subagent with the file's full content as its prompt, working only inside that run's `project/`. Record its token and time usage as `evals/runs/<name>/baseline/timing.json` (`{"total_tokens": N, "duration_ms": N}`). The six are independent: dispatch them in parallel.

- [ ] **Step 3: Grade**

```bash
python evals/harness.py grade raw-idea evals/runs --label baseline
python evals/harness.py grade tech-drift evals/runs --label baseline
python evals/harness.py grade against-recommendation evals/runs --label baseline
python evals/harness.py grade nothing-new evals/runs --label baseline
python evals/harness.py grade consistency evals/runs --label baseline
python evals/harness.py grade handoff evals/runs --label baseline
python evals/harness.py report evals/runs
```

- [ ] **Step 4: Record the baseline**

Write `evals/baseline-idea-to-design-<date>.md` in the shape of `evals/baseline-2026-09-21.md`: a first paragraph saying the runs used `--no-skill` before `skills/idea-to-design/` existed; a table `| Scenario | Pass | Assertions | Tokens | Seconds |` with a total row; then "## What failed" — a table `| Scenario | Failed assertion | What the agent did instead |`, one row per failure, the last column quoting or paraphrasing the agent's `final_message.md`. Read every `final_message.md` and add a "## Seen but not asserted" list of behaviours the skill should correct that no assertion catches (for example several questions at once, features proposed before purpose).

- [ ] **Step 5: Lint and commit**

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → 0/0.

```bash
git add evals/baseline-idea-to-design-*.md
git commit -m "Evals: idea-to-design baseline with no skill — the target assertions

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The skill

> **REQUIRED SUB-SKILL:** Use superpowers:writing-skills for this task. The text below is the draft; Step 8 reshapes it against the baseline as that skill directs.

**Files:**
- Create: `skills/idea-to-design/SKILL.md`
- Create: `skills/idea-to-design/references/questions.md`
- Create: `skills/idea-to-design/references/consistency-pass.md`
- Create: `skills/idea-to-design/assets/templates/vision-readme.md`, `alternatives.md`, `area.md`
- Modify: `docs/.check_docs.toml`
- Modify: `tests/test_kit_consistency.py` (append one test)

**Interfaces:**
- Consumes: the generalised package tests (Task 1) pick the new directory up automatically.
- Produces: the skill named `idea-to-design`, version `2.10.1` in this task (bumped with the rest in Task 6).

- [ ] **Step 1: Write the failing kit-consistency test**

Append to `tests/test_kit_consistency.py`:

```python
def test_idea_to_design_carries_no_double_brace_placeholders():
    skill = ROOT / "skills" / "idea-to-design"
    files = sorted(skill.rglob("*.md"))
    assert files, "skills/idea-to-design/ has no Markdown files"
    bad = [p.relative_to(ROOT).as_posix() for p in files if "{{" in p.read_text(encoding="utf-8")]
    assert bad == []
```

(`ROOT` is already defined at the top of that file; if it is not, add `ROOT = Path(__file__).resolve().parents[1]`.)

Run: `python -m pytest tests/test_kit_consistency.py -q -k double_brace` → FAIL ("has no Markdown files").

- [ ] **Step 2: Write `skills/idea-to-design/SKILL.md`**

```markdown
---
name: idea-to-design
description: Use when someone brings a raw idea for a product, game, tool or service — "I have an idea for…", "turn this idea into something that could work", "is this idea any good", "help me design this app" — and no design notes or code exist yet. Not for building, code changes, or a repository that already has design notes.
license: MIT
metadata:
  author: NSpotGames
  version: "2.10.1"
---

# Idea to design

Turns a raw idea into a design a project can be built from, as a conversation: find what is new
about the idea, settle what it is for, make every structural decision one question at a time,
write each decision down as it is made, and check the whole for contradictions before handing
off. The output is `<project>/docs/vision/`, which project-bootstrap reads as a docs-first
project. Follow the steps in order.

Every file this skill names lives inside its own directory: the question method in
`references/questions.md`, the final check in `references/consistency-pass.md`, the file shapes in
`assets/templates/`. Paths written `<project>/...` are in the project being designed.

## 1. Find the hook

Restate the idea in one sentence. Place it among what already exists: name the existing products
it resembles ("this mix already exists in A, B and C"). Then name the one thing that is new — the
hook. Every later decision protects it.

If nothing is new, say so plainly and name the product it already is. Offer two or three angles
that would make it new, as a list, and ask which one appeals. Do not design a copy.

Ask nothing else until the hook is stated.

## 2. Purpose first

Ask one question: what the product is for — commercial, internal tool, community, learning,
portfolio, or whatever fits. Give options with a recommendation. Ask it before any feature,
because it changes most later answers (how it earns, how big it is, what "done" means).

## 3. Structural decisions, top-down, one per message

Ask the decisions that shape the product, biggest first: its overall structure, its core loop or
core flow, then each subsystem, then details. One question per message, each built as
`references/questions.md` describes: 2–4 options that genuinely differ, each with what it gains,
what it costs and a real product as a reference point; the recommendation first, with its reason.

A question too small to matter gets no message: pick the conventional default, say so in one line
inside the next question, and move on.

## 4. Pillars

Once the shape is visible — usually after the purpose and two or three structural decisions —
propose 3–5 pillars: short rules every later decision is checked against ("every match is a
decision", "nobody profits from a neighbour"). Write them into `<project>/docs/vision/README.md`.
From then on, an option that breaks a pillar says which; a recommendation never breaks one
silently.

## 5. Write as you go

Each decision is written the moment it is agreed, never batched for the end:

- The area it belongs to gets its own `<project>/docs/vision/<area>.md` (shape:
  `assets/templates/area.md`), created on its first decision and extended after.
- `<project>/docs/vision/alternatives.md` (shape: `assets/templates/alternatives.md`) gets the
  question, the option chosen, and every option not taken with a note on where it might fit later.
  An idea left out on purpose goes under "Possible additions".
- `<project>/docs/vision/README.md` (shape: `assets/templates/vision-readme.md`) keeps the hook,
  purpose, pillars, the decided table and the still-to-design table current.
- Commit after each agreed area, with a message naming the decision.

If the project has no repository yet, offer to create one before the first write. Never push,
and never create a remote, without the person's yes.

## 6. Rules apart from content and numbers

Agree the rules of each area first: how it works. Lists of content (the items, the enemies, the
screens) and numbers (prices, amounts, timings) go into the area file's "Still to design" and do
not block the next decision. A starting number may be proposed as a starting value, marked as one.

## 7. Technology waits

Make no engine, stack, language or architecture decision until the design is agreed. When the
person raises a technical question mid-design, answer it briefly, add it to "Parked for later" in
`<project>/docs/vision/README.md`, and return to the open design question in the same message.
A hard technical limit that shapes the design — a platform's rules, a regulation, a device's
screen — is recorded as a constraint in the area it shapes, not decided as design.

## 8. Consistency pass

When the person says the design is complete, or every structural area is decided, read every file
in `<project>/docs/vision/` together and run `references/consistency-pass.md`. Fix each finding
in the files, commit, and report each fix in a short list so the person can check it. If nothing
is wrong, change nothing and say so.

## 9. Hand off

Summarize in a few lines what is decided and what is still to design, linking
`<project>/docs/vision/README.md`. Offer the next step: project-bootstrap, which reads
`<project>/docs/vision/` as the thinking a docs-first project starts from, or a first prototype
to test the riskiest part. Start neither without a yes.

## Conduct

- Plain language. A term the person may not know is explained the first time it appears.
- One question per message, always with a recommendation and its reason.
- A change of direction from the person is taken at once, without arguing back.
- A choice against the recommendation is accepted; the recommended option is recorded in
  `alternatives.md` as not taken, like any other.
- The person's words decide; the skill's recommendations only advise.
```

- [ ] **Step 3: Write `skills/idea-to-design/references/questions.md`**

```markdown
# Building a question

How to ask one design decision so the person can answer it in a word and the answer holds.

## 1. One decision

A question settles one decision. If answering it needs another decision first, ask that one first.
If two decisions are independent and both small, settle the smaller by default and ask the larger.

## 2. Options that genuinely differ

Offer 2–4 options. Each must lead somewhere different — a different product, not a different
setting of the same one. Two options that differ only in degree are one option with a number,
and the number belongs in "Still to design".

## 3. Each option: gain, cost, reference

For each option say, in a sentence or two:

- what it gains;
- what it costs or risks;
- a real product that works this way, when one exists ("the model behind Archero's chapters").

A reference product makes an abstract option concrete in one word. Name products the person is
likely to know.

## 4. The recommendation first

List the recommended option first and mark it "(my recommendation)". Give the reason in one
sentence, tied to the purpose, the hook or a pillar. Never recommend without a reason; never
leave the person without a recommendation.

## 5. Check against the pillars

Once pillars exist, check every option against them. An option that breaks a pillar says which,
in its cost. A recommendation never breaks a pillar.

## 6. Order: structure, then flow, then parts, then details

Ask the decisions that constrain the most first: the overall structure (what a session, a
customer journey, a run is), then the core loop or flow, then each subsystem, then details inside
a subsystem. A detail asked before its structure gets re-asked later.

## 7. Too small to ask

A decision whose options a reasonable person would not argue over — a conventional default
exists and nothing depends on it — is not asked. State the default in one line inside the next
question ("I've assumed portrait orientation") so the person can object.

## 8. After the answer

Record the decision (`SKILL.md` §5) before asking the next question. If the person picked an
option other than the recommendation, accept it in one line and move on.
```

- [ ] **Step 4: Write `skills/idea-to-design/references/consistency-pass.md`**

```markdown
# Consistency pass

The final read of the whole design. Read every file in `<project>/docs/vision/` together, then
look for each kind of problem below. Fix each finding in the files, and report each one.

## 1. Rules that cannot happen

A rule that assumes a state the rest of the design rules out: a bonus for something the design
never allows, a starting bundle bigger than the holding limit, a trigger on an event that every
other rule prevents. Check every rule's condition against the rules that govern that condition.

## 2. Numbers and timings that clash

The same quantity stated differently in two files; a timing that does not fit inside the
timing that contains it (a step longer than the session it belongs to); a total that the parts
cannot add up to.

## 3. Limits inside the normal case

A limit, penalty or alarm that fires during ordinary, intended use: "late" earlier than the
standard loan length, an anti-stall rule that triggers inside a normal fight's length, a cap
below the starting value. Compare every limit with the normal range the design intends.

## 4. Stale summaries

`README.md`'s hook, purpose, decided table and still-to-design table, and any other summary,
against the area files they summarize. The area file is the truth; the summary is corrected.

## 5. Fairness and abuse

Where money, luck or rank meet: a paid or random advantage leaking into a ranked or competitive
part; a loop that pays out without limit; an action that is always correct, so no decision is
left. Check each pillar against the whole: does anything break it?

## 6. Reporting

Report each finding as one line: what contradicted what, and the fix made. If a fix needs a
decision only the person can make, ask it as a question (`references/questions.md`) instead of
fixing it. If nothing is wrong, change nothing and say so.
```

- [ ] **Step 5: Write the three templates**

`skills/idea-to-design/assets/templates/vision-readme.md`:

```markdown
# <Product name>

<One sentence: what it is.>

## The hook

<What already exists, by name, and the one thing that is new here.>

## Purpose

<What the product is for, and what success means.>

## Pillars

1. **<Pillar>.** <One sentence.>

## How it fits together

<A short picture of how the decided areas connect: the core loop or flow, and what each area
changes in it.>

## Decided

| Area | Decision |
|---|---|
| [<Area>](<area>.md) | <the decision in a line> |

## Still to design

| Area | Status |
|---|---|
| <Area> | <open question / rules agreed, content to design / not started> |

## Parked for later

- <A technical or out-of-scope question raised during design, and its brief answer.>
```

`skills/idea-to-design/assets/templates/alternatives.md`:

```markdown
# Alternatives

Every design question, the option chosen, and the options not taken — kept so later iterations
can pick them up.

## 1. <The question>

**Chosen: <letter> — <option>.** <One line on why.>

| Option | Notes |
|---|---|
| <letter> — <option not taken> | <what it gains, what it costs, where it might fit later> |

## Possible additions

- <An idea left out on purpose, and when to revisit it.>
```

`skills/idea-to-design/assets/templates/area.md`:

```markdown
# <Area>

<The rule of this area in one paragraph: what it is for and how it works.>

## Rules

1. **<Rule>.** <How it works.>

## Still to design

- <Content lists and numbers this area still needs.>
```

- [ ] **Step 6: Point the linter at the new skill**

In `docs/.check_docs.toml`, change `citation_roots` to `["skills/project-bootstrap", "skills/idea-to-design"]` and add `"skills/idea-to-design/assets/templates/"` to `citation_exclude`.

- [ ] **Step 7: Run tests and lint**

Run: `python -m pytest tests -q`
Expected: PASS, including `test_every_skill_relative_path_in_skill_md_exists[idea-to-design]`, `test_skill_paths_resolve_when_copied_alone[idea-to-design]` and the double-brace test.

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .`
Expected: `0 error(s), 0 warning(s)`. If it reports E001 for a `<project>/...` path or a template citation, adjust the config, not the skill text.

- [ ] **Step 8: Reshape the draft against the baseline (writing-skills GREEN)**

Open `evals/baseline-idea-to-design-<date>.md`. For each failed assertion and each "seen but not asserted" behaviour:

1. **Classify it** with writing-skills' "Match the Form to the Failure" table, and record the class in a new "## Failure classes" section of the baseline file:
   - *discipline* — the agent knew better and did it anyway (e.g. picked a stack mid-design, argued against the person's choice): a firm rule, plus a rationalization table of the agent's own words from the baseline, plus a red-flag line;
   - *shape* — the output had the wrong form (several questions in one message, features before purpose): a positive recipe stating what the message IS, its parts in order; no prohibition;
   - *omitted element* — something required was missing (an option not taken left unrecorded, no "Parked for later"): a required slot in the template the agent fills;
   - *conditional* — the behaviour should depend on a condition: a rule keyed to an observable predicate ("if the person raises a technical question…").
2. **Find or write the guidance** in that form in the `SKILL.md` step that owns it. Remove draft wording the baseline shows is unneeded (the control did not fail): write only what a failure calls for.
3. **Micro-test each behaviour-shaping change** before the full re-run: one single-shot fresh subagent per sample, system context = the full `SKILL.md`, user message = the scenario prompt that tempted the failure; 5 samples with the change and 5 with the draft without it (the no-guidance control); read every `final_message.md` yourself. Keep a change only if the control fails and the change's samples converge on the right shape. Record the counts in the baseline file under "## Wording micro-tests".

Then add two sections at the end of `SKILL.md`, from the baseline evidence only:

```markdown
## Red flags

<One line per discipline failure seen in the baseline, in the agent's own words, e.g. "Let me
suggest a tech stack so we can estimate effort." — each means: stop, return to step 7.>

## Common mistakes

| Mistake | Fix |
|---|---|
| <a shape or omission failure seen in the baseline> | <the step and the recipe or slot that prevents it> |
```

Re-run Step 7. Check `SKILL.md` stays under 500 lines (`wc -l skills/idea-to-design/SKILL.md`).

- [ ] **Step 9: Commit**

```bash
git add skills/idea-to-design docs/.check_docs.toml tests/test_kit_consistency.py
git commit -m "idea-to-design: the skill — nine steps, the question method, the consistency pass, templates

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Wire into project-bootstrap, repo docs and manifests; v2.11.0

**Files:**
- Modify: `skills/project-bootstrap/SKILL.md` (§1, after the classification bullets; frontmatter version)
- Modify: `skills/idea-to-design/SKILL.md` (frontmatter version)
- Modify: `README.md`, `BOOTSTRAP.md`, `AGENTS.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill from Task 5.

- [ ] **Step 1: Bump the version in one place and watch the test fail**

Change `version` in `.claude-plugin/plugin.json` to `"2.11.0"`.
Run: `python -m pytest tests/test_skill_package.py -q -k version` → FAIL for both skills (2.10.1 ≠ 2.11.0).

- [ ] **Step 2: Bump the rest**

`"2.11.0"` in `.claude-plugin/marketplace.json` (`plugins[0].version`), in `metadata.version` of both `SKILL.md` files, and in `AGENTS.md`'s version rule, which becomes:

```markdown
- The version is `2.11.0` in `skills/project-bootstrap/SKILL.md` and
  `skills/idea-to-design/SKILL.md` metadata, `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`; bump all four together.
```

Run: `python -m pytest tests/test_skill_package.py -q` → PASS.

- [ ] **Step 3: Manifest descriptions**

`.claude-plugin/plugin.json`: `"description": "Two skills for agent-driven projects: idea-to-design turns a raw idea into a design in docs/vision; project-bootstrap turns a design into docs-as-contract — design docs, milestones, plans, ADRs, and a linter that keeps them true."` and add `"ideation", "product-design"` to `keywords`.
`.claude-plugin/marketplace.json`: both `description` fields become `"Idea-to-design and docs-as-contract bootstrap skills for agent-driven projects."`.

- [ ] **Step 4: project-bootstrap §1 offers idea-to-design**

In `skills/project-bootstrap/SKILL.md`, after the paragraph that begins "Every path runs §1a and §2 first.", add:

```markdown
If the repository is greenfield and the person brings only an idea — nothing written down beyond
a sentence or two — offer the idea-to-design skill first, in one line, when it is installed: it
turns the idea into a design in `<project>/docs/vision/`, which this procedure then reads as a
docs-first project. If they decline, continue here.
```

- [ ] **Step 5: `AGENTS.md`**

Replace the first paragraph ("This repository is the bootstrap kit itself — one Agent Skill at ...") with:

```markdown
This repository is the kit itself — two Agent Skills, not a project built on the kit:
`skills/idea-to-design/` (turns a raw idea into a design in `docs/vision/`; Markdown only) and
`skills/project-bootstrap/` (holding `references/core/`, `references/profiles/`,
`assets/templates/` and `scripts/check_docs.py`). Read `BOOTSTRAP.md` first: it states the idea,
names the machinery, and points into both skills.
```

In the paths rule, change "Inside `skills/project-bootstrap/`, kit paths are relative to the skill root" to "Inside each skill, kit paths are relative to that skill's root".

- [ ] **Step 6: `BOOTSTRAP.md`**

In the first paragraph, after "It contains no templates of its own.", add a new paragraph:

```markdown
**Before bootstrap, if there is only an idea:** the kit's second skill, `skills/idea-to-design/`,
turns a raw idea into a design — its hook, purpose, pillars, every structural decision and the
options not taken — in `<project>/docs/vision/`. Bootstrap then starts from that as a docs-first
project. The chain is *idea-to-design → project-bootstrap → build*.
```

- [ ] **Step 7: `README.md`**

Replace the second paragraph ("The kit ships as one Agent Skill, ...") with:

```markdown
The kit ships as two Agent Skills that follow the [Agent Skills](https://agentskills.io) layout:
`skills/idea-to-design/` turns a raw idea into a design, and `skills/project-bootstrap/` turns a
design into a project — the procedure in `SKILL.md`, the rules in `references/`, the templates in
`assets/`, the linter in `scripts/`. Install both into your agent or just read them.
```

Under "## Use", add before the existing first paragraph:

```markdown
**From an idea.** Tell your agent "I have an idea for …". `idea-to-design` places the idea among
what already exists and names what is new, asks what it is for, then settles every structural
decision one question at a time, each with a recommendation, writing each decision into
`docs/vision/` as it is made and every option not taken into `docs/vision/alternatives.md`. It
holds technology back until the design is agreed, checks the whole design for contradictions at
the end, and offers project-bootstrap as the next step.

**From a design or an existing repo.**
```

In "## Repository layout", add as the second bullet:
`- `skills/idea-to-design/` — the idea-to-design skill: `SKILL.md`, the question method and the consistency pass in `references/`, the `docs/vision/` file shapes in `assets/templates/`.`

- [ ] **Step 8: Tests and lint**

Run: `python -m pytest tests -q` → all pass. Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

- [ ] **Step 9: Commit**

```bash
git add skills/project-bootstrap/SKILL.md skills/idea-to-design/SKILL.md README.md BOOTSTRAP.md AGENTS.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Kit 2.11.0: idea-to-design ships beside project-bootstrap

project-bootstrap offers idea-to-design when a greenfield repo holds only an
idea; the README, BOOTSTRAP.md and AGENTS.md describe a kit of two skills.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Release evals

**Files:**
- Create: `evals/release-k-<date>.md`

- [ ] **Step 1: Prepare all fifteen scenarios with the skills under test**

```bash
python evals/harness.py prepare all evals/runs --label release-k
```

(Each scenario's `"skill"` key picks its skill; the first nine get project-bootstrap.)

- [ ] **Step 2: Run each prompt with a fresh agent**

As Task 4 Step 2, for every `evals/runs/<name>/release-k/prompt.md`, in parallel, with `timing.json` recorded. Before dispatching the nine project-bootstrap scenarios, tell the owner they cost roughly 1.2M tokens together (the earlier releases' totals) and ask whether to run all nine or only `docs-rich-greenfield` and `generation`, the two whose path the §1 change touches; record the choice in the results file.

- [ ] **Step 3: Grade and report**

```bash
python evals/harness.py grade all evals/runs --label release-k
python evals/harness.py report evals/runs
```

- [ ] **Step 4: Fix and re-run until the six idea-to-design scenarios pass in full**

For each failed idea-to-design assertion, read that run's `final_message.md` and files, decide whether the skill text or the assertion is wrong, fix the one that is, and re-run that scenario with a new label (`release-k2`). An assertion is changed only when the agent's behaviour is right and the pattern too narrow; say so in the results file. A skill fix follows writing-skills REFACTOR: classify the failure as in Task 5 Step 8, use the matching form, and add any new rationalization, in the agent's own words, to `SKILL.md`'s "Red flags". Re-run Task 5 Step 7 after any skill edit.

- [ ] **Step 5: Record**

Write `evals/release-k-<date>.md` in the shape of `evals/release-j-2026-10-04.md`: what changed in this release, the results table (baseline vs release for the six new scenarios; release for the bootstrap scenarios run), and every assertion changed in Step 4 with the reason.

- [ ] **Step 6: Lint and commit**

Run: `python -m pytest tests -q` and `python skills/project-bootstrap/scripts/check_docs.py --root .` → all green.

```bash
git add evals/release-k-*.md skills/idea-to-design evals/evals.json
git commit -m "Evals: release K — idea-to-design against its baseline

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Hand back**

Report the results table to the owner and ask whether to push `design/idea-to-design` and open a PR. Do neither without a yes.

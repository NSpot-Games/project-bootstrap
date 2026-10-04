# Tracker Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mirror a kit project's milestones and features onto a GitHub Project, one-way, with the board as the claim lock checked before a feature is claimed.

**Architecture:** A new standard-library script, `skills/project-bootstrap/scripts/sync_tracker.py`, reuses the linter's parsers (`check_docs.py`, same directory) to compute what the board should be, diffs it against the board with a pure function, and applies the diff through one adapter class (`GhBoard`) that is the only code calling the `gh` CLI. The linter gains offline validation of a `[tracker]` config table and one warning (`W009`). The procedure docs and templates gain the claim and Close steps.

**Tech Stack:** Python 3.11+ standard library (`tomllib`, `subprocess`, `json`, `argparse`), the `gh` CLI at run time, pytest.

**Spec:** `docs/superpowers/specs/2026-10-04-tracker-sync-design.md`

## Global Constraints

- Python 3.11+, standard library only; no new dependency anywhere.
- `check_docs.py` stays offline: it never runs `gh`, `git` or touches the network.
- Exit codes of `sync_tracker.py`: 0 ok · 1 usage error, some write failed, or drift found by `check` · 2 board not reached · 3 claim held.
- The board never changes the repo. The only repo write is a `(tracker: #N)` link on a feature line, written by `sync` only; `claim` writes nothing to the repo.
- Paths: inside `skills/project-bootstrap/` kit paths are skill-relative; at the repo root they are full; project paths are `<project>/...` (repo `AGENTS.md`).
- No double-brace placeholders outside `skills/project-bootstrap/assets/templates/` — not in docs, and not in the new Python either (no `{owner}/{repo}` gh placeholders; use the resolved `owner/name`).
- Section numbers are contracts: append (`parallel-agents.md §7`), never renumber; numbered list items in `lifecycle.md §5` are not renumbered.
- A change to what the linter checks adds a test to `tests/test_check_docs.py`.
- `SKILL.md` stays under 500 lines (`tests/test_skill_package.py`).
- Nothing is created on GitHub by the implementer without the owner's yes in that session (Task 8's live check).
- Before every commit: `python -m pytest tests -q` passes and `python skills/project-bootstrap/scripts/check_docs.py --root .` reports `0 error(s), 0 warning(s)`.
- Version `2.10.0` in `skills/project-bootstrap/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the repo `AGENTS.md`, bumped together (Task 8).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. A feature line whose link sits before the plan path (`… (tracker: #4) — \`docs/plans/…\``), because an agent appended the plan path after a link sync had already written: the plan path and the link must both still parse, and `sync` must move the link to the end, not add a second one (Task 1, Task 4).
2. A milestone file with CRLF line endings on a Windows checkout: writing a link must keep every `\r\n` (Task 4).
3. A `(tracker: #N)` pointing at an issue that was deleted or transferred: `sync` falls back to the title lookup or creates a new issue and rewrites the link, rather than failing (Task 3).
4. `sync` run from a stale local `main` (behind `origin/main`) or from a feature branch: it would see a merged feature as unticked and reopen its Done issue, so it refuses and says why (Task 4).
5. Two people running `claim` on the same feature within seconds: both see it free and both assign; after assigning, `claim` re-reads the issue and, with another assignee present, exits 3 for both so a human decides (Task 4).

---

## File map

| File | Responsibility |
|---|---|
| `skills/project-bootstrap/scripts/check_docs.py` (modify) | Parse `(tracker: #N)` anywhere on a feature line; `TrackerConfig` in `Config`; `check_tracker` (E012 at lite, W009) |
| `skills/project-bootstrap/scripts/sync_tracker.py` (create) | Model, diff, apply, link writer, commands, `GhBoard`, CLI |
| `skills/project-bootstrap/assets/templates/check_docs.toml` (modify) | Document the `[tracker]` table, commented out |
| `skills/project-bootstrap/assets/templates/WORKFLOW.md`, `AGENTS.md` (modify) | Claim and Close steps with a tracker |
| `skills/project-bootstrap/SKILL.md`, `references/core/{parallel-agents,lifecycle,long-horizon,adoption}.md` (modify) | Procedure |
| `tests/test_check_docs.py` (modify) | Link parsing, config validation, W009 |
| `tests/test_sync_tracker.py` (create) | Diff, apply, links, commands, `GhBoard`, CLI against the fake |
| `tests/test_kit_consistency.py`, `tests/test_skill_package.py` (modify) | Config template covers `[tracker]`; `Closes #`; skill copied alone runs `sync_tracker.py` |
| `tests/fixture/full/` (modify) | A `[tracker]` table and links |
| `evals/fake_gh.py` (create) | A `gh` stand-in for tests and evals |
| `evals/harness.py`, `evals/evals.json`, `evals/README.md` (modify) | `tracker` and `remote` setup; two scenarios; one generation assertion |
| `README.md`, version files, `evals/release-j-<date>.md` | Release |

---

### Task 1: Feature lines carry a tracker link

**Files:**
- Modify: `skills/project-bootstrap/scripts/check_docs.py` (the `Feature` dataclass near line 245; `FEATURE_RE`/`MOVED_FEATURE_RE` near line 358; `parse_milestone` near line 378)
- Modify: `skills/project-bootstrap/references/core/adoption.md` (§2 step 6)
- Test: `tests/test_check_docs.py`

**Interfaces:**
- Produces: `Feature.tracker: int | None` (last field, default `None`); `TRACKER_LINK_RE` (module constant, `re.compile(r" \(tracker: #(\d+)\)")`) used by Task 4's link writer.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_check_docs.py`:

```python
# --------------------------------------------------------------------------- 2.10.0: tracker links

TRACKER_LINES = [
    ("- [ ] M1-03 — Third thing (tracker: #7)", None, [], 7),
    ("- [x] M1-03 — Third thing — `docs/plans/M1/M1-03-x.md` (tracker: #7)", "docs/plans/M1/M1-03-x.md", [], 7),
    ("- [ ] M1-03 — Third thing — `docs/plans/M1/M1-03-x.md` (depends on: M0-01) (tracker: #7)",
     "docs/plans/M1/M1-03-x.md", ["M0-01"], 7),
    ("- [ ] M1-03 — Third thing (tracker: #7) — `docs/plans/M1/M1-03-x.md`", "docs/plans/M1/M1-03-x.md", [], 7),
    ("- [ ] M1-03 — Parse (raw) notes — v2", None, [], None),
]


@pytest.mark.parametrize("line,plan,deps,tracker", TRACKER_LINES)
def test_feature_line_parses_a_tracker_link_anywhere(tmp_path, line, plan, deps, tracker):
    root = make_project(tmp_path, {"docs/milestones/M1.md": ("- [ ] M1-03 — Third thing", line)})
    f = cd.parse_milestone(root / "docs" / "milestones" / "M1.md").feature("M1-03")
    assert (f.plan_path, f.depends_on, f.tracker) == (plan, deps, tracker)
    assert "tracker" not in f.title


def test_moved_feature_line_parses_a_tracker_link(tmp_path):
    root = make_project(tmp_path, {"docs/milestones/M1.md": (
        "- [ ] M1-03 — Third thing", "- ~~M1-03 — Third thing~~ moved to M1-01 (tracker: #9)")})
    f = cd.parse_milestone(root / "docs" / "milestones" / "M1.md").feature("M1-03")
    assert (f.moved_to, f.tracker) == ("M1-01", 9)


def test_ticked_feature_with_plan_deps_and_link_raises_no_e006(tmp_path):
    root = make_full(tmp_path)
    p = root / "docs" / "milestones" / "M2.md"
    p.write_text(p.read_text(encoding="utf-8").replace(
        "(depends on: M2-01)", "(depends on: M2-01) (tracker: #12)"), encoding="utf-8", newline="\n")
    assert "E006" not in codes(cd.run(root))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest tests/test_check_docs.py -q -k "tracker_link or no_e006"`
Expected: FAIL — `AttributeError: 'Feature' object has no attribute 'tracker'`.

- [ ] **Step 3: Implement** — in `check_docs.py`:

Add the field last in `Feature`:

```python
    line: int
    tracker: int | None = None
```

Next to `FEATURE_RE`, add the link pattern and allow it on moved lines' parse by stripping it first:

```python
# A feature line may carry `(tracker: #N)` (tools/sync_tracker.py writes it last on the line).
# It is read wherever it sits and removed before FEATURE_RE runs, so a plan path appended after
# the link still parses.
TRACKER_LINK_RE = re.compile(r" \(tracker: #(\d+)\)")
```

Replace the body of `parse_milestone` up to the `features.sort(...)` line with:

```python
def parse_milestone(path: Path) -> Milestone:
    text = read_text(path)
    mid, title = _id_and_title(first_heading(text), r"M\d+", path.stem)
    links: dict[int, int] = {}
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        m = TRACKER_LINK_RE.search(ln)
        if m and (ln.startswith("- [") or ln.startswith("- ~~")):
            links[i + 1] = int(m.group(1))
            lines[i] = TRACKER_LINK_RE.sub("", ln)
    clean = "\n".join(lines)
    features: list[Feature] = []
    for m in FEATURE_RE.finditer(clean):
        ln = line_of(clean, m.start())
        features.append(Feature(m.group(2), m.group(3).strip(), m.group(1) in "xX", None,
                                m.group(4), parse_ids(m.group(5)), ln, links.get(ln)))
    for m in MOVED_FEATURE_RE.finditer(clean):
        ln = line_of(clean, m.start())
        features.append(Feature(m.group(1), m.group(2).strip(), False, m.group(3), None, [], ln,
                                links.get(ln)))
    features.sort(key=lambda f: f.line)
```

(The `return Milestone(...)` that follows is unchanged; it keeps reading fields from `text`.)

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests -q`
Expected: all pass (the new 7 included).

- [ ] **Step 5: Say where the link goes, in `references/core/adoption.md` §2 step 6** — replace

`a milestone or feature line cites the issue as \`(tracker: #123)\`,`

with

`a milestone or feature line cites the issue as \`(tracker: #123)\`, written last on the line,`

- [ ] **Step 6: Lint and commit**

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`

```bash
git add skills/project-bootstrap/scripts/check_docs.py skills/project-bootstrap/references/core/adoption.md tests/test_check_docs.py
git commit -m "Linter: a feature line's (tracker: #N) link is read wherever it sits"
```

---

### Task 2: `[tracker]` config, E012 at lite, W009

**Files:**
- Modify: `skills/project-bootstrap/scripts/check_docs.py` (docstring, `CODES`, `Config`, `load_config`, new `check_tracker`, `check`)
- Modify: `skills/project-bootstrap/assets/templates/check_docs.toml`
- Modify: `tests/fixture/full/docs/.check_docs.toml`, `tests/fixture/full/docs/milestones/M2.md`, `tests/fixture/full/docs/milestones/M3.md` (only if `planned`/`in progress`)
- Test: `tests/test_check_docs.py`, `tests/test_kit_consistency.py`

**Interfaces:**
- Consumes: `Feature.tracker` (Task 1).
- Produces: `cd.TrackerConfig(kind: str = "none", owner: str = "", project: int = 0, gh: str = "gh")`; `cd.Config.tracker: TrackerConfig`; `cd.TRACKER_KINDS = ("none", "github-projects")`; `cd.STANDARD_LIKE` (existing) used by Task 5.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_check_docs.py`:

```python
def _with_tracker(root: Path, body: str) -> Path:
    cfg = root / "docs" / ".check_docs.toml"
    cfg.write_text(cfg.read_text(encoding="utf-8") + "\n[tracker]\n" + body, encoding="utf-8", newline="\n")
    return root


GOOD_TRACKER = 'kind = "github-projects"\nowner = "acme"\nproject = 3\n'


def test_tracker_config_is_read(tmp_path):
    root = _with_tracker(make_project(tmp_path), GOOD_TRACKER + 'gh = "tools/gh.py"\n')
    t = cd.load_config(root).tracker
    assert (t.kind, t.owner, t.project, t.gh) == ("github-projects", "acme", 3, "tools/gh.py")


def test_tracker_absent_means_none(tmp_path):
    assert cd.load_config(make_project(tmp_path)).tracker.kind == "none"


@pytest.mark.parametrize("body", [
    'kind = "jira"\n',
    'kind = "github-projects"\nproject = 3\n',
    'kind = "github-projects"\nowner = "acme"\nproject = 0\n',
    'kind = "github-projects"\nowner = "acme"\nproject = true\n',
    'kind = "github-projects"\nowner = "acme"\nproject = "3"\n',
])
def test_bad_tracker_config_is_e012_and_tracker_off(tmp_path, body):
    root = _with_tracker(make_project(tmp_path), body)
    assert cd.load_config(root).tracker.kind == "none"
    assert "E012" in codes(cd.run(root))


def test_tracker_at_lite_is_e012(tmp_path):
    root = make_project(tmp_path)
    shutil.rmtree(root / "docs" / "milestones")
    cfg = root / "docs" / ".check_docs.toml"
    cfg.write_text('tier = "lite"\n[tracker]\n' + GOOD_TRACKER, encoding="utf-8", newline="\n")
    found = cd.run(root)
    assert any(f.code == "E012" and "standard or full" in f.message for f in found)


def test_w009_on_planned_feature_without_link(tmp_path):
    root = _with_tracker(make_project(tmp_path), GOOD_TRACKER)
    found = [f for f in cd.run(root) if f.code == "W009"]
    assert any("M1-03" in f.message for f in found)


def test_w009_silent_with_links_or_without_tracker(tmp_path):
    root = make_project(tmp_path)
    assert "W009" not in codes(cd.run(root))
    _with_tracker(root, GOOD_TRACKER)
    for p in (root / "docs" / "milestones").glob("M*.md"):
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^(- \[[ xX]\] M\d+-(\d+) — .*?)[ \t]*$",
                      lambda m: f"{m.group(1)} (tracker: #{int(m.group(2))})", text)
        p.write_text(text, encoding="utf-8", newline="\n")
    assert "W009" not in codes(cd.run(root))
```

In `tests/test_kit_consistency.py`, replace `test_config_template_documents_every_linter_key` with:

```python
def test_config_template_documents_every_linter_key():
    import dataclasses
    import tomllib
    keys = {f.name for f in dataclasses.fields(cd.Config)} - {"root", "config_error", "tracker"}
    text = _text(TEMPLATES / "check_docs.toml")
    mentioned = set(re.findall(r"^#?\s*([a-z_]+)\s*=", text, re.M))
    assert keys <= mentioned, keys - mentioned
    assert re.search(r"(?m)^#\s*\[tracker\]", text), "the [tracker] table is documented"
    sub = {f.name for f in dataclasses.fields(cd.TrackerConfig)}
    assert sub <= mentioned, sub - mentioned
    active = tomllib.loads(text)
    assert set(active) <= keys, set(active) - keys
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest tests/test_check_docs.py tests/test_kit_consistency.py -q -k "tracker or w009 or config_template"`
Expected: FAIL — `AttributeError: 'Config' object has no attribute 'tracker'`.

- [ ] **Step 3: Implement** — in `check_docs.py`:

Docstring code table: after the `W008` line add

```
  W009 planned feature has no (tracker: #N) while a tracker is configured
```

`CODES`: after `"W008"` add

```python
    "W009": "planned feature has no tracker link",
```

Before `class Config`, add:

```python
TRACKER_KINDS = ("none", "github-projects")


@dataclass
class TrackerConfig:
    """The `[tracker]` table: where tools/sync_tracker.py mirrors milestones and features."""
    kind: str = "none"
    owner: str = ""
    project: int = 0
    gh: str = "gh"
```

In `Config`, before `config_error`, add `tracker: TrackerConfig = field(default_factory=TrackerConfig)`.

In `load_config`, just before `return cfg` at the end of the `if path.exists():` block, add:

```python
        if "tracker" in data:
            err = _load_tracker(cfg, data["tracker"])
            if err:
                cfg.config_error = err
                cfg.tracker = TrackerConfig()
```

and below `load_config`:

```python
def _load_tracker(cfg: Config, raw: object) -> str | None:
    if not isinstance(raw, dict):
        return "[tracker] must be a table"
    t = TrackerConfig(**{k: raw[k] for k in ("kind", "owner", "project", "gh") if k in raw})
    if t.kind not in TRACKER_KINDS:
        return f"tracker kind must be one of {', '.join(TRACKER_KINDS)}, not {t.kind!r}"
    if t.kind == "github-projects":
        if not isinstance(t.owner, str) or not t.owner:
            return "tracker owner must be the GitHub user or organisation that owns the project"
        if isinstance(t.project, bool) or not isinstance(t.project, int) or t.project <= 0:
            return f"tracker project must be a positive project number, not {t.project!r}"
        if not isinstance(t.gh, str) or not t.gh:
            return "tracker gh must be the path or name of the gh executable"
    cfg.tracker = t
    return None
```

Before `# ---- run / main`, add the check:

```python
def check_tracker(project: Project) -> list[Finding]:
    """E012: a GitHub Projects tracker needs milestone files, so the standard or full tier.
    W009: a feature in a planned or in-progress milestone has no `(tracker: #N)` link yet; the
    board lags the repo until the next `tools/sync_tracker.py sync`, so this only warns."""
    t = project.cfg.tracker
    if t.kind != "github-projects":
        return []
    if project.tier not in STANDARD_LIKE:
        return [Finding("E012", "docs/.check_docs.toml", 1,
                        f"invalid config: the tracker needs the standard or full tier, not {project.tier}")]
    out: list[Finding] = []
    for m in project.milestones.values():
        if m.status not in ("planned", "in progress"):
            continue
        for f in m.features:
            if f.tracker is None and not f.moved_to:
                out.append(Finding("W009", rel(project.cfg, m.path), f.line,
                                   f"{f.id} has no (tracker: #N); run tools/sync_tracker.py sync"))
    return out
```

In `check`, after `findings += check_sizes(project)` add `findings += check_tracker(project)`.

- [ ] **Step 4: Document the table** — append to `skills/project-bootstrap/assets/templates/check_docs.toml`:

```toml

# Mirror milestones and features onto a GitHub Project (standard and full tiers only).
# tools/sync_tracker.py reads this table; the linter checks it and warns (W009) on a feature in
# a planned milestone with no `(tracker: #N)` link. The board never changes the repo: a card
# moved by hand is moved back on the next sync. Leave the table commented out for no tracker.
# [tracker]
# kind = "github-projects"   # or "none"
# owner = "<user-or-org>"    # who owns the project
# project = 1                # the project number, from its URL
# gh = "gh"                  # the gh executable; a path is relative to the project root
```

- [ ] **Step 5: Give the full fixture a tracker** — append to `tests/fixture/full/docs/.check_docs.toml`:

```toml

[tracker]
kind = "github-projects"
owner = "acme"
project = 1
```

and add `(tracker: #N)` at the end of every feature line in each fixture milestone whose `**Status:**` is `planned` or `in progress` (number them 1, 2, 3… in file order; e.g. in `M2.md`: `- [ ] M2-03 — Clock agreement (tracker: #6)`). Then run the full-fixture tests: `python -m pytest tests -q -k full` → pass, no new W009.

- [ ] **Step 6: Run everything, lint, commit**

Run: `python -m pytest tests -q` → all pass. Linter on the repo → `0 error(s), 0 warning(s)`.

```bash
git add skills/project-bootstrap/scripts/check_docs.py skills/project-bootstrap/assets/templates/check_docs.toml tests/
git commit -m "Linter: [tracker] config, E012 at lite, W009 for an unlinked planned feature"
```

---

### Task 3: `sync_tracker.py` — model and diff

**Files:**
- Create: `skills/project-bootstrap/scripts/sync_tracker.py`
- Create: `tests/test_sync_tracker.py`

**Interfaces:**
- Consumes: `cd.load_config`, `cd.load_project`, `Project.milestone_order()`, `Project.milestones`, `Project.plans`, `Feature.tracker`.
- Produces (used by Tasks 4–5):
  - constants `TODO, IN_PROGRESS, DONE, NOT_PLANNED = "Todo", "In Progress", "Done", "not planned"`; `DROPPED = "milestone dropped"`; `EXIT_OK, EXIT_USAGE, EXIT_UNREACHED, EXIT_HELD = 0, 1, 2, 3`
  - `Want(fid, title, milestone, status, link, reason="")`
  - `Issue(number, title, state, assignees=[], status=None, milestone=None)` — `status is None` means not on the board; `""` means on the board with no Status set
  - `BoardState(issues: dict[int, Issue], milestones: dict[str, str], default_branch: str = "")`
  - `Change(kind, target, value="", number=None)` — kinds: `create_milestone`, `close_milestone`, `create_issue`, `link`, `rename`, `add_to_project`, `set_status`, `complete`, `close`, `reopen`
  - `wants_from(project) -> list[Want]`, `find_issue(want, board) -> Issue | None`, `plan_changes(wants, board) -> list[Change]`, `describe(change) -> str`

- [ ] **Step 1: Write the failing tests** — create `tests/test_sync_tracker.py`:

```python
"""tools/sync_tracker.py: the diff between the repo and the board, applied through a fake."""
from pathlib import Path

import pytest

import check_docs as cd
import sync_tracker as st

TOML = 'tier = "standard"\n[tracker]\nkind = "github-projects"\nowner = "acme"\nproject = 1\n'

M1 = """# M1 — Ledger
**Status:** in progress
**Exit criteria:** two entries balance.
**Evidence of exit:** docs/evidence/M1-exit.md

## Features
- [x] M1-01 — Schema — `docs/plans/M1/M1-01-schema.md`
- [ ] M1-02 — Add entry — `docs/plans/M1/M1-02-add.md`
- [ ] M1-03 — Reverse entry
"""

PLAN = """# {fid} — {title}
**Status:** {status}

## Sessions
- 2026-10-04T09:00Z — claude-code — feat/{fid}
"""


def make(tmp_path: Path, milestones: dict[str, str] | None = None, plans: dict[str, tuple[str, str]] | None = None):
    root = tmp_path / "p"
    (root / "docs" / "milestones").mkdir(parents=True)
    (root / "docs" / ".check_docs.toml").write_text(TOML, encoding="utf-8", newline="\n")
    for name, text in (milestones or {"M1.md": M1}).items():
        (root / "docs" / "milestones" / name).write_text(text, encoding="utf-8", newline="\n")
    defaults = {"M1-01": ("Schema", "done"), "M1-02": ("Add entry", "in progress")}
    for fid, (title, status) in (defaults if plans is None else plans).items():
        p = root / "docs" / "plans" / fid.split("-")[0] / f"{fid}-x.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(PLAN.format(fid=fid, title=title, status=status), encoding="utf-8", newline="\n")
    return cd.load_project(cd.load_config(root))


def kinds(changes):
    return [(c.kind, c.target, c.value) for c in changes]


def test_wants_from_maps_each_feature(tmp_path):
    w = {x.fid: x for x in st.wants_from(make(tmp_path))}
    assert (w["M1-01"].status, w["M1-02"].status, w["M1-03"].status) == (st.DONE, st.IN_PROGRESS, st.TODO)
    assert w["M1-02"].title == "M1-02 — Add entry"
    assert w["M1-02"].milestone == "M1 — Ledger"


def test_blocked_plan_is_in_progress_and_planned_plan_is_todo(tmp_path):
    p = make(tmp_path, plans={"M1-02": ("Add entry", "blocked"), "M1-03": ("Reverse entry", "planned")})
    w = {x.fid: x.status for x in st.wants_from(p)}
    assert (w["M1-02"], w["M1-03"]) == (st.IN_PROGRESS, st.TODO)


def test_dropped_milestone_and_moved_feature_are_not_planned(tmp_path):
    m4 = "# M4 — Offline\n**Status:** dropped\n\n## Features\n- [ ] M4-01 — Cache\n"
    m1 = M1.replace("- [ ] M1-03 — Reverse entry", "- ~~M1-03 — Reverse entry~~ moved to M1-02")
    w = {x.fid: x for x in st.wants_from(make(tmp_path, {"M1.md": m1, "M4.md": m4}))}
    assert (w["M4-01"].status, w["M4-01"].reason) == (st.NOT_PLANNED, st.DROPPED)
    assert (w["M1-03"].status, w["M1-03"].reason) == (st.NOT_PLANNED, "moved to M1-02")


def test_empty_board_creates_milestone_and_issues(tmp_path):
    changes = st.plan_changes(st.wants_from(make(tmp_path)), st.BoardState())
    assert kinds(changes) == [
        ("create_milestone", "M1 — Ledger", ""),
        ("create_issue", "M1-01", st.DONE),
        ("create_issue", "M1-02", st.IN_PROGRESS),
        ("create_issue", "M1-03", st.TODO),
    ]


def board(*issues, milestones=("M1 — Ledger",)):
    return st.BoardState({i.number: i for i in issues}, {m: "open" for m in milestones})


def test_matching_board_needs_nothing(tmp_path):
    b = board(st.Issue(1, "M1-01 — Schema", "CLOSED", [], st.DONE),
              st.Issue(2, "M1-02 — Add entry", "OPEN", ["ann"], st.IN_PROGRESS),
              st.Issue(3, "M1-03 — Reverse entry", "OPEN", [], st.TODO))
    assert kinds(st.plan_changes(st.wants_from(make(tmp_path)), b)) == [
        ("link", "M1-01", ""), ("link", "M1-02", ""), ("link", "M1-03", "")]


def test_lookup_by_link_first_then_title(tmp_path):
    m1 = M1.replace("- [ ] M1-03 — Reverse entry", "- [ ] M1-03 — Reverse entry (tracker: #9)")
    w = {x.fid: x for x in st.wants_from(make(tmp_path, {"M1.md": m1}))}
    b = board(st.Issue(9, "renamed by hand", "OPEN", [], st.TODO), st.Issue(4, "M1-03 — Reverse entry", "OPEN"))
    assert st.find_issue(w["M1-03"], b).number == 9
    assert st.find_issue(w["M1-02"], b) is None


def test_title_lookup_does_not_match_a_longer_id(tmp_path):
    w = {x.fid: x for x in st.wants_from(make(tmp_path))}
    assert st.find_issue(w["M1-02"], board(st.Issue(5, "M1-020 — Other", "OPEN"))) is None


def test_link_to_a_deleted_issue_falls_back_and_relinks(tmp_path):
    m1 = M1.replace("- [ ] M1-03 — Reverse entry", "- [ ] M1-03 — Reverse entry (tracker: #99)")
    wants = [w for w in st.wants_from(make(tmp_path, {"M1.md": m1})) if w.fid == "M1-03"]
    assert kinds(st.plan_changes(wants, board())) == [("create_issue", "M1-03", st.TODO)]
    found = st.plan_changes(wants, board(st.Issue(4, "M1-03 — Reverse entry", "OPEN", [], st.TODO)))
    assert [(c.kind, c.number) for c in found] == [("link", 4)]


def test_repo_wins_closed_issue_reopened_and_early_done_moved_back(tmp_path):
    wants = [w for w in st.wants_from(make(tmp_path)) if w.fid == "M1-03"]
    b = board(st.Issue(3, "M1-03 — Reverse entry", "CLOSED", [], st.DONE))
    assert [c.kind for c in st.plan_changes(wants, b)] == ["link", "reopen", "set_status"]


def test_assigned_in_progress_is_a_claim_on_another_branch_and_is_kept(tmp_path):
    wants = [w for w in st.wants_from(make(tmp_path)) if w.fid == "M1-03"]
    b = board(st.Issue(3, "M1-03 — Reverse entry", "OPEN", ["bob"], st.IN_PROGRESS))
    assert [c.kind for c in st.plan_changes(wants, b)] == ["link"]
    b.issues[3].assignees = []
    assert [(c.kind, c.value) for c in st.plan_changes(wants, b)][-1] == ("set_status", st.TODO)


def test_ticked_feature_completes_its_issue(tmp_path):
    wants = [w for w in st.wants_from(make(tmp_path)) if w.fid == "M1-01"]
    b = board(st.Issue(1, "M1-01 — Schema", "OPEN", ["ann"], st.IN_PROGRESS))
    assert [(c.kind, c.value) for c in st.plan_changes(wants, b)][1:] == [
        ("set_status", st.DONE), ("complete", "done in the repo")]


def test_renamed_feature_renames_issue_and_off_board_issue_is_added(tmp_path):
    wants = [w for w in st.wants_from(make(tmp_path)) if w.fid == "M1-03"]
    b = board(st.Issue(3, "M1-03 — Old name", "OPEN", [], None))
    assert [c.kind for c in st.plan_changes(wants, b)] == ["link", "rename", "add_to_project", "set_status"]


def test_dropped_and_moved_close_as_not_planned(tmp_path):
    m4 = "# M4 — Offline\n**Status:** dropped\n\n## Features\n- [ ] M4-01 — Cache\n"
    wants = st.wants_from(make(tmp_path, {"M1.md": M1, "M4.md": m4}))
    b = board(st.Issue(8, "M4-01 — Cache", "OPEN", [], st.TODO), milestones=("M1 — Ledger", "M4 — Offline"))
    got = [(c.kind, c.target) for c in st.plan_changes([w for w in wants if w.fid == "M4-01"], b)]
    assert got == [("link", "M4-01"), ("close", "M4-01"), ("close_milestone", "M4 — Offline")]
    assert st.plan_changes([w for w in wants if w.fid == "M4-01"], board(milestones=())) == []
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest tests/test_sync_tracker.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'sync_tracker'`.

- [ ] **Step 3: Implement** — create `skills/project-bootstrap/scripts/sync_tracker.py`:

```python
#!/usr/bin/env python3
"""sync_tracker — mirror a bootstrap-kit project's milestones and features onto a GitHub Project.

Usage: sync_tracker.py [--root PATH] sync [--dry-run] | check | claim <feature-id> [--take | --release]

The repo is the source of status; the board is a mirror plus the claim lock. Nothing read from
the board is written into the repo except the `(tracker: #N)` link that `sync` puts last on a
feature line. Exit: 0 ok; 1 usage error, a failed write, or drift found by `check`; 2 board not
reached; 3 claim held by someone else.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_docs as cd  # noqa: E402  the linter sits beside this file, in the kit and in tools/

TODO, IN_PROGRESS, DONE, NOT_PLANNED = "Todo", "In Progress", "Done", "not planned"
DROPPED = "milestone dropped"
EXIT_OK, EXIT_USAGE, EXIT_UNREACHED, EXIT_HELD = 0, 1, 2, 3
CLAIMED_PLAN_STATUSES = ("in progress", "blocked")


@dataclass
class Want:
    """What the repo says one feature's board item should be."""
    fid: str
    title: str          # the issue title: "M3-02 — <feature title>"
    milestone: str      # the GitHub milestone title: "M3 — <milestone title>"
    status: str         # TODO, IN_PROGRESS, DONE or NOT_PLANNED
    link: int | None    # the feature line's (tracker: #N)
    reason: str = ""    # why NOT_PLANNED: DROPPED or "moved to M7-02"


@dataclass
class Issue:
    number: int
    title: str
    state: str                       # "OPEN" or "CLOSED"
    assignees: list[str] = field(default_factory=list)
    status: str | None = None        # the project item's Status; None: not on the board
    milestone: str | None = None


@dataclass
class BoardState:
    issues: dict[int, Issue] = field(default_factory=dict)
    milestones: dict[str, str] = field(default_factory=dict)   # title -> "open" | "closed"
    default_branch: str = ""


@dataclass(frozen=True)
class Change:
    kind: str           # create_milestone, close_milestone, create_issue, link, rename,
                        # add_to_project, set_status, complete, close, reopen
    target: str         # a feature ID, or a milestone title for the milestone kinds
    value: str = ""     # new title, status, or the reason printed with the change
    number: int | None = None


def describe(c: Change) -> str:
    s = f"{c.kind} {c.target}"
    if c.number is not None:
        s += f" #{c.number}"
    return s + (f": {c.value}" if c.value else "")


def wants_from(project: cd.Project) -> list[Want]:
    out: list[Want] = []
    for mid in project.milestone_order():
        m = project.milestones.get(mid)
        if m is None:
            continue  # a sketch: no milestone file, nothing on the board
        for f in m.features:
            reason = ""
            if m.status == "dropped":
                status, reason = NOT_PLANNED, DROPPED
            elif f.moved_to:
                status, reason = NOT_PLANNED, f"moved to {f.moved_to}"
            elif f.ticked:
                status = DONE
            else:
                plan = project.plans.get(f.id)
                status = IN_PROGRESS if plan and plan.status in CLAIMED_PLAN_STATUSES else TODO
            out.append(Want(f.id, f"{f.id} — {f.title}", f"{m.id} — {m.title}", status, f.tracker, reason))
    return out


def find_issue(want: Want, board: BoardState) -> Issue | None:
    if want.link is not None and want.link in board.issues:
        return board.issues[want.link]
    prefix = f"{want.fid} — "
    hits = sorted(n for n, i in board.issues.items() if i.title.startswith(prefix))
    return board.issues[hits[0]] if hits else None


def plan_changes(wants: list[Want], board: BoardState) -> list[Change]:
    """The changes that make the board match the repo (spec §3.2). Pure: reads, never writes."""
    changes: list[Change] = []
    for title in dict.fromkeys(w.milestone for w in wants if w.status != NOT_PLANNED):
        if title not in board.milestones:
            changes.append(Change("create_milestone", title))
    for w in wants:
        issue = find_issue(w, board)
        if issue is None:
            if w.status != NOT_PLANNED:
                changes.append(Change("create_issue", w.fid, w.status))
            continue
        if w.link != issue.number:
            changes.append(Change("link", w.fid, number=issue.number))
        if w.status == NOT_PLANNED:
            if issue.state == "OPEN":
                changes.append(Change("close", w.fid, w.reason, issue.number))
            continue
        if issue.title != w.title:
            changes.append(Change("rename", w.fid, w.title, issue.number))
        if issue.status is None:
            changes.append(Change("add_to_project", w.fid, number=issue.number))
        if w.status == DONE:
            if issue.status != DONE:
                changes.append(Change("set_status", w.fid, DONE, issue.number))
            if issue.state == "OPEN":
                changes.append(Change("complete", w.fid, "done in the repo", issue.number))
            continue
        if issue.state == "CLOSED":
            changes.append(Change("reopen", w.fid, "the feature is still open in the repo", issue.number))
        if w.status == TODO and issue.status == IN_PROGRESS and issue.assignees:
            continue  # a claim on another branch: only the board knows it yet (spec §3.2)
        if issue.status != w.status:
            changes.append(Change("set_status", w.fid, w.status, issue.number))
    for title in dict.fromkeys(w.milestone for w in wants if w.reason == DROPPED):
        if board.milestones.get(title) == "open":
            changes.append(Change("close_milestone", title))
    return changes
```

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_sync_tracker.py -q` → all pass. Then `python -m pytest tests -q` → all pass.

- [ ] **Step 5: Commit**

```bash
git add skills/project-bootstrap/scripts/sync_tracker.py tests/test_sync_tracker.py
git commit -m "sync_tracker: the repo-to-board diff, pure and tested offline"
```

---

### Task 4: apply, link writer, and the three commands over a board interface

**Files:**
- Modify: `skills/project-bootstrap/scripts/sync_tracker.py`
- Test: `tests/test_sync_tracker.py`

**Interfaces:**
- Consumes: everything Task 3 produces; `cd.TRACKER_LINK_RE` (Task 1).
- Produces (used by Task 5):
  - exceptions `Unreachable`, `BoardError`
  - the board interface every implementation provides: `read() -> BoardState`, `whoami() -> str`, `create_milestone(title)`, `close_milestone(title)`, `create_issue(title, milestone) -> int`, `rename(n, title)`, `add_to_project(n)`, `set_status(n, status)`, `close(n, reason, comment)` (`reason` is `"completed"` or `"not planned"`), `reopen(n, comment)`, `assign(n, login)`, `unassign(n, login)`
  - `apply_changes(changes, api, wants) -> tuple[list[str], list[str], dict[str, int]]` (applied, failed, links)
  - `write_links(project, links: dict[str, int]) -> list[Path]`
  - `git_runner(root) -> Callable[[list[str]], tuple[int, str]]` (exit code, stdout); tests pass their own callable as `git=`
  - `cmd_sync(project, api, dry_run=False, out=print, git=None) -> int`, `cmd_check(project, api, out=print) -> int`, `cmd_claim(project, fid, api, take=False, release=False, out=print) -> int`

- [ ] **Step 1: Write the failing tests** — append to `tests/test_sync_tracker.py`:

```python
class FakeBoard:
    """The board interface, in memory. `fail` names change kinds that raise BoardError."""

    def __init__(self, state: st.BoardState | None = None, me: str = "ann", unreachable: bool = False,
                 fail: tuple[str, ...] = (), on_assign=None):
        self.state = state or st.BoardState(default_branch="main")
        self.me, self.unreachable, self.fail, self.on_assign = me, unreachable, fail, on_assign
        self.calls: list[str] = []

    def _do(self, name):
        self.calls.append(name)
        if name in self.fail:
            raise st.BoardError(f"{name} refused")

    def read(self):
        if self.unreachable:
            raise st.Unreachable("gh is not logged in")
        import copy
        return copy.deepcopy(self.state)

    def whoami(self):
        return self.me

    def create_milestone(self, title):
        self._do("create_milestone"); self.state.milestones[title] = "open"

    def close_milestone(self, title):
        self._do("close_milestone"); self.state.milestones[title] = "closed"

    def create_issue(self, title, milestone):
        self._do("create_issue")
        n = max(self.state.issues, default=0) + 1
        self.state.issues[n] = st.Issue(n, title, "OPEN", [], None, milestone)
        return n

    def rename(self, n, title):
        self._do("rename"); self.state.issues[n].title = title

    def add_to_project(self, n):
        self._do("add_to_project"); self.state.issues[n].status = ""

    def set_status(self, n, status):
        self._do("set_status"); self.state.issues[n].status = status

    def close(self, n, reason, comment):
        self._do("close"); self.state.issues[n].state = "CLOSED"

    def reopen(self, n, comment):
        self._do("reopen"); self.state.issues[n].state = "OPEN"

    def assign(self, n, login):
        self._do("assign"); self.state.issues[n].assignees.append(login)
        if self.on_assign:
            self.on_assign(self.state.issues[n])

    def unassign(self, n, login):
        self._do("unassign"); self.state.issues[n].assignees.remove(login)


ON_MAIN = lambda args: (0, "main\n") if args[:1] == ["rev-parse"] and "--abbrev-ref" in args else (0, "abc\n")


def lines(p):
    return (p.cfg.root / "docs" / "milestones" / "M1.md").read_text(encoding="utf-8")


def test_sync_creates_everything_writes_links_and_is_idempotent(tmp_path):
    p, api, out = make(tmp_path), FakeBoard(), []
    assert st.cmd_sync(p, api, out=out.append, git=ON_MAIN) == st.EXIT_OK
    assert {i.title: (i.state, i.status) for i in api.state.issues.values()} == {
        "M1-01 — Schema": ("CLOSED", st.DONE),
        "M1-02 — Add entry": ("OPEN", st.IN_PROGRESS),
        "M1-03 — Reverse entry": ("OPEN", st.TODO)}
    assert "- [ ] M1-02 — Add entry — `docs/plans/M1/M1-02-add.md` (tracker: #2)" in lines(p)
    p2 = cd.load_project(p.cfg)
    assert [f.tracker for f in p2.milestones["M1"].features] == [1, 2, 3]
    out.clear()
    assert st.cmd_sync(p2, api, out=out.append, git=ON_MAIN) == st.EXIT_OK
    assert out == ["board matches the repo"]


def test_dry_run_writes_nothing(tmp_path):
    p, api, out = make(tmp_path), FakeBoard(), []
    before = lines(p)
    assert st.cmd_sync(p, api, dry_run=True, out=out.append, git=ON_MAIN) == st.EXIT_OK
    assert api.calls == [] and lines(p) == before
    assert out[0].startswith("would create_milestone M1 — Ledger")


def test_one_failing_write_does_not_stop_the_rest(tmp_path):
    p, api, out = make(tmp_path), FakeBoard(fail=("rename",)), []
    api.state.milestones["M1 — Ledger"] = "open"
    api.state.issues[7] = st.Issue(7, "M1-03 — Old", "OPEN", [], st.TODO)
    assert st.cmd_sync(p, api, out=out.append, git=ON_MAIN) == st.EXIT_USAGE
    assert any("failed" in o and "rename" in o for o in out)
    assert len(api.state.issues) == 3


def test_sync_unreachable_is_exit_2(tmp_path):
    assert st.cmd_sync(make(tmp_path), FakeBoard(unreachable=True), out=lambda s: None, git=ON_MAIN) == st.EXIT_UNREACHED


@pytest.mark.parametrize("git,needle", [
    (lambda a: (0, "feat/M1-03-x\n") if "--abbrev-ref" in a else (0, "abc\n"), "from main"),
    (lambda a: (0, "main\n") if "--abbrev-ref" in a else (0, "abc\n" if a[-1] == "HEAD" else "def\n"), "pull"),
])
def test_sync_refuses_off_main_or_behind_origin(tmp_path, git, needle):
    out = []
    assert st.cmd_sync(make(tmp_path), FakeBoard(), out=out.append, git=git) == st.EXIT_USAGE
    assert needle in out[0]


def test_write_links_keeps_crlf_and_moves_a_misplaced_link(tmp_path):
    m1 = M1.replace("- [ ] M1-03 — Reverse entry",
                    "- [ ] M1-03 — Reverse entry (tracker: #4) — `docs/plans/M1/M1-03-r.md`").replace("\n", "\r\n")
    p = make(tmp_path, {"M1.md": m1})
    st.write_links(p, {"M1-03": 4})
    raw = (p.cfg.root / "docs" / "milestones" / "M1.md").read_bytes().decode("utf-8")
    assert "- [ ] M1-03 — Reverse entry — `docs/plans/M1/M1-03-r.md` (tracker: #4)\r\n" in raw
    assert raw.count("\r\n") == m1.count("\r\n") and raw.count("tracker") == 1


def test_check_reports_drift_and_duplicates(tmp_path):
    p, out = make(tmp_path), []
    api = FakeBoard()
    st.cmd_sync(p, api, out=lambda s: None, git=ON_MAIN)
    p = cd.load_project(p.cfg)
    assert st.cmd_check(p, api, out=out.append) == st.EXIT_OK
    api.state.issues[9] = st.Issue(9, "M1-03 — Reverse entry", "OPEN", [], st.TODO)
    api.state.issues[2].status = st.TODO
    out.clear()
    assert st.cmd_check(p, api, out=out.append) == st.EXIT_USAGE
    assert any("duplicate" in o and "#3" in o and "#9" in o for o in out)
    assert any("set_status M1-02" in o for o in out)


def test_claim_free_feature_assigns_and_moves_in_progress(tmp_path):
    p, api = make(tmp_path), FakeBoard()
    assert st.cmd_claim(p, "M1-03", api, out=lambda s: None) == st.EXIT_OK
    issue = next(i for i in api.state.issues.values() if i.title.startswith("M1-03"))
    assert (issue.assignees, issue.status) == (["ann"], st.IN_PROGRESS)
    assert "tracker" not in lines(p), "claim writes nothing to the repo"


def test_claim_held_is_exit_3_and_take_reassigns(tmp_path):
    p = make(tmp_path)
    api = FakeBoard(st.BoardState({3: st.Issue(3, "M1-03 — Reverse entry", "OPEN", ["bob"], st.IN_PROGRESS)},
                                  {"M1 — Ledger": "open"}))
    out = []
    assert st.cmd_claim(p, "M1-03", api, out=out.append) == st.EXIT_HELD
    assert "bob" in out[0] and "assign" not in api.calls
    assert st.cmd_claim(p, "M1-03", api, take=True, out=lambda s: None) == st.EXIT_OK
    assert api.state.issues[3].assignees == ["ann"]


def test_claim_release_unassigns_and_sets_todo(tmp_path):
    p = make(tmp_path)
    api = FakeBoard(st.BoardState({3: st.Issue(3, "M1-03 — Reverse entry", "OPEN", ["ann"], st.IN_PROGRESS)},
                                  {"M1 — Ledger": "open"}))
    assert st.cmd_claim(p, "M1-03", api, release=True, out=lambda s: None) == st.EXIT_OK
    assert (api.state.issues[3].assignees, api.state.issues[3].status) == ([], st.TODO)


def test_claim_unreachable_unknown_and_done(tmp_path):
    p = make(tmp_path)
    assert st.cmd_claim(p, "M1-03", FakeBoard(unreachable=True), out=lambda s: None) == st.EXIT_UNREACHED
    assert st.cmd_claim(p, "M9-01", FakeBoard(), out=lambda s: None) == st.EXIT_USAGE
    assert st.cmd_claim(p, "M1-01", FakeBoard(), out=lambda s: None) == st.EXIT_USAGE


def test_claim_race_two_assignees_is_exit_3(tmp_path):
    p = make(tmp_path)
    api = FakeBoard(on_assign=lambda issue: issue.assignees.append("bob"))
    out = []
    assert st.cmd_claim(p, "M1-03", api, out=out.append) == st.EXIT_HELD
    assert "bob" in out[-1]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest tests/test_sync_tracker.py -q`
Expected: FAIL — `AttributeError: module 'sync_tracker' has no attribute 'cmd_sync'`.

- [ ] **Step 3: Implement** — append to `sync_tracker.py`:

```python
class Unreachable(Exception):
    """The board cannot be read: gh missing, not logged in, offline, or the project not found."""


class BoardError(Exception):
    """One write to the board failed."""


def apply_changes(changes: list[Change], api, wants: list[Want]) -> tuple[list[str], list[str], dict[str, int]]:
    by_fid = {w.fid: w for w in wants}
    applied: list[str] = []
    failed: list[str] = []
    links: dict[str, int] = {}
    for c in changes:
        try:
            if c.kind == "create_milestone":
                api.create_milestone(c.target)
            elif c.kind == "close_milestone":
                api.close_milestone(c.target)
            elif c.kind == "create_issue":
                w = by_fid[c.target]
                n = api.create_issue(w.title, w.milestone)
                links[w.fid] = n
                api.add_to_project(n)
                api.set_status(n, w.status)
                if w.status == DONE:
                    api.close(n, "completed", "")
            elif c.kind == "link":
                links[c.target] = c.number
            elif c.kind == "rename":
                api.rename(c.number, c.value)
            elif c.kind == "add_to_project":
                api.add_to_project(c.number)
            elif c.kind == "set_status":
                api.set_status(c.number, c.value)
            elif c.kind == "complete":
                api.close(c.number, "completed", "")
            elif c.kind == "close":
                api.close(c.number, "not planned", f"Not planned in the repo: {c.value}.")
            elif c.kind == "reopen":
                api.reopen(c.number, f"Reopened by tools/sync_tracker.py: {c.value}.")
        except BoardError as e:
            failed.append(f"{describe(c)} failed: {e}")
            continue
        applied.append(describe(c))
    return applied, failed, links


def write_links(project: cd.Project, links: dict[str, int]) -> list[Path]:
    """Put `(tracker: #N)` last on each named feature line, keeping the file's line endings and
    removing a link that sat anywhere else on the line. The only write this tool makes to the repo."""
    written: list[Path] = []
    for m in project.milestones.values():
        wanted = {f.id: links[f.id] for f in m.features if f.id in links}
        if not wanted:
            continue
        raw = m.path.read_bytes().decode("utf-8")
        out = []
        for line in raw.splitlines(keepends=True):
            body = line.rstrip("\r\n")
            end = line[len(body):]
            hit = re.match(r"- (?:\[[ xX]\] |~~)(M\d+-\d+) — ", body)
            if hit and hit.group(1) in wanted:
                body = cd.TRACKER_LINK_RE.sub("", body).rstrip() + f" (tracker: #{wanted[hit.group(1)]})"
            out.append(body + end)
        new = "".join(out)
        if new != raw:
            m.path.write_bytes(new.encode("utf-8"))
            written.append(m.path)
    return written


def git_runner(root: Path):
    def run(args: list[str]) -> tuple[int, str]:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        return r.returncode, r.stdout
    return run


def _branch_problem(git, default: str) -> str | None:
    """Why `sync` must not write from here: it only sees the checked-out tree, so a stale or
    feature-branch tree would reopen issues that are done on the default branch."""
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"])[1].strip()
    if default and branch != default:
        return f"sync writes from {default} only (checked out: {branch}); switch to {default} and pull"
    if default:
        git(["fetch", "-q", "origin", default])
        if git(["rev-parse", "HEAD"])[1].strip() != git(["rev-parse", f"origin/{default}"])[1].strip():
            return f"{default} is not at origin/{default}; pull first, then sync"
    return None


def cmd_sync(project: cd.Project, api, dry_run: bool = False, out=print, git=None) -> int:
    wants = wants_from(project)
    try:
        board = api.read()
    except Unreachable as e:
        out(f"board not reached: {e}")
        return EXIT_UNREACHED
    changes = plan_changes(wants, board)
    if not changes:
        out("board matches the repo")
        return EXIT_OK
    if dry_run:
        for c in changes:
            out(f"would {describe(c)}")
        return EXIT_OK
    problem = _branch_problem(git or git_runner(project.cfg.root), board.default_branch)
    if problem:
        out(problem)
        return EXIT_USAGE
    applied, failed, links = apply_changes(changes, api, wants)
    written = write_links(project, links)
    for line in applied + failed:
        out(line)
    out(f"{len(applied)} applied, {len(failed)} failed, links written in {len(written)} file(s)")
    return EXIT_USAGE if failed else EXIT_OK


def cmd_check(project: cd.Project, api, out=print) -> int:
    wants = wants_from(project)
    try:
        board = api.read()
    except Unreachable as e:
        out(f"board not reached: {e}")
        return EXIT_UNREACHED
    drift = [describe(c) for c in plan_changes(wants, board)]
    for w in wants:
        dupes = sorted(n for n, i in board.issues.items() if i.title.startswith(f"{w.fid} — "))
        if len(dupes) > 1:
            drift.append(f"duplicate issues for {w.fid}: " + ", ".join(f"#{n}" for n in dupes))
    for d in drift:
        out(d)
    out("board matches the repo" if not drift else f"{len(drift)} difference(s)")
    return EXIT_USAGE if drift else EXIT_OK


def cmd_claim(project: cd.Project, fid: str, api, take: bool = False, release: bool = False, out=print) -> int:
    want = next((w for w in wants_from(project) if w.fid == fid), None)
    if want is None:
        out(f"{fid} is not a feature line in any milestone file")
        return EXIT_USAGE
    if want.status in (DONE, NOT_PLANNED):
        out(f"{fid} is not open in the repo ({want.reason or 'ticked'}); nothing to claim")
        return EXIT_USAGE
    try:
        board = api.read()
        me = api.whoami()
    except Unreachable as e:
        out(f"board not reached: {e}. Claim in the repo and say so under Needs from you.")
        return EXIT_UNREACHED
    issue = find_issue(want, board)
    try:
        if release:
            if issue and me in issue.assignees:
                api.unassign(issue.number, me)
                api.set_status(issue.number, TODO)
            out(f"released {fid}")
            return EXIT_OK
        if issue is None:
            if want.milestone not in board.milestones:
                api.create_milestone(want.milestone)
            n = api.create_issue(want.title, want.milestone)
            api.add_to_project(n)
            issue = Issue(n, want.title, "OPEN", [], "")
        others = [a for a in issue.assignees if a != me]
        if others and not take:
            out(f"{fid} is held by {', '.join(others)} (#{issue.number}). Take it only on a human's "
                f"say-so: sync_tracker.py claim {fid} --take")
            return EXIT_HELD
        for a in others:
            api.unassign(issue.number, a)
        if issue.state == "CLOSED":
            api.reopen(issue.number, f"Reopened by tools/sync_tracker.py: claimed by {me}.")
        if issue.status is None:
            api.add_to_project(issue.number)
        if me not in issue.assignees:
            api.assign(issue.number, me)
        api.set_status(issue.number, IN_PROGRESS)
        after = api.read().issues.get(issue.number)
    except (BoardError, Unreachable) as e:
        out(f"board write failed: {e}. Claim in the repo and say so under Needs from you.")
        return EXIT_UNREACHED
    rivals = [a for a in (after.assignees if after else []) if a != me]
    if rivals:
        out(f"{fid} was claimed at the same moment by {', '.join(rivals)} (#{issue.number}); "
            "both claims stand on the board. Stop and let a human decide who keeps it.")
        return EXIT_HELD
    out(f"claimed {fid} (#{issue.number}) for {me}")
    return EXIT_OK
```

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests/test_sync_tracker.py -q` → all pass; `python -m pytest tests -q` → all pass.

- [ ] **Step 5: Commit**

```bash
git add skills/project-bootstrap/scripts/sync_tracker.py tests/test_sync_tracker.py
git commit -m "sync_tracker: sync, check and claim over a board interface; links written last, CRLF kept"
```

---

### Task 5: `GhBoard`, the CLI, and the fake `gh`

**Files:**
- Modify: `skills/project-bootstrap/scripts/sync_tracker.py`
- Create: `evals/fake_gh.py`
- Test: `tests/test_sync_tracker.py`

**Interfaces:**
- Consumes: Task 4's board interface, exceptions and commands; `cd.TrackerConfig` (Task 2).
- Produces: `GhBoard(root: Path, owner: str, project: int, gh: str = "gh", run=None)` where `run(args: list[str]) -> tuple[int, str, str]`; `main(argv: list[str] | None = None) -> int`; `evals/fake_gh.py` reading `fake_gh.json` and appending to `fake_gh.log` in its own directory, each log line `plans=<count of docs/plans/*/*.md under cwd> <args>`.

- [ ] **Step 1: Write the fake** — create `evals/fake_gh.py`:

```python
#!/usr/bin/env python3
"""A stand-in for the gh CLI, for tests and evals. It answers the calls tools/sync_tracker.py
makes from `fake_gh.json` beside it, applies writes to that file, and appends every call to
`fake_gh.log` with the number of plan files under the working directory at that moment, so a
grader can tell whether the claim ran before the plan was written. Set "offline": true in the
state to make every call fail as a network error would."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE, LOG = HERE / "fake_gh.json", HERE / "fake_gh.log"


def opt(a, name):
    return a[a.index(name) + 1] if name in a else None


def handle(st, a):
    if st.get("offline"):
        return None, "error connecting to api.github.com", 1
    issue = lambda n: next(i for i in st["issues"] if i["number"] == int(n))
    if a[:2] == ["auth", "status"]:
        return "", "", 0
    if a[:2] == ["repo", "view"]:
        return {"nameWithOwner": st["repo"], "defaultBranchRef": {"name": "main"}}, "", 0
    if a[:2] == ["project", "view"]:
        return {"id": "PVT_fake"}, "", 0
    if a[:2] == ["project", "field-list"]:
        opts = [{"id": f"O_{n}", "name": n} for n in ("Todo", "In Progress", "Done")]
        return {"fields": [{"id": "F_status", "name": "Status", "options": opts}]}, "", 0
    if a[:2] == ["project", "item-list"]:
        items = [{"id": f"I_{i['number']}", "content": {"type": "Issue", "number": i["number"], "repository": st["repo"]},
                  **({"status": i["status"]} if i.get("status") else {})} for i in st["issues"] if i.get("on_board")]
        return {"items": items}, "", 0
    if a[:2] == ["issue", "list"]:
        return [{"number": i["number"], "title": i["title"], "state": i["state"],
                 "assignees": [{"login": x} for x in i["assignees"]],
                 "milestone": {"title": i["milestone"]} if i.get("milestone") else None} for i in st["issues"]], "", 0
    if a[:2] == ["api", "user"]:
        return st["me"] + "\n", "", 0
    if a[0] == "api":
        path = next(x for x in a[1:] if x.startswith("repos/"))
        if "-X" in a:
            num = int(path.rsplit("/", 1)[1])
            for m in st["milestones"]:
                if m["number"] == num:
                    m["state"] = "closed"
            return {}, "", 0
        if "-f" in a:
            num = len(st["milestones"]) + 1
            st["milestones"].append({"number": num, "title": opt(a, "-f").split("=", 1)[1], "state": "open"})
            return {"number": num}, "", 0
        return st["milestones"], "", 0
    if a[:2] == ["issue", "create"]:
        n = st["next"]
        st["next"] += 1
        st["issues"].append({"number": n, "title": opt(a, "--title"), "state": "OPEN", "assignees": [],
                             "milestone": opt(a, "--milestone"), "on_board": False})
        return f"https://github.com/{st['repo']}/issues/{n}\n", "", 0
    if a[:2] == ["issue", "edit"]:
        i = issue(a[2])
        if "--title" in a:
            i["title"] = opt(a, "--title")
        if "--add-assignee" in a:
            i["assignees"].append(opt(a, "--add-assignee"))
        if "--remove-assignee" in a:
            i["assignees"].remove(opt(a, "--remove-assignee"))
        return "", "", 0
    if a[:2] == ["issue", "close"]:
        issue(a[2])["state"] = "CLOSED"
        return "", "", 0
    if a[:2] == ["issue", "reopen"]:
        issue(a[2])["state"] = "OPEN"
        return "", "", 0
    if a[:2] == ["project", "item-add"]:
        n = int(opt(a, "--url").rsplit("/", 1)[1])
        issue(n)["on_board"] = True
        return {"id": f"I_{n}"}, "", 0
    if a[:2] == ["project", "item-edit"]:
        issue(opt(a, "--id")[2:])["status"] = opt(a, "--single-select-option-id")[2:]
        return "", "", 0
    return None, f"fake gh: unhandled call: {' '.join(a)}", 1


def main(argv):
    st = json.loads(STATE.read_text(encoding="utf-8"))
    plans = len(list(Path.cwd().glob("docs/plans/*/*.md")))
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"plans={plans} {' '.join(argv)}\n")
    out, err, code = handle(st, argv)
    STATE.write_text(json.dumps(st, indent=1), encoding="utf-8")
    if out is not None:
        sys.stdout.write(out if isinstance(out, str) else json.dumps(out))
    if err:
        sys.stderr.write(err + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 2: Write the failing tests** — append to `tests/test_sync_tracker.py`:

```python
import json
import shutil
import subprocess
import sys

FAKE_GH = Path(__file__).resolve().parents[1] / "evals" / "fake_gh.py"
SYNC = Path(__file__).resolve().parents[1] / "skills" / "project-bootstrap" / "scripts" / "sync_tracker.py"


def fake_gh(root: Path, issues=(), offline=False) -> Path:
    d = root / ".fake-gh"
    d.mkdir()
    shutil.copy(FAKE_GH, d / "fake_gh.py")
    (d / "fake_gh.json").write_text(json.dumps({"repo": "acme/ledger", "me": "ann", "next": 1 + len(issues),
                                                "milestones": [], "issues": list(issues), "offline": offline}),
                                    encoding="utf-8")
    cfg = root / "docs" / ".check_docs.toml"
    cfg.write_text(cfg.read_text(encoding="utf-8") + 'gh = ".fake-gh/fake_gh.py"\n', encoding="utf-8", newline="\n")
    return d


def run_cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SYNC), "--root", str(root), *args], capture_output=True, text=True)


def test_ghboard_reads_and_writes_through_gh(tmp_path):
    p = make(tmp_path)
    d = fake_gh(p.cfg.root, issues=[{"number": 1, "title": "M1-03 — Reverse entry", "state": "OPEN",
                                     "assignees": ["bob"], "milestone": None, "on_board": True, "status": "In Progress"}])
    api = st.GhBoard(p.cfg.root, "acme", 1, str(d / "fake_gh.py"))
    b = api.read()
    assert (b.default_branch, b.issues[1].assignees, b.issues[1].status) == ("main", ["bob"], st.IN_PROGRESS)
    n = api.create_issue("M1-02 — Add entry", "M1 — Ledger")
    api.add_to_project(n)
    api.set_status(n, st.DONE)
    state = json.loads((d / "fake_gh.json").read_text(encoding="utf-8"))
    assert next(i for i in state["issues"] if i["number"] == n)["status"] == "Done"


def test_ghboard_failures_classify(tmp_path):
    p = make(tmp_path)
    with pytest.raises(st.Unreachable):
        st.GhBoard(p.cfg.root, "acme", 1, "no-such-gh-binary").read()
    d = fake_gh(p.cfg.root, offline=True)
    with pytest.raises(st.Unreachable, match="error connecting"):
        st.GhBoard(p.cfg.root, "acme", 1, str(d / "fake_gh.py")).read()
    api = st.GhBoard(p.cfg.root, "acme", 1, run=lambda a: (1, "", "HTTP 403: forbidden\nmore"))
    with pytest.raises(st.BoardError, match="^HTTP 403: forbidden$"):
        api.rename(1, "x")


def test_cli_claim_held_then_free(tmp_path):
    p = make(tmp_path)
    fake_gh(p.cfg.root, issues=[{"number": 1, "title": "M1-03 — Reverse entry", "state": "OPEN",
                                 "assignees": ["alice"], "milestone": None, "on_board": True, "status": "In Progress"}])
    r = run_cli(p.cfg.root, "claim", "M1-03")
    assert r.returncode == 3 and "alice" in r.stdout
    r = run_cli(p.cfg.root, "claim", "M1-03", "--take")
    assert r.returncode == 0, r.stdout + r.stderr


def test_cli_without_tracker_or_at_lite(tmp_path):
    p = make(tmp_path)
    (p.cfg.root / "docs" / ".check_docs.toml").write_text('tier = "standard"\n', encoding="utf-8")
    assert run_cli(p.cfg.root, "sync").returncode == 0
    r = run_cli(p.cfg.root, "claim", "M1-03")
    assert r.returncode == 1 and "no tracker" in r.stdout
```

- [ ] **Step 3: Run them to verify they fail**

Run: `python -m pytest tests/test_sync_tracker.py -q -k "ghboard or cli"`
Expected: FAIL — `AttributeError: module 'sync_tracker' has no attribute 'GhBoard'`.

- [ ] **Step 4: Implement** — append to `sync_tracker.py`:

```python
ISSUE_BODY = ("Mirrored from this repository's milestone files by tools/sync_tracker.py. The "
              "repository is the source of status: a card moved by hand is moved back on the next sync.")


class GhBoard:
    """The board, through the gh CLI. The only code in the kit that talks to GitHub."""

    def __init__(self, root: Path, owner: str, project: int, gh: str = "gh", run=None):
        self.root, self.owner, self.project, self.gh = Path(root), owner, project, gh
        self._run = run or self._subprocess
        self._repo = ""                       # owner/name of the checked-out repository
        self._project_id = ""
        self._field = ""
        self._options: dict[str, str] = {}    # status name -> option id
        self._items: dict[int, str] = {}      # issue number -> project item id
        self._milestones: dict[str, int] = {} # milestone title -> number

    def _subprocess(self, args: list[str]) -> tuple[int, str, str]:
        cmd = [sys.executable, self.gh] if self.gh.endswith(".py") else [self.gh]
        try:
            r = subprocess.run(cmd + args, cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            raise Unreachable(f"{self.gh} not found; install the GitHub CLI and run gh auth login")
        return r.returncode, r.stdout, r.stderr

    def _gh(self, *args: str, read: bool = False) -> str:
        code, out, err = self._run(list(args))
        if code != 0:
            first = ((err or out).strip().splitlines() or [f"gh exited {code}"])[0]
            raise (Unreachable if read else BoardError)(first)
        return out

    def _json(self, *args: str):
        return json.loads(self._gh(*args, read=True) or "null")

    def read(self) -> BoardState:
        self._gh("auth", "status", read=True)
        repo = self._json("repo", "view", "--json", "nameWithOwner,defaultBranchRef")
        self._repo = repo["nameWithOwner"]
        p, o = str(self.project), self.owner
        self._project_id = self._json("project", "view", p, "--owner", o, "--format", "json")["id"]
        fields = self._json("project", "field-list", p, "--owner", o, "--format", "json")["fields"]
        status = next((f for f in fields if f.get("name") == "Status"), None)
        if status is None:
            raise Unreachable(f"project {p} has no Status field")
        self._field = status["id"]
        self._options = {x["name"]: x["id"] for x in status.get("options", [])}
        on_board: dict[int, str] = {}
        for it in self._json("project", "item-list", p, "--owner", o, "--format", "json", "--limit", "1000")["items"]:
            c = it.get("content") or {}
            if c.get("type") == "Issue" and c.get("repository") == self._repo:
                self._items[c["number"]] = it["id"]
                on_board[c["number"]] = it.get("status") or ""
        state = BoardState(default_branch=(repo.get("defaultBranchRef") or {}).get("name", ""))
        for raw in self._json("issue", "list", "--state", "all", "--limit", "1000",
                              "--json", "number,title,state,assignees,milestone"):
            n = raw["number"]
            state.issues[n] = Issue(n, raw["title"], raw["state"],
                                    [a["login"] for a in raw.get("assignees") or []],
                                    on_board.get(n), (raw.get("milestone") or {}).get("title"))
        for ms in self._json("api", f"repos/{self._repo}/milestones?state=all&per_page=100"):
            state.milestones[ms["title"]] = ms["state"]
            self._milestones[ms["title"]] = ms["number"]
        return state

    def whoami(self) -> str:
        return self._gh("api", "user", "--jq", ".login", read=True).strip()

    def create_milestone(self, title: str) -> None:
        out = self._gh("api", f"repos/{self._repo}/milestones", "-f", f"title={title}")
        self._milestones[title] = json.loads(out)["number"]

    def close_milestone(self, title: str) -> None:
        if title not in self._milestones:
            raise BoardError(f"no GitHub milestone named {title!r}")
        self._gh("api", "-X", "PATCH", f"repos/{self._repo}/milestones/{self._milestones[title]}", "-f", "state=closed")

    def create_issue(self, title: str, milestone: str) -> int:
        out = self._gh("issue", "create", "--title", title, "--milestone", milestone, "--body", ISSUE_BODY)
        return int(out.strip().rsplit("/", 1)[-1])

    def rename(self, n: int, title: str) -> None:
        self._gh("issue", "edit", str(n), "--title", title)

    def add_to_project(self, n: int) -> None:
        out = self._gh("project", "item-add", str(self.project), "--owner", self.owner,
                       "--url", f"https://github.com/{self._repo}/issues/{n}", "--format", "json")
        self._items[n] = json.loads(out)["id"]

    def set_status(self, n: int, status: str) -> None:
        if status not in self._options:
            raise BoardError(f"the project's Status field has no option {status!r}")
        if n not in self._items:
            raise BoardError(f"#{n} is not on the project")
        self._gh("project", "item-edit", "--id", self._items[n], "--project-id", self._project_id,
                 "--field-id", self._field, "--single-select-option-id", self._options[status])

    def close(self, n: int, reason: str, comment: str) -> None:
        args = ["issue", "close", str(n), "--reason", reason]
        self._gh(*(args + ["--comment", comment] if comment else args))

    def reopen(self, n: int, comment: str) -> None:
        self._gh("issue", "reopen", str(n), "--comment", comment)

    def assign(self, n: int, login: str) -> None:
        self._gh("issue", "edit", str(n), "--add-assignee", login)

    def unassign(self, n: int, login: str) -> None:
        self._gh("issue", "edit", str(n), "--remove-assignee", login)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mirror milestones and features onto a GitHub Project.")
    ap.add_argument("--root", default=".", help="project root (default: current directory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="make the board match the repo; run from the default branch")
    s.add_argument("--dry-run", action="store_true", help="print the changes, apply none")
    sub.add_parser("check", help="list where the board and the repo disagree")
    c = sub.add_parser("claim", help="the claim lock: assign the feature's issue and move it to In Progress")
    c.add_argument("feature", help="a feature ID, M<n>-<nn>")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--take", action="store_true", help="reassign a held feature (a human said so)")
    g.add_argument("--release", action="store_true", help="give up a claim abandoned without Close")
    args = ap.parse_args(argv)
    cfg = cd.load_config(Path(args.root).resolve())
    project = cd.load_project(cfg)
    t = cfg.tracker
    if t.kind != "github-projects" or project.tier not in cd.STANDARD_LIKE:
        why = ("no tracker configured" if t.kind != "github-projects"
               else f"the tracker needs the standard or full tier, not {project.tier}")
        print(f"sync_tracker: {why} ([tracker] in docs/.check_docs.toml)")
        return EXIT_USAGE if args.cmd == "claim" else EXIT_OK
    gh = t.gh
    if ("/" in gh or "\\" in gh) and not Path(gh).is_absolute():
        gh = str(cfg.root / gh)
    api = GhBoard(cfg.root, t.owner, t.project, gh)
    if args.cmd == "sync":
        return cmd_sync(project, api, dry_run=args.dry_run)
    if args.cmd == "check":
        return cmd_check(project, api)
    return cmd_claim(project, args.feature, api, take=args.take, release=args.release)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the tests**

Run: `python -m pytest tests -q` → all pass.

- [ ] **Step 6: Commit**

```bash
git add skills/project-bootstrap/scripts/sync_tracker.py evals/fake_gh.py tests/test_sync_tracker.py
git commit -m "sync_tracker: GhBoard over the gh CLI, the command line, and a fake gh for tests and evals"
```

---

### Task 6: Procedure, references and templates

**Files:**
- Modify: `skills/project-bootstrap/SKILL.md` (§4 step 2 and step 6, new step 7; §5)
- Modify: `skills/project-bootstrap/references/core/parallel-agents.md` (§1; new §7)
- Modify: `skills/project-bootstrap/references/core/lifecycle.md` (§5 item 6)
- Modify: `skills/project-bootstrap/references/core/long-horizon.md` (§4 item 2)
- Modify: `skills/project-bootstrap/assets/templates/WORKFLOW.md` (§3, §4, §10 item 2)
- Modify: `skills/project-bootstrap/assets/templates/AGENTS.md` (How to work, step 1)
- Test: `tests/test_kit_consistency.py`, `tests/test_skill_package.py`

**Interfaces:**
- Consumes: the CLI of Task 5 (`python tools/sync_tracker.py sync|check|claim <id> [--take|--release]`), exit codes 0/1/2/3.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_kit_consistency.py`:

```python
def test_tracker_procedure_is_written_where_sessions_read_it():
    workflow = _text(TEMPLATES / "WORKFLOW.md")
    assert "tools/sync_tracker.py claim" in workflow
    assert "Closes #" in workflow
    assert "moved back" in workflow, "WORKFLOW.md says the board never changes the repo"
    skill = _text(SKILL_DIR / "SKILL.md")
    assert "sync_tracker.py" in skill and "GitHub Project" in skill
    assert "## 7. Tracker mirror" in _text(REFERENCES / "core" / "parallel-agents.md")
    assert "Closes #" in _text(REFERENCES / "core" / "lifecycle.md")
```

and to `tests/test_skill_package.py`, after `test_skill_directory_works_when_copied_alone`:

```python
def test_sync_tracker_runs_when_the_skill_is_copied_alone(tmp_path):
    dest = tmp_path / "skill"
    shutil.copytree(SKILL_DIR, dest)
    r = subprocess.run([sys.executable, str(dest / "scripts" / "sync_tracker.py"), "--root", str(tmp_path), "sync"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "no tracker configured" in r.stdout, r.stdout + r.stderr
```

(Add `import sys` at the top of `tests/test_skill_package.py` if it is not imported.)

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest tests/test_kit_consistency.py tests/test_skill_package.py -q -k "tracker or sync_tracker"`
Expected: `test_tracker_procedure...` FAILS (`assert 'tools/sync_tracker.py claim' in ...`); the copied-alone test PASSES already (Task 5 made it true) — keep it as the guard.

- [ ] **Step 3: Edit `SKILL.md` §4.** At the end of step 2 (after "...wire it as `scripts/hooks/README.md` shows."), add:

```markdown
   The tracker is the user's choice too, asked in the same gate message and only when the
   repository has a GitHub remote: "This repository has a GitHub remote. Create a GitHub
   Project and sync the milestones to it?" Nothing is created on GitHub before a yes (§4, step 7).
```

In step 6, replace `the hook question from step 2,` with `the hook and tracker questions from step 2,`. After step 6 add:

```markdown
7. On a yes to the tracker: `gh project create --owner <owner> --title "<Project>"` (the owner
   from the remote), `gh project link <number> --owner <owner> --repo <owner>/<name>`, copy
   `scripts/sync_tracker.py` to `<project>/tools/sync_tracker.py`, uncomment the `[tracker]`
   table in `<project>/docs/.check_docs.toml` with that owner and number, then run
   `python tools/sync_tracker.py sync` and commit the `(tracker: #N)` links it writes. The
   project's built-in "Item closed" workflow sets Done when a PR with `Closes #N` merges; say so
   in one line. A `gh` that is missing or not logged in is the user's to fix: name the command
   (`gh auth login --scopes project`) and carry on without the tracker.
```

In §5, after "Open `<project>/docs/CURRENT.md` and claim `M0-01`:", insert: "with a tracker, run `python tools/sync_tracker.py claim M0-01` first — exit 3 means someone else holds it, so stop and report who; exit 2 means the board was not reached, so claim in the repo and put it under Needs from you; then" — and keep the rest of the sentence ("copy `<project>/tools/templates/plan.md` ...").

Check: `python -c "print(len(open('skills/project-bootstrap/SKILL.md',encoding='utf-8').read().splitlines()))"` → under 500.

- [ ] **Step 4: Edit `references/core/parallel-agents.md`.** At the end of §1 add:

```markdown
With a tracker configured (`[tracker]` in `<project>/docs/.check_docs.toml`), the claim starts
with `python tools/sync_tracker.py claim <id>`, before the plan file is written: exit 0 assigns
the feature's issue and moves it to In Progress; exit 3 means someone else is assigned, which is
this section's hard stop — the claim proceeds only on a human's say-so, with `--take`; exit 2
means the board was not reached, and the claim proceeds in the repo with that said in the
session report (`references/core/economy.md §4`).
```

Append a new section after §6:

```markdown
## 7. Tracker mirror

A project may mirror its milestones and features onto a GitHub Project with
`tools/sync_tracker.py`, so people who never open the repository see the plan, and a claim made
on one branch is visible to every other branch at once. The mirror is one-way: status lives in
the milestone and plan files (`references/core/layers.md §4`), `sync` makes the board match
them, and nothing done on the board changes the repository; a card moved by hand is moved back
on the next `sync`. The one exception is the claim lock: `sync` sees only the checked-out tree,
so it never moves an assigned In Progress card back to Todo, because that card is a claim whose
plan lives on a branch not yet merged. For the same reason `sync` writes only from the default
branch, up to date with its remote. Done comes from the merge: the PR body carries `Closes #N`
and the project's built-in "Item closed" workflow moves the card, with no CI and no stored
token. The only thing `sync` writes into the repository is a `(tracker: #N)` link, last on the
feature line; the linter warns (`W009`) on a planned feature without one.
```

- [ ] **Step 5: Edit `references/core/lifecycle.md` §5 item 6** — replace

`6. Run \`tools/check_docs.py --fix\` and commit the regenerated indexes alongside the rest of the change.`

with

`6. Run \`tools/check_docs.py --fix\` and commit the regenerated indexes alongside the rest of the change. With a tracker, the PR body carries \`Closes #N\` for the feature's issue, so the merge moves its card to Done (\`references/core/parallel-agents.md §7\`).`

and `references/core/long-horizon.md §4` item 2 — replace

`2. Promote the next \`sketch\` milestone to \`planned\` with a real, measurable exit.`

with

`2. Promote the next \`sketch\` milestone to \`planned\` with a real, measurable exit; with a tracker, run \`tools/sync_tracker.py sync\` once it is merged, so its features get issues.`

- [ ] **Step 6: Edit the templates.** In `assets/templates/WORKFLOW.md` §3, after the sentence ending "...Never take a feature stamped under 24 hours ago by someone else." add:

`With a tracker (\`[tracker]\` in \`docs/.check_docs.toml\`), run \`python tools/sync_tracker.py claim M<n>-<nn>\` before writing the plan: exit 3 means someone else holds it — stop and say who; exit 2 means the board was not reached — claim anyway and say so under Needs from you. The board mirrors the repo and never changes it: a card moved by hand is moved back on the next \`python tools/sync_tracker.py sync\`, which runs from an up-to-date \`main\`.`

In §4, replace `PRs link the plan; don't duplicate it.` with `PRs link the plan; don't duplicate it. With a tracker, the PR body carries \`Closes #N\` for the feature's issue.`

In §10 item 2, replace `2. Promote the next \`sketch\` milestone to \`planned\` with a real exit.` with `2. Promote the next \`sketch\` milestone to \`planned\` with a real exit; with a tracker, \`python tools/sync_tracker.py sync\` once merged.`

In `assets/templates/AGENTS.md`, "How to work" step 1, replace `set its plan to \`in progress\` and add a session stamp under \`## Sessions\`.` with `with a tracker, run \`python tools/sync_tracker.py claim <id>\` first (\`docs/WORKFLOW.md\` §3); set its plan to \`in progress\` and add a session stamp under \`## Sessions\`.`

- [ ] **Step 7: Run everything, lint, commit**

Run: `python -m pytest tests -q` → all pass. Linter → `0 error(s), 0 warning(s)`.

```bash
git add skills/project-bootstrap/SKILL.md skills/project-bootstrap/references skills/project-bootstrap/assets/templates tests/
git commit -m "Procedure: the tracker question at generation, claim first, Closes #N at Close, parallel-agents §7"
```

---

### Task 7: Evals

**Files:**
- Modify: `evals/harness.py` (`prepare`)
- Modify: `evals/evals.json` (two scenarios; one assertion in `generation`)
- Modify: `evals/README.md` (scenario table and count)
- Test: `tests/test_sync_tracker.py` (harness prepares the tracker scenarios)

**Interfaces:**
- Consumes: `evals/fake_gh.py` (Task 5), `skills/project-bootstrap/scripts/sync_tracker.py`.
- Produces: setup keys `"copy_sync": true`, `"tracker": {"held_by": "<login>" | null}`, `"remote": "<url>"`.

- [ ] **Step 1: Write the failing test** — append to `tests/test_sync_tracker.py`:

```python
def test_harness_prepares_tracker_scenarios(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
    import harness
    skill = Path(__file__).resolve().parents[1] / "skills" / "project-bootstrap"
    for name, holder in (("tracker-claim", None), ("tracker-held", "alice")):
        project = harness.prepare(name, tmp_path, "t", skill) / "project"
        state = json.loads((project / ".fake-gh" / "fake_gh.json").read_text(encoding="utf-8"))
        assert [i["assignees"] for i in state["issues"]] == ([] if holder is None else [[holder]])
        assert (project / "tools" / "sync_tracker.py").is_file()
        r = run_cli(project, "claim", "M0-01")
        assert r.returncode == (0 if holder is None else 3), r.stdout + r.stderr
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_sync_tracker.py -q -k harness`
Expected: FAIL — `KeyError` / `StopIteration` for scenario `tracker-claim`.

- [ ] **Step 3: Implement in `evals/harness.py`.** Near the `LINTER` constant add:

```python
SYNC = DEFAULT_SKILL / "scripts" / "sync_tracker.py"
FAKE_GH = HERE / "fake_gh.py"
```

In `prepare`, after the `copy_linter` block add:

```python
    if setup.get("copy_sync"):
        (project / "tools").mkdir(exist_ok=True)
        shutil.copy(SYNC, project / "tools" / "sync_tracker.py")
    if "tracker" in setup:
        _fake_tracker(project, setup["tracker"].get("held_by"))
```

and change the git block's first line to `if setup.get("git") or setup.get("remote"):`, adding inside it, after the commit, `if setup.get("remote"): git(project, "remote", "add", "origin", setup["remote"])`.

Add the helper above `prepare`:

```python
def _fake_tracker(project: Path, held_by: str | None) -> None:
    """A fake gh in <project>/.fake-gh and a [tracker] table pointing at it. When `held_by` is
    set, the first feature of M0 already has an issue assigned to that login, In Progress."""
    d = project / ".fake-gh"
    d.mkdir()
    shutil.copy(FAKE_GH, d / "fake_gh.py")
    issues = []
    if held_by:
        first = re.search(r"(?m)^- \[ \] (M0-01 — .*?)(?: — `|\s*$)", _read(project / "docs" / "milestones" / "M0.md"))
        issues.append({"number": 1, "title": first.group(1).strip(), "state": "OPEN", "assignees": [held_by],
                       "milestone": None, "on_board": True, "status": "In Progress"})
    (d / "fake_gh.json").write_text(json.dumps({"repo": "example/fieldnote", "me": "bootstrap-agent",
                                                "next": len(issues) + 1, "milestones": [], "issues": issues}),
                                    encoding="utf-8")
    cfg = project / "docs" / ".check_docs.toml"
    cfg.write_text(_read(cfg) + '\n[tracker]\nkind = "github-projects"\nowner = "example"\nproject = 1\n'
                   'gh = ".fake-gh/fake_gh.py"\n', encoding="utf-8", newline="\n")
```

- [ ] **Step 4: Add the scenarios to `evals/evals.json`** (ids 8 and 9, after `ci-default`):

```json
    {
      "id": 8,
      "name": "tracker-claim",
      "fixture": "generated",
      "setup": {"git": false, "copy_linter": true, "copy_sync": true, "tracker": {"held_by": null}},
      "prompt": "The bootstrap of this project is complete and reviewed, and the user said yes to the GitHub Project, which is set up (see [tracker] in docs/.check_docs.toml). Open the first session exactly as the skill's section 5 describes, then stop before writing any implementation code.",
      "expected_output": "The claim command runs before the plan is written and assigns M0-01; then the plan, the stamp, the M0 status and the regenerated files are as in first-session.",
      "assertions": [
        {"text": "claim assigned M0-01 before any plan file existed", "check": "grep", "path": ".fake-gh/fake_gh.log", "pattern": "(?m)^plans=0 issue edit \\d+ --add-assignee bootstrap-agent"},
        {"text": "M0 is now in progress", "check": "grep", "path": "docs/milestones/M0.md", "pattern": "(?m)^\\*\\*Status:\\*\\* in progress"},
        {"text": "Exactly one plan exists for M0-01", "check": "count_glob", "glob": "docs/plans/M0/M0-01-*.md", "min": 1, "max": 1},
        {"text": "The plan is claimed (status in progress)", "check": "grep_any", "glob": "docs/plans/M0/M0-01-*.md", "pattern": "(?m)^\\*\\*Status:\\*\\* in progress"},
        {"text": "The project lints with zero errors", "check": "lint", "max_errors": 0}
      ]
    },
    {
      "id": 9,
      "name": "tracker-held",
      "fixture": "generated",
      "setup": {"git": false, "copy_linter": true, "copy_sync": true, "tracker": {"held_by": "alice"}},
      "prompt": "The bootstrap of this project is complete and reviewed, and the user said yes to the GitHub Project, which is set up (see [tracker] in docs/.check_docs.toml). Open the first session exactly as the skill's section 5 describes, then stop before writing any implementation code.",
      "expected_output": "claim exits 3 naming alice; no plan is written, M0 stays planned, and the final message tells the human who holds M0-01.",
      "assertions": [
        {"text": "claim was run", "check": "grep", "path": ".fake-gh/fake_gh.log", "pattern": "(?m)^plans=0 api user"},
        {"text": "No plan was written for a held feature", "check": "count_glob", "glob": "docs/plans/M*/M*-*.md", "max": 0},
        {"text": "M0 was not set in progress", "check": "not_grep", "path": "docs/milestones/M0.md", "pattern": "(?m)^\\*\\*Status:\\*\\* in progress"},
        {"text": "The board was not taken over", "check": "not_grep", "path": ".fake-gh/fake_gh.log", "pattern": "--remove-assignee alice"},
        {"text": "The final message names who holds M0-01", "check": "final_contains", "pattern": "alice"}
      ]
    }
```

In the `generation` scenario, set `"setup": {"git": false, "copy_linter": false, "remote": "https://github.com/example/fieldnote.git"}` and append two assertions:

```json
        {"text": "The gate message asks about a GitHub Project", "check": "final_contains", "pattern": "(?i)github project"},
        {"text": "No tracker was set up without the user's yes", "check": "not_grep", "path": "docs/.check_docs.toml", "pattern": "(?m)^\\[tracker\\]"}
```

- [ ] **Step 5: Update `evals/README.md`** — "the seven scenarios" → "the nine scenarios", and add two rows to the scenario table:

```markdown
| `tracker-claim` | SKILL.md §5 with a tracker | `claim` runs before the plan is written and assigns the feature |
| `tracker-held` | the claim lock | a feature assigned to someone else is not claimed, and the human is told who holds it |
```

Add one line under the layout list: `- \`fake_gh.py\` — a stand-in for the gh CLI that the tracker scenarios put in \`<project>/.fake-gh/\`; it answers from a JSON state file and logs every call.`

- [ ] **Step 6: Run everything, lint, commit**

Run: `python -m pytest tests -q` → all pass. Linter → `0 error(s), 0 warning(s)`.

```bash
git add evals/ tests/test_sync_tracker.py
git commit -m "Evals: tracker-claim and tracker-held scenarios with a fake gh; generation asks about the project"
```

---

### Task 8: Release 2.10.0

**Files:**
- Modify: `skills/project-bootstrap/SKILL.md` (metadata version), `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`
- Create: `evals/release-j-<date>.md`

- [ ] **Step 1: Bump the version** in the four files from `2.9.1` to `2.10.0`. Run `python -m pytest tests -q -k version` → pass.

- [ ] **Step 2: README section.** Add to `README.md`, after the section that describes the linter and hooks:

```markdown
## Tracker sync

At generation the skill offers to mirror the project's milestones and features onto a GitHub
Project (`skills/project-bootstrap/scripts/sync_tracker.py`, copied to `tools/`). The repository
stays the source of status; the board is a one-way mirror plus the claim lock: a session runs
`tools/sync_tracker.py claim <id>` before it writes a plan, and stops if someone else is
assigned. Merging a PR whose body says `Closes #N` moves the card to Done through the project's
built-in workflow, so no CI or stored token is needed. It needs the GitHub CLI logged in with the
`project` scope (`gh auth login --scopes project`). Linear and Jira are not supported yet.
```

- [ ] **Step 3: Run the eval scenarios.** Per `evals/README.md`: `python evals/harness.py prepare <name> --label 2.10.0` for each of the nine scenarios, run each prompt in a fresh agent session, `python evals/harness.py grade <name> --label 2.10.0`, then `python evals/harness.py report`. Expected: every existing assertion still passes, and `tracker-claim` and `tracker-held` pass in full. Record the table in `evals/release-j-<date>.md` in the form of `evals/release-h-2026-09-25.md`.

- [ ] **Step 4: Live check — ask the owner first.** Post: "Ready for the live check: I'd create a throwaway private repository `tracker-sync-check` under your account and a GitHub Project linked to it, run a sync, a claim and a merged PR with `Closes #1`, then delete both. OK?" Only on a yes:
  1. `gh repo create tracker-sync-check --private --clone`; copy `tests/fixture/full` into it, `tools/check_docs.py`, `tools/sync_tracker.py`; commit and push `main`.
  2. `gh auth refresh --scopes project`; `gh project create --owner @me --title tracker-sync-check`; `gh project link <n> --owner @me --repo <me>/tracker-sync-check`; write `[tracker]` with `owner = "<me>"`, `project = <n>`.
  3. `python tools/sync_tracker.py sync` → issues and milestones created; `python tools/sync_tracker.py check` → exit 0. If `item-list` JSON names the Status key differently than `status`, or `content.repository` is not `owner/name`, fix `GhBoard.read` and add the observed shape to `evals/fake_gh.py`.
  4. Branch, `python tools/sync_tracker.py claim M2-03` → exit 0, card In Progress and assigned on the board.
  5. Tick `M2-03` on the branch, open a PR with `Closes #<n>`, merge it → the card is in Done within a minute (the built-in "Item closed" workflow). If it is not, enable that workflow in the project settings and say so in the SKILL step 7 sentence.
  6. Record the outcome in `evals/release-j-<date>.md`; `gh repo delete <me>/tracker-sync-check --yes` and `gh project delete <n> --owner @me` (both after the owner's earlier yes).

- [ ] **Step 5: Final verification and commit**

Run: `python -m pytest tests -q` → all pass; linter → `0 error(s), 0 warning(s)`.

```bash
git add -A
git commit -m "Release 2.10.0: tracker sync — GitHub Projects as a one-way mirror and claim lock"
```

Then push the branch and open the PR (the owner decides on merge and the `v2.10.0` tag).

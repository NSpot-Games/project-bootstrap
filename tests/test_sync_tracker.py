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


def board(*issues, milestones=("M1 — Ledger",)):
    return st.BoardState({i.number: i for i in issues}, {m: "open" for m in milestones})


# --------------------------------------------------------------------------- what the repo wants


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


# --------------------------------------------------------------------------- the diff


def test_empty_board_creates_milestone_and_issues(tmp_path):
    changes = st.plan_changes(st.wants_from(make(tmp_path)), st.BoardState())
    assert kinds(changes) == [
        ("create_milestone", "M1 — Ledger", ""),
        ("create_issue", "M1-01", st.DONE),
        ("create_issue", "M1-02", st.IN_PROGRESS),
        ("create_issue", "M1-03", st.TODO),
    ]


def test_matching_board_needs_only_the_links(tmp_path):
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
    wants = [w for w in st.wants_from(make(tmp_path, {"M1.md": M1, "M4.md": m4})) if w.fid == "M4-01"]
    b = board(st.Issue(8, "M4-01 — Cache", "OPEN", [], st.TODO), milestones=("M1 — Ledger", "M4 — Offline"))
    got = [(c.kind, c.target) for c in st.plan_changes(wants, b)]
    assert got == [("link", "M4-01"), ("close", "M4-01"), ("close_milestone", "M4 — Offline")]
    assert st.plan_changes(wants, board(milestones=())) == []

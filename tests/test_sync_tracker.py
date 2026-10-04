"""tools/sync_tracker.py: the diff between the repo and the board, applied through a fake."""
import copy
import json
import shutil
import subprocess
import sys
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


# --------------------------------------------------------------------------- commands over a fake board


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
        return copy.deepcopy(self.state)

    def whoami(self):
        return self.me

    def create_milestone(self, title):
        self._do("create_milestone")
        self.state.milestones[title] = "open"

    def close_milestone(self, title):
        self._do("close_milestone")
        self.state.milestones[title] = "closed"

    def create_issue(self, title, milestone):
        self._do("create_issue")
        n = max(self.state.issues, default=0) + 1
        self.state.issues[n] = st.Issue(n, title, "OPEN", [], None, milestone)
        return n

    def rename(self, n, title):
        self._do("rename")
        self.state.issues[n].title = title

    def add_to_project(self, n):
        self._do("add_to_project")
        self.state.issues[n].status = ""

    def set_status(self, n, status):
        self._do("set_status")
        self.state.issues[n].status = status

    def close(self, n, reason, comment):
        self._do("close")
        self.state.issues[n].state = "CLOSED"

    def reopen(self, n, comment):
        self._do("reopen")
        self.state.issues[n].state = "OPEN"

    def assign(self, n, login):
        self._do("assign")
        self.state.issues[n].assignees.append(login)
        if self.on_assign:
            self.on_assign(self.state.issues[n])

    def unassign(self, n, login):
        self._do("unassign")
        self.state.issues[n].assignees.remove(login)


def on_main(args):
    return (0, "main\n") if "--abbrev-ref" in args else (0, "abc\n")


def off_main(args):
    return (0, "feat/M1-03-x\n") if "--abbrev-ref" in args else (0, "abc\n")


def behind_origin(args):
    if "--abbrev-ref" in args:
        return 0, "main\n"
    return 0, ("abc\n" if args[-1] == "HEAD" else "def\n")


def lines(p):
    return (p.cfg.root / "docs" / "milestones" / "M1.md").read_text(encoding="utf-8")


def test_sync_creates_everything_writes_links_and_is_idempotent(tmp_path):
    p, api, out = make(tmp_path), FakeBoard(), []
    assert st.cmd_sync(p, api, out=out.append, git=on_main) == st.EXIT_OK
    assert {i.title: (i.state, i.status) for i in api.state.issues.values()} == {
        "M1-01 — Schema": ("CLOSED", st.DONE),
        "M1-02 — Add entry": ("OPEN", st.IN_PROGRESS),
        "M1-03 — Reverse entry": ("OPEN", st.TODO)}
    assert "- [ ] M1-02 — Add entry — `docs/plans/M1/M1-02-add.md` (tracker: #2)" in lines(p)
    p2 = cd.load_project(p.cfg)
    assert [f.tracker for f in p2.milestones["M1"].features] == [1, 2, 3]
    out.clear()
    assert st.cmd_sync(p2, api, out=out.append, git=on_main) == st.EXIT_OK
    assert out == ["board matches the repo"]


def test_dry_run_writes_nothing(tmp_path):
    p, api, out = make(tmp_path), FakeBoard(), []
    before = lines(p)
    assert st.cmd_sync(p, api, dry_run=True, out=out.append, git=on_main) == st.EXIT_OK
    assert api.calls == [] and lines(p) == before
    assert out[0].startswith("would create_milestone M1 — Ledger")


def test_one_failing_write_does_not_stop_the_rest(tmp_path):
    p, api, out = make(tmp_path), FakeBoard(fail=("rename",)), []
    api.state.milestones["M1 — Ledger"] = "open"
    api.state.issues[7] = st.Issue(7, "M1-03 — Old", "OPEN", [], st.TODO)
    assert st.cmd_sync(p, api, out=out.append, git=on_main) == st.EXIT_USAGE
    assert any("failed" in o and "rename" in o for o in out)
    assert len(api.state.issues) == 3


def test_sync_unreachable_is_exit_2(tmp_path):
    api = FakeBoard(unreachable=True)
    assert st.cmd_sync(make(tmp_path), api, out=lambda s: None, git=on_main) == st.EXIT_UNREACHED


@pytest.mark.parametrize("git,needle", [(off_main, "from main"), (behind_origin, "pull")])
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
    st.cmd_sync(p, api, out=lambda s: None, git=on_main)
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


# --------------------------------------------------------------------------- GhBoard and the CLI, through the fake gh

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


HELD_M1_03 = {"number": 1, "title": "M1-03 — Reverse entry", "state": "OPEN", "assignees": ["alice"],
              "milestone": None, "on_board": True, "status": "In Progress"}


def test_ghboard_reads_and_writes_through_gh(tmp_path):
    p = make(tmp_path)
    d = fake_gh(p.cfg.root, issues=[HELD_M1_03])
    api = st.GhBoard(p.cfg.root, "acme", 1, str(d / "fake_gh.py"))
    b = api.read()
    assert (b.default_branch, b.issues[1].assignees, b.issues[1].status) == ("main", ["alice"], st.IN_PROGRESS)
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


def test_cli_claim_held_then_taken(tmp_path):
    p = make(tmp_path)
    fake_gh(p.cfg.root, issues=[HELD_M1_03])
    r = run_cli(p.cfg.root, "claim", "M1-03")
    assert r.returncode == 3 and "alice" in r.stdout, r.stdout + r.stderr
    r = run_cli(p.cfg.root, "claim", "M1-03", "--take")
    assert r.returncode == 0, r.stdout + r.stderr


def test_cli_without_tracker(tmp_path):
    p = make(tmp_path)
    (p.cfg.root / "docs" / ".check_docs.toml").write_text('tier = "standard"\n', encoding="utf-8")
    assert run_cli(p.cfg.root, "sync").returncode == 0
    r = run_cli(p.cfg.root, "claim", "M1-03")
    assert r.returncode == 1 and "no tracker" in r.stdout

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
    link_last: bool = True   # False when the link sits before the plan path; sync moves it
    create: bool = True      # False in a done milestone: match an existing issue, never create one


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
    default_sha: str = ""      # GitHub's head of the default branch; "" for an empty repository


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
        text = m.path.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
        for f in m.features:
            line = text[f.line - 1].rstrip() if 0 < f.line <= len(text) else ""
            last = f.tracker is None or line.endswith(f"(tracker: #{f.tracker})")
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
            out.append(Want(f.id, f"{f.id} — {f.title}", f"{m.id} — {m.title}", status, f.tracker, reason,
                            link_last=last, create=m.status != "done"))
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
    for title in dict.fromkeys(w.milestone for w in wants if w.status != NOT_PLANNED and w.create):
        if title not in board.milestones:
            changes.append(Change("create_milestone", title))
    for w in wants:
        issue = find_issue(w, board)
        if issue is None:
            if w.status != NOT_PLANNED and w.create:
                changes.append(Change("create_issue", w.fid, w.status))
            continue
        if w.link != issue.number or not w.link_last:
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


# --------------------------------------------------------------------------- applying changes


class Unreachable(Exception):
    """The board cannot be read: gh missing, not logged in, offline, or the project not found."""


class BoardError(Exception):
    """One write to the board failed."""


def apply_changes(changes: list[Change], api, wants: list[Want]) -> tuple[list[str], list[str], dict[str, int]]:
    """Apply each change through `api` (GhBoard, or a fake in tests). One failure does not stop
    the rest. Returns what was applied, what failed, and the links the repo should carry."""
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


FEATURE_LINE_RE = re.compile(r"- (?:\[[ xX]\] |~~)(M\d+-\d+) — ")


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
            hit = FEATURE_LINE_RE.match(body)
            if hit and hit.group(1) in wanted:
                body = cd.TRACKER_LINK_RE.sub("", body).rstrip() + f" (tracker: #{wanted[hit.group(1)]})"
            out.append(body + end)
        new = "".join(out)
        if new != raw:
            m.path.write_bytes(new.encode("utf-8"))
            written.append(m.path)
    return written


# --------------------------------------------------------------------------- commands


def git_runner(root: Path):
    """A git callable for `cmd_sync`: args in, (exit code, stdout) out. Tests pass their own."""
    def run(args: list[str]) -> tuple[int, str]:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        return r.returncode, r.stdout
    return run


def _undoes_done(c: Change, board: BoardState) -> bool:
    """A change that would take a feature back out of Done: reopening its issue, or moving its
    card off Done."""
    if c.kind == "reopen":
        return True
    issue = board.issues.get(c.number) if c.number is not None else None
    return c.kind == "set_status" and issue is not None and issue.status == DONE


def _tree_has_every_merge(git, board: BoardState) -> bool:
    """Whether the checked-out tree contains GitHub's default-branch head, so every merged PR's
    tick is in it. Compared against GitHub's own SHA, not a remote name or a fetch that may fail."""
    if not board.default_sha:
        return True  # an empty repository: nothing has been merged
    return git(["merge-base", "--is-ancestor", board.default_sha, "HEAD"])[0] == 0


def _links(wants: list[Want]) -> list[int]:
    return [w.link for w in wants if w.link is not None]


def _read(api, links: list[int], out) -> tuple[BoardState | None, int]:
    """Read the board, or say why not: exit 2 when it cannot be reached (gh missing, offline,
    not logged in), exit 1 when it answers wrong (no such project, no Status field, odd output)."""
    try:
        return api.read(links), EXIT_OK
    except Unreachable as e:
        out(f"board not reached: {e}")
        return None, EXIT_UNREACHED
    except BoardError as e:
        out(f"board not read: {e}. Check [tracker] in docs/.check_docs.toml and the gh token's project scope.")
        return None, EXIT_USAGE


def cmd_sync(project: cd.Project, api, dry_run: bool = False, out=print, git=None) -> int:
    wants = wants_from(project)
    board, code = _read(api, _links(wants), out)
    if board is None:
        return code
    changes = plan_changes(wants, board)
    if not changes:
        out("board matches the repo")
        return EXIT_OK
    if dry_run:
        for c in changes:
            out(f"would {describe(c)}")
        return EXIT_OK
    skipped: list[Change] = []
    if not _tree_has_every_merge(git or git_runner(project.cfg.root), board):
        # A tree without every merge sees merged features as unticked; it must not undo their Done.
        skipped = [c for c in changes if _undoes_done(c, board)]
        changes = [c for c in changes if c not in skipped]
    applied, failed, links = apply_changes(changes, api, wants)
    written = write_links(project, links)
    for line in applied + failed:
        out(line)
    for c in skipped:
        out(f"skipped {describe(c)}: this tree lacks merges on {board.default_branch or 'the default branch'}; "
            "sync from an up-to-date default branch to apply it")
    out(f"{len(applied)} applied, {len(failed)} failed, {len(skipped)} skipped, "
        f"links written in {len(written)} file(s)")
    return EXIT_USAGE if failed else EXIT_OK


def cmd_check(project: cd.Project, api, out=print) -> int:
    wants = wants_from(project)
    board, code = _read(api, _links(wants), out)
    if board is None:
        return code
    drift = [describe(c) for c in plan_changes(wants, board)]
    for w in wants:
        dupes = sorted(n for n, i in board.issues.items() if i.title.startswith(f"{w.fid} — "))
        if len(dupes) > 1:
            drift.append(f"duplicate issues for {w.fid}: " + ", ".join(f"#{n}" for n in dupes))
    by_link: dict[int, list[str]] = {}
    for w in wants:
        if w.link is not None:
            by_link.setdefault(w.link, []).append(w.fid)
    for n, fids in by_link.items():
        if len(fids) > 1:  # sync would rename the one issue back and forth on every run
            drift.append(f"shared link #{n}: " + ", ".join(fids) + "; give each feature its own issue")
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
    board, code = _read(api, _links([want]), out)
    if board is None:
        if code == EXIT_UNREACHED:
            out("Claim in the repo and say so under Needs from you.")
        return code
    issue = find_issue(want, board)
    try:
        me = api.whoami()
        if release:
            if issue and me in issue.assignees:
                api.unassign(issue.number, me)
                if not [a for a in issue.assignees if a != me]:
                    api.set_status(issue.number, TODO)  # only when nobody else still holds it
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
        after = api.read([issue.number])
    except Unreachable as e:
        out(f"board not reached: {e}. Claim in the repo and say so under Needs from you.")
        return EXIT_UNREACHED
    except BoardError as e:  # a refusal (no rights, no such project) is not an outage: stop and report it
        out(f"board write failed: {e}. The claim is not made; stop and report it.")
        return EXIT_USAGE
    # A rival may hold this issue, or a second issue for the same feature that someone created
    # at the same moment because neither of you found one.
    mine = [after.issues[issue.number]] if issue.number in after.issues else []
    same = mine + [i for n, i in after.issues.items() if n != issue.number and i.title.startswith(f"{fid} — ")]
    rivals = sorted({a for i in same for a in i.assignees if a != me})
    if rivals:
        out(f"{fid} is also claimed by {', '.join(rivals)} (#{issue.number}), at the same moment as "
            "you. Stop and let a human decide who keeps it.")
        return EXIT_HELD
    out(f"claimed {fid} (#{issue.number}) for {me}")
    return EXIT_OK


# --------------------------------------------------------------------------- GitHub, through gh

LIST_LIMIT = "10000"  # gh pages through internally; linked issues past it are fetched one by one
ISSUE_FIELDS = "number,title,state,assignees,milestone"
ISSUE_BODY = ("Mirrored from this repository's milestone files by tools/sync_tracker.py. The "
              "repository is the source of status: a card moved by hand is moved back on the next sync.")


class GhBoard:
    """The board, through the gh CLI. The only code in the kit that talks to GitHub."""

    def __init__(self, root: Path, owner: str, project: int, gh: str = "gh", run=None):
        self.root, self.owner, self.project, self.gh = Path(root), owner, project, gh
        self._run = run or self._subprocess
        self._repo = ""                        # owner/name of the checked-out repository
        self._project_id = ""
        self._field = ""
        self._options: dict[str, str] = {}     # status name -> option id
        self._items: dict[int, str] = {}       # issue number -> project item id
        self._milestones: dict[str, int] = {}  # milestone title -> number

    def _subprocess(self, args: list[str]) -> tuple[int, str, str]:
        cmd = [sys.executable, self.gh] if self.gh.endswith(".py") else [self.gh]
        try:
            r = subprocess.run(cmd + args, cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            raise Unreachable(f"{self.gh} not found; install the GitHub CLI and run gh auth login")
        return r.returncode, r.stdout, r.stderr

    @staticmethod
    def _first_line(code: int, out: str, err: str) -> str:
        return ((err or out).strip().splitlines() or [f"gh exited {code}"])[0]

    def _gh(self, *args: str) -> str:
        code, out, err = self._run(list(args))
        if code != 0:
            raise BoardError(self._first_line(code, out, err))
        return out

    @staticmethod
    def _parsed(what: str, parse):
        """`parse()`, with output gh was not expected to give turned into a BoardError."""
        try:
            return parse()
        except (ValueError, KeyError, TypeError, IndexError, AttributeError) as e:
            raise BoardError(f"unexpected gh output for {what}: {type(e).__name__}: {e}")

    def _json(self, *args: str):
        out = self._gh(*args)
        return self._parsed(" ".join(args[:2]), lambda: json.loads(out or "null"))

    def read(self, links=()) -> BoardState:
        """The board. `links` are issue numbers the repo cites: any the issue list did not
        return (a repository past the list limit) are fetched one by one. Only a failed login
        check is Unreachable (offline, logged out); any later failure is the board answering
        wrong — no such project, no Status field — and is a BoardError."""
        code, out, err = self._run(["auth", "status", "--hostname", "github.com"])
        if code != 0:
            raise Unreachable(self._first_line(code, out, err))
        return self._parsed("the board", lambda: self._read_board(links))

    def _read_board(self, links) -> BoardState:
        repo = self._json("repo", "view", "--json", "nameWithOwner,defaultBranchRef")
        self._repo = repo["nameWithOwner"]
        p, o = str(self.project), self.owner
        self._project_id = self._json("project", "view", p, "--owner", o, "--format", "json")["id"]
        fields = self._json("project", "field-list", p, "--owner", o, "--format", "json")["fields"]
        status = next((f for f in fields if f.get("name") == "Status"), None)
        if status is None:
            raise BoardError(f"project {p} has no Status field")
        self._field = status["id"]
        self._options = {x["name"]: x["id"] for x in status.get("options", [])}
        on_board: dict[int, str] = {}
        for it in self._json("project", "item-list", p, "--owner", o, "--format", "json", "--limit", LIST_LIMIT)["items"]:
            c = it.get("content") or {}
            if c.get("type") == "Issue" and c.get("repository") == self._repo:
                self._items[c["number"]] = it["id"]
                on_board[c["number"]] = it.get("status") or ""
        default = (repo.get("defaultBranchRef") or {}).get("name", "")
        state = BoardState(default_branch=default)
        if default:
            state.default_sha = self._gh("api", f"repos/{self._repo}/commits/{default}", "--jq", ".sha").strip()

        def add(raw: dict) -> None:
            n = raw["number"]
            state.issues[n] = Issue(n, raw["title"], raw["state"],
                                    [a["login"] for a in raw.get("assignees") or []],
                                    on_board.get(n), (raw.get("milestone") or {}).get("title"))

        for raw in self._json("issue", "list", "--state", "all", "--limit", LIST_LIMIT, "--json", ISSUE_FIELDS):
            add(raw)
        for n in links:
            if n not in state.issues:
                code, out, _ = self._run(["issue", "view", str(n), "--json", ISSUE_FIELDS])
                if code == 0:  # a link to a deleted or transferred issue is simply not there
                    add(json.loads(out))
        listing = self._gh("api", "--paginate", f"repos/{self._repo}/milestones?state=all&per_page=100",
                           "--jq", ".[] | {title, state, number}")
        for row in listing.splitlines():
            if row.strip():
                ms = json.loads(row)
                state.milestones[ms["title"]] = ms["state"]
                self._milestones[ms["title"]] = ms["number"]
        return state

    def whoami(self) -> str:
        return self._gh("api", "user", "--jq", ".login").strip()

    def create_milestone(self, title: str) -> None:
        out = self._gh("api", f"repos/{self._repo}/milestones", "-f", f"title={title}")
        self._milestones[title] = self._parsed("milestone create", lambda: json.loads(out)["number"])

    def close_milestone(self, title: str) -> None:
        if title not in self._milestones:
            raise BoardError(f"no GitHub milestone named {title!r}")
        self._gh("api", "-X", "PATCH", f"repos/{self._repo}/milestones/{self._milestones[title]}",
                 "-f", "state=closed")

    def create_issue(self, title: str, milestone: str) -> int:
        out = self._gh("issue", "create", "--title", title, "--milestone", milestone, "--body", ISSUE_BODY)
        return self._parsed("issue create", lambda: int(out.strip().rsplit("/", 1)[-1]))

    def rename(self, n: int, title: str) -> None:
        self._gh("issue", "edit", str(n), "--title", title)

    def add_to_project(self, n: int) -> None:
        out = self._gh("project", "item-add", str(self.project), "--owner", self.owner,
                       "--url", f"https://github.com/{self._repo}/issues/{n}", "--format", "json")
        self._items[n] = self._parsed("project item-add", lambda: json.loads(out)["id"])

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


# --------------------------------------------------------------------------- command line


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mirror milestones and features onto a GitHub Project.")
    ap.add_argument("--root", default=".", help="project root (default: current directory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="make the board match the repo; writes from the default branch only")
    s.add_argument("--dry-run", action="store_true", help="print the changes, apply none")
    sub.add_parser("check", help="list where the board and the repo disagree")
    c = sub.add_parser("claim", help="the claim lock: assign the feature's issue and move it to In Progress")
    c.add_argument("feature", help="a feature ID, M<n>-<nn>")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--take", action="store_true", help="reassign a held feature (a human said so)")
    g.add_argument("--release", action="store_true", help="give up a claim abandoned without Close")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # a console that cannot show a title gets "?" rather than a traceback
        sys.stdout.reconfigure(errors="replace")
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

#!/usr/bin/env python3
"""sync_tracker — mirror a bootstrap-kit project's milestones and features onto a GitHub Project.

Usage: sync_tracker.py [--root PATH] sync [--dry-run] | check | claim <feature-id> [--take | --release]

The repo is the source of status; the board is a mirror plus the claim lock. Nothing read from
the board is written into the repo except the `(tracker: #N)` link that `sync` puts last on a
feature line. Exit: 0 ok; 1 usage error, a failed write, or drift found by `check`; 2 board not
reached; 3 claim held by someone else.
"""
from __future__ import annotations

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


def _branch_problem(git, default: str) -> str | None:
    """Why `sync` must not write from here: it sees only the checked-out tree, so a feature
    branch or a stale default branch would reopen issues that a merged PR already closed."""
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

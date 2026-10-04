#!/usr/bin/env python3
"""sync_tracker — mirror a bootstrap-kit project's milestones and features onto a GitHub Project.

Usage: sync_tracker.py [--root PATH] sync [--dry-run] | check | claim <feature-id> [--take | --release]

The repo is the source of status; the board is a mirror plus the claim lock. Nothing read from
the board is written into the repo except the `(tracker: #N)` link that `sync` puts last on a
feature line. Exit: 0 ok; 1 usage error, a failed write, or drift found by `check`; 2 board not
reached; 3 claim held by someone else.
"""
from __future__ import annotations

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

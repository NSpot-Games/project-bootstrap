#!/usr/bin/env python3
"""Behavioural evals for the project-bootstrap skill: one bootstrap step per scenario, run by
an agent against a synthetic fixture repository, graded by the linter and by file checks.

    python evals/harness.py prepare <scenario|all> <runs_dir> [--label with_skill] [--skill PATH]
    python evals/harness.py grade   <scenario|all> <runs_dir> [--label with_skill]
    python evals/harness.py report  <runs_dir>

`prepare` copies the fixture to <runs_dir>/<scenario>/<label>/project/, applies the scenario's
setup (git history, a copy of the linter) and writes prompt.md — the full prompt to hand to an
agent. The agent works inside project/ and writes project/final_message.md before it stops.
`grade` evaluates every assertion in evals.json against project/ and writes grading.json.
`report` prints one table across scenarios and labels.

Standard library only; Python 3.11+.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EVALS = HERE / "evals.json"
FIXTURES = HERE / "fixtures"
DEFAULT_SKILL = ROOT / "skills" / "project-bootstrap"
LINTER = DEFAULT_SKILL / "scripts" / "check_docs.py"
PRE_BOOTSTRAP_MSG = "pre-bootstrap: the repository as it was before the docs-as-contract bootstrap"

PROMPT = """You are exercising the project-bootstrap skill exactly as an agent would use it.

Skill: read `{skill}/SKILL.md` first and follow it. Its references, templates and scripts live
under `{skill}/`. Never modify anything under `{skill}`.

Project: `{project}`. Work only inside this directory; it is a scratch copy and nothing
outside it matters. Paths the skill writes as `<project>/...` mean this directory.

Task: {task}

The user is not available. Every answer they would give is stated above. If the procedure
requires a human reply that is not given above, stop at that point. Before you finish, write
`{project}/final_message.md` containing exactly the message you would post to the user at the
point you stopped, and nothing else. Then reply with a short report: which SKILL.md sections you
followed, which files you wrote, and where you stopped and why.
"""


def load_evals() -> dict:
    return json.loads(EVALS.read_text(encoding="utf-8"))


def scenario(name: str) -> dict:
    for e in load_evals()["evals"]:
        if e["name"] == name:
            return e
    sys.exit(f"no scenario named {name!r}; known: {', '.join(x['name'] for x in load_evals()['evals'])}")


def run_dir(runs: Path, name: str, label: str) -> Path:
    return runs / name / label


# ------------------------------------------------------------------------------ prepare


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def _rmtree(path: Path) -> None:
    """rmtree that copes with read-only files, which git's object store is made of on Windows."""
    import os
    import stat

    def _force(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_force)
    else:
        shutil.rmtree(path, onerror=_force)


def prepare(name: str, runs: Path, label: str, skill: Path) -> Path:
    ev = scenario(name)
    rd = run_dir(runs, name, label)
    if rd.exists():
        _rmtree(rd)
    project = rd / "project"
    shutil.copytree(FIXTURES / ev["fixture"], project)
    setup = ev.get("setup", {})
    if setup.get("copy_linter"):
        (project / "tools").mkdir(exist_ok=True)
        shutil.copy(LINTER, project / "tools" / "check_docs.py")
    if setup.get("git"):
        git(project, "init", "-q", "-b", "main")
        git(project, "config", "user.email", "fixture@example.invalid")
        git(project, "config", "user.name", "Fixture")
        git(project, "add", "-A")
        git(project, "commit", "-q", "-m", PRE_BOOTSTRAP_MSG)
        sha = git(project, "rev-parse", "HEAD").stdout.strip()
        (rd / "pre_bootstrap_sha.txt").write_text(sha + "\n", encoding="utf-8")
    data = load_evals()
    task = ev["prompt"].format(answers=data["answers"], brainstorm=data["brainstorm"])
    prompt = PROMPT.format(skill=skill.resolve().as_posix(), project=project.resolve().as_posix(), task=task)
    (rd / "prompt.md").write_text(prompt, encoding="utf-8", newline="\n")
    (rd / "eval_metadata.json").write_text(json.dumps({
        "eval_id": ev["id"], "eval_name": name, "label": label, "skill": skill.resolve().as_posix(),
        "prompt": task, "assertions": [a["text"] for a in ev["assertions"]],
    }, indent=2), encoding="utf-8", newline="\n")
    return rd


# ------------------------------------------------------------------------------ grade


def _files(project: Path, glob: str, exclude: str | None = None) -> list[Path]:
    out = []
    for p in sorted(project.glob(glob)):
        if not p.is_file():
            continue
        r = p.relative_to(project).as_posix()
        if r.startswith(".git/") or (exclude and r.startswith(exclude)):
            continue
        out.append(p)
    return out


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8").replace("\r\n", "\n")
    except (UnicodeDecodeError, OSError):
        return ""


def _lint(project: Path) -> tuple[list[str], int]:
    r = subprocess.run([sys.executable, str(LINTER), "--root", str(project)], capture_output=True, text=True)
    lines = (r.stdout + r.stderr).strip().splitlines()
    codes = [m.group(1) for ln in lines for m in [re.search(r": ([EW]\d{3}) ", ln)] if m]
    return lines, sum(1 for c in codes if c.startswith("E"))


def check(a: dict, project: Path, rd: Path, ev: dict) -> tuple[bool, str]:
    kind = a["check"]
    if kind == "file_exists":
        ok = (project / a["path"]).is_file()
        return ok, f"{a['path']} {'exists' if ok else 'missing'}"
    if kind == "files_exist":
        missing = [p for p in a["paths"] if not (project / p).is_file()]
        return not missing, ("all present" if not missing else "missing: " + ", ".join(missing))
    if kind == "file_absent":
        ok = not (project / a["path"]).exists()
        return ok, f"{a['path']} {'absent' if ok else 'present'}"
    if kind == "grep":
        p = project / a["path"]
        if not p.is_file():
            return False, f"{a['path']} missing"
        m = re.search(a["pattern"], _read(p))
        return bool(m), (f"matched: {m.group(0)[:80]!r}" if m else "no match")
    if kind == "not_grep":
        p = project / a["path"]
        if not p.is_file():
            return True, f"{a['path']} absent (nothing to violate)"
        m = re.search(a["pattern"], _read(p))
        return not m, (f"found: {m.group(0)[:80]!r}" if m else "no match, as required")
    if kind == "grep_any":
        hits = [p for p in _files(project, a["glob"], a.get("exclude")) if re.search(a["pattern"], _read(p))]
        hits += [p for p in [project / "final_message.md"] if p.is_file() and re.search(a["pattern"], _read(p)) and p not in hits]
        return bool(hits), ("in " + ", ".join(h.relative_to(project).as_posix() for h in hits[:3])) if hits else "no file matches"
    if kind == "mentions_each":
        texts = {p.relative_to(project).as_posix(): _read(p) for p in _files(project, "**/*.md", a.get("exclude"))}
        missing = [n for n in a["names"] if not any(n in t for t in texts.values())]
        return not missing, ("all named" if not missing else "not named: " + ", ".join(missing))
    if kind == "unchanged":
        fixture = FIXTURES / ev["fixture"]
        changed = [p.relative_to(project).as_posix() for p in _files(project, a["glob"])
                   if _read(p) != _read(fixture / p.relative_to(project))]
        missing = [p.relative_to(fixture).as_posix() for p in fixture.glob(a["glob"]) if not (project / p.relative_to(fixture)).is_file()]
        bad = changed + [m + " (deleted)" for m in missing]
        return not bad, ("unchanged" if not bad else "changed: " + ", ".join(bad))
    if kind == "count_glob":
        n = len(_files(project, a["glob"]))
        ok = a.get("min", 0) <= n <= a.get("max", 10**9)
        return ok, f"{n} file(s) match {a['glob']}"
    if kind == "no_tokens":
        bad = [p.relative_to(project).as_posix() for p in _files(project, a["glob"], a.get("exclude")) if "{{" in _read(p)]
        return not bad, ("no tokens left" if not bad else "tokens in: " + ", ".join(bad[:5]))
    if kind == "lint":
        lines, n_err = _lint(project)
        if "max_errors" in a:
            ok = n_err <= a["max_errors"]
            return ok, (f"{n_err} error(s)" + ("" if ok else ": " + "; ".join(lines[:4])))
        present = [c for c in a["absent_codes"] if any(f" {c} " in ln for ln in lines)]
        return not present, ("none of the codes present" if not present else "present: " + ", ".join(present))
    if kind == "git_branch_prefix":
        b = git(project, "branch", "--show-current").stdout.strip()
        return b.startswith(a["prefix"]), f"branch {b!r}"
    if kind == "git_commits_min":
        n = len(git(project, "rev-list", "--all").stdout.split())
        return n >= a["n"], f"{n} commit(s)"
    if kind == "git_clean":
        s = git(project, "status", "--porcelain").stdout.strip()
        s = "\n".join(ln for ln in s.splitlines() if "final_message.md" not in ln)
        return not s, ("clean" if not s else "dirty: " + s.splitlines()[0])
    if kind == "sha_recorded":
        sha_file = rd / "pre_bootstrap_sha.txt"
        if not sha_file.is_file():
            return False, "no pre-bootstrap SHA recorded by setup"
        sha = sha_file.read_text(encoding="utf-8").strip()
        short = sha[:7]
        in_docs = [p.relative_to(project).as_posix() for p in _files(project, "**/*") if p.suffix in (".md", ".txt", ".toml") and short in _read(p)]
        in_log = short in git(project, "log", "--all", "--format=%B").stdout
        ok = bool(in_docs) or in_log
        return ok, (f"SHA {short} in " + (", ".join(in_docs[:3]) if in_docs else "a commit message")) if ok else f"SHA {short} not recorded anywhere"
    if kind in ("final_contains", "final_not_contains"):
        p = project / "final_message.md"
        if not p.is_file():
            return False, "final_message.md missing"
        m = re.search(a["pattern"], _read(p))
        if kind == "final_contains":
            return bool(m), (f"matched: {m.group(0)[:80]!r}" if m else "no match")
        return not m, (f"found: {m.group(0)[:80]!r}" if m else "absent, as required")
    return False, f"unknown check {kind!r}"


def grade(name: str, runs: Path, label: str) -> dict:
    ev = scenario(name)
    rd = run_dir(runs, name, label)
    project = rd / "project"
    if not project.is_dir():
        sys.exit(f"{project} does not exist; run prepare first")
    results = []
    for a in ev["assertions"]:
        passed, evidence = check(a, project, rd, ev)
        results.append({"text": a["text"], "passed": passed, "evidence": evidence})
    out = {"eval_name": name, "label": label, "expectations": results,
           "pass_rate": sum(r["passed"] for r in results) / len(results)}
    (rd / "grading.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    return out


# ------------------------------------------------------------------------------ report


def report(runs: Path) -> str:
    rows = []
    for g in sorted(runs.glob("*/*/grading.json")):
        d = json.loads(g.read_text(encoding="utf-8"))
        timing = g.parent / "timing.json"
        t = json.loads(timing.read_text(encoding="utf-8")) if timing.is_file() else {}
        rows.append((d["eval_name"], d["label"], d["pass_rate"], len(d["expectations"]), t.get("total_tokens"), t.get("duration_ms")))
    lines = ["| Scenario | Label | Pass rate | Assertions | Tokens | Seconds |", "|---|---|---|---|---|---|"]
    for name, label, rate, n, tok, ms in rows:
        lines.append(f"| {name} | {label} | {rate:.0%} | {n} | {tok if tok is not None else '—'} | {ms / 1000:.0f} |" if ms else
                     f"| {name} | {label} | {rate:.0%} | {n} | {tok if tok is not None else '—'} | — |")
    detail = []
    for g in sorted(runs.glob("*/*/grading.json")):
        d = json.loads(g.read_text(encoding="utf-8"))
        detail.append(f"\n### {d['eval_name']} — {d['label']}\n")
        for r in d["expectations"]:
            detail.append(f"- {'PASS' if r['passed'] else 'FAIL'} — {r['text']} — {r['evidence']}")
    return "\n".join(lines + detail) + "\n"


# ------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare"); p.add_argument("scenario"); p.add_argument("runs"); p.add_argument("--label", default="with_skill"); p.add_argument("--skill", default=str(DEFAULT_SKILL))
    g = sub.add_parser("grade"); g.add_argument("scenario"); g.add_argument("runs"); g.add_argument("--label", default="with_skill")
    r = sub.add_parser("report"); r.add_argument("runs")
    args = ap.parse_args(argv)
    names = [e["name"] for e in load_evals()["evals"]] if getattr(args, "scenario", None) == "all" else [getattr(args, "scenario", None)]
    if args.cmd == "prepare":
        for n in names:
            rd = prepare(n, Path(args.runs), args.label, Path(args.skill))
            print(f"prepared {rd / 'prompt.md'}")
    elif args.cmd == "grade":
        for n in names:
            out = grade(n, Path(args.runs), args.label)
            print(f"{n} [{args.label}]: {out['pass_rate']:.0%} ({sum(r['passed'] for r in out['expectations'])}/{len(out['expectations'])})")
    else:
        print(report(Path(args.runs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

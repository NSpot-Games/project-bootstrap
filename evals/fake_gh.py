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


def as_json(i):
    return {"number": i["number"], "title": i["title"], "state": i["state"],
            "assignees": [{"login": x} for x in i["assignees"]],
            "milestone": {"title": i["milestone"]} if i.get("milestone") else None}


def handle(st, a):
    if st.get("offline"):
        return None, "error connecting to api.github.com", 1

    def issue(n):
        return next(i for i in st["issues"] if i["number"] == int(n))

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
        items = [{"id": f"I_{i['number']}",
                  "content": {"type": "Issue", "number": i["number"], "repository": st["repo"]},
                  **({"status": i["status"]} if i.get("status") else {})}
                 for i in st["issues"] if i.get("on_board")]
        return {"items": items}, "", 0
    if a[:2] == ["issue", "list"]:  # an issue marked "hidden" stands for one past gh's list limit
        return [as_json(i) for i in st["issues"] if not i.get("hidden")], "", 0
    if a[:2] == ["issue", "view"]:
        found = [i for i in st["issues"] if i["number"] == int(a[2])]
        if not found:
            return None, f"GraphQL: Could not resolve to an issue with the number of {a[2]}.", 1
        return as_json(found[0]), "", 0
    if a[:2] == ["api", "user"]:
        return st["me"] + "\n", "", 0
    if a[0] == "api":
        path = next(x for x in a[1:] if x.startswith("repos/"))
        if "/commits/" in path:
            return st.get("head", "") + "\n", "", 0
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
        if "--jq" in a:  # `--paginate --jq '.[] | ...'`: one object per line, across every page
            return "".join(json.dumps(m) + "\n" for m in st["milestones"]), "", 0
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

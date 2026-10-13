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


def _assertion(scenario, text):
    ev = next(e for e in harness.load_evals()["evals"] if e["name"] == scenario)
    return next(a for a in ev["assertions"] if a["text"] == text)


@pytest.mark.parametrize("scenario,text,message,expected", [
    ("raw-idea", "Exactly one question is asked", "Which is it for?)", True),
    ("nothing-new", "At least two angles are offered", "**A)** Stories that vanish\nB) Photos only of food\n", True),
    ("nothing-new", "At least two angles are offered", "**A)** Stories that vanish\n", False),
    ("nothing-new", "The message says plainly that it already exists", "Instagram already does this.", True),
    ("handoff", "No code or stack is started", "No tech stack is chosen yet; project-bootstrap scaffolds the docs.", True),
    ("handoff", "No code or stack is started", "Next: npm install and we'll use Postgres.", False),
    ("raw-idea", "The message names what is new about the idea",
     "What is new here is that the story only moves when you reply in the language.", True),
    ("raw-idea", "The question is about purpose",
     "What is it for: a side project, a commercial app, or a learning project?", True),
    ("raw-idea", "The message does not declare the idea a copy",
     "What is new here is that the story only moves when you reply in the language.", True),
    ("raw-idea", "The message names what is new about the idea",
     "This already exists: it is Streaks. So the idea is not yet new.\n\nThree angles to pick from:", False),
    ("raw-idea", "The message does not declare the idea a copy",
     "This already exists: it is Streaks. So the idea is not yet new.\n\nThree angles to pick from:", False),
    ("raw-idea", "Exactly one question is asked",
     'People post "anyone got a ladder?"\nWhich angle, or one of your own?\n', True),
    ("tech-drift", "At most one question is asked",
     "Back to the open question: how do people find it?\nWhich one?\n", False),
])
def test_scenario_patterns_match_intended_text(tmp_path, scenario, text, message, expected):
    (tmp_path / "final_message.md").write_text(message, encoding="utf-8")
    ok, evidence = harness.check(_assertion(scenario, text), tmp_path / "project", tmp_path, {})
    assert ok is expected, evidence


def test_grep_reads_a_file_written_in_a_windows_code_page(tmp_path):
    project = tmp_path / "project"
    (project / "docs").mkdir(parents=True)
    (project / "docs" / "alt.md").write_bytes("**Chosen: C — a request board**\n".encode("cp1252"))
    ok, evidence = harness.check({"check": "grep", "path": "docs/alt.md", "pattern": r"(?i)chosen[^\n]{0,80}request board"},
                                 project, tmp_path, {})
    assert ok, evidence

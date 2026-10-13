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

"""Agreement between what the kit's documents say and what its code does. Each test here
guards a class of drift that a prose rule alone cannot: a tier the linter cannot see, a token
the table does not explain, a finding code the references cite but the linter never emits."""
import re
from pathlib import Path

import check_docs as cd

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "project-bootstrap"
REFERENCES = SKILL_DIR / "references"
TEMPLATES = SKILL_DIR / "assets" / "templates"
DOC_FILES = [SKILL_DIR / "SKILL.md", ROOT / "BOOTSTRAP.md", ROOT / "README.md",
             SKILL_DIR / "scripts" / "hooks" / "README.md",
             *sorted(REFERENCES.rglob("*.md")), *sorted(TEMPLATES.glob("*.md"))]


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def _section(text: str, number: int) -> str:
    m = re.search(rf"^## {number}\. .*?$\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert m, f"no section {number}"
    return m.group(1)


def test_tier_table_names_exactly_the_tiers_the_linter_returns():
    table = _section(_text(REFERENCES / "core" / "tiers.md"), 1)
    rows = [ln for ln in table.splitlines()
            if ln.startswith("| ") and not ln.startswith("| Tier") and not ln.startswith("|---")]
    named = {ln.split("|")[1].strip().lower() for ln in rows}
    assert named == set(cd.TIERS), named ^ set(cd.TIERS)


def test_every_template_token_is_in_the_token_table():
    table = _text(TEMPLATES / "README.md")
    documented = set(re.findall(r"`(\{\{[^}]+\}\})`", table))
    used = set()
    for p in TEMPLATES.glob("*.md"):
        if p.name == "README.md":
            continue
        used |= set(re.findall(r"\{\{[^}]+\}\}", _text(p)))
    assert used <= documented, used - documented


def test_every_finding_code_cited_in_the_docs_exists_in_the_linter():
    cited = set()
    for p in DOC_FILES:
        cited |= set(re.findall(r"\b([EW]\d{3})\b", _text(p)))
    assert cited <= set(cd.CODES), cited - set(cd.CODES)


def test_milestone_template_feature_line_carries_no_plan_path():
    text = _text(TEMPLATES / "milestone.md")
    feature_lines = [ln for ln in text.splitlines() if ln.startswith("- [ ]")]
    assert feature_lines, "milestone template has no feature line"
    assert not any("docs/plans/" in ln for ln in feature_lines), feature_lines


def test_hooks_readme_snippet_matches_the_shipped_project_hook():
    readme = _text(SKILL_DIR / "scripts" / "hooks" / "README.md")
    snippet = re.search(r"```sh\n(#!/bin/sh\n.*?)```", readme, re.S).group(1)
    assert snippet == _text(SKILL_DIR / "scripts" / "hooks" / "stop.sh")


def _fenced_block_after(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}[ \t]*$\n```markdown\n(.*?)```", text, re.M | re.S)
    assert m, f"no fenced block under '{heading}'"
    return m.group(1)


def test_workflow_template_embeds_the_plan_and_milestone_templates_verbatim():
    workflow = _text(TEMPLATES / "WORKFLOW.md")
    assert _fenced_block_after(workflow, "7. Plan template") == _text(TEMPLATES / "plan.md")
    assert _fenced_block_after(workflow, "8. Milestone template") == _text(TEMPLATES / "milestone.md")


def test_no_profile_outline_ends_a_design_doc_with_an_open_questions_section():
    """lessons.md lesson 5: one open-questions file. An outline that lists 'open questions' as a
    section makes every project scatter them again; the only allowed mention is the pointer."""
    for p in sorted((REFERENCES / "profiles").glob("*.md")):
        if p.name == "README.md":
            continue
        for line in _section(_text(p), 2).splitlines():
            if not line.startswith("| `"):
                continue
            outline = line.split("|")[2].lower()
            for part in outline.split(";"):
                if "open questions" in part:
                    assert "OPEN-QUESTIONS.md" in line, (p.name, part.strip())

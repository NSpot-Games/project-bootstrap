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


def test_workflow_template_points_at_the_object_templates_and_carries_no_tokens():
    workflow = _text(TEMPLATES / "WORKFLOW.md")
    assert "tools/templates/plan.md" in workflow
    assert "tools/templates/plan-lite.md" in workflow
    assert "tools/templates/milestone.md" in workflow
    assert "{{" not in workflow, "format hints in WORKFLOW.md are angle-bracketed, never tokens"


def test_token_table_lists_exactly_the_tokens_the_templates_use():
    table = _text(TEMPLATES / "README.md")
    documented = set(re.findall(r"`(\{\{[^}]+\}\})`", table))
    used = set()
    for p in TEMPLATES.glob("*.md"):
        if p.name == "README.md":
            continue
        used |= set(re.findall(r"\{\{[^}]+\}\}", _text(p)))
    assert documented == used, documented ^ used


def test_config_template_documents_every_linter_key():
    import dataclasses
    import tomllib
    keys = {f.name for f in dataclasses.fields(cd.Config)} - {"root", "config_error"}
    text = _text(TEMPLATES / "check_docs.toml")
    mentioned = set(re.findall(r"^#?\s*([a-z_]+)\s*=", text, re.M))
    assert keys <= mentioned, keys - mentioned
    active = tomllib.loads(text)
    assert set(active) <= keys, set(active) - keys


def test_gitattributes_template_pins_lf():
    text = _text(TEMPLATES / "gitattributes")
    assert "* text=auto eol=lf" in text and "*.sh text eol=lf" in text


def test_every_profile_has_the_seven_sections_and_is_indexed():
    readme = _text(REFERENCES / "profiles" / "README.md")
    for p in sorted((REFERENCES / "profiles").glob("*.md")):
        if p.name == "README.md":
            continue
        heads = re.findall(r"^## (\d+)\. ", _text(p), re.M)
        assert heads == [str(i) for i in range(1, 8)], (p.name, heads)
        assert f"references/profiles/{p.name}" in _section(readme, 1), p.name
        assert f"references/profiles/{p.name}" in _section(readme, 4), p.name


def test_skill_routing_sends_every_path_through_the_setup_questions():
    """The first acceptance run found docs-first routed past §2, whose answers §6a and §3(b)
    depend on. The routing sentence must name §1a and §2 for every path."""
    text = _text(SKILL_DIR / "SKILL.md")
    routing = _section(text, 1)
    assert "Every path runs §1a and §2 first" in routing


def test_no_profile_outline_mentions_open_questions_at_all():
    """doc-kinds §3 mandates the Decisions section and the open-questions pointer at the end of
    every design doc; an outline that lists either invites a second, mispositioned copy."""
    for p in sorted((REFERENCES / "profiles").glob("*.md")):
        if p.name == "README.md":
            continue
        for line in _section(_text(p), 2).splitlines():
            if line.startswith("| `"):
                assert "open questions" not in line.lower(), (p.name, line[:60])
                assert "OPEN-QUESTIONS" not in line, (p.name, line[:60])


def test_curated_directory_writes_its_own_architecture_doc():
    text = _section(_text(REFERENCES / "profiles" / "curated-directory.md"), 2)
    assert "`<project>/docs/design/architecture.md`" in text


def test_docs_map_template_uses_the_adoption_classes():
    """The second real-repository run found the map template and the adoption reference naming
    different classes for pre-bootstrap documents; one vocabulary, in both places."""
    template = _section(_text(TEMPLATES / "DOCS.md"), 1)
    adoption = _section(_text(REFERENCES / "core" / "adoption.md"), 4)
    for cls in ("*contract*", "*history*", "*external reference*"):
        assert cls in template, cls
        assert cls in adoption, cls
    assert "*research*" not in template


def test_plan_templates_carry_the_orchestrator_sections():
    full = (TEMPLATES / "plan.md").read_text(encoding="utf-8")
    lite = (TEMPLATES / "plan-lite.md").read_text(encoding="utf-8")
    for heading in ("## Done when", "## Stop and ask if", "## Tasks", "## Sessions", "## Progress notes"):
        assert heading in full and heading in lite, heading
    assert "### Tests this feature adds" in full
    assert "**Shape:** lite" in lite and "**Shape:**" not in full
    assert "## Approach" not in lite


def test_project_templates_carry_the_economy_rules_without_citing_the_kit():
    workflow = (TEMPLATES / "WORKFLOW.md").read_text(encoding="utf-8")
    agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
    assert "tools/templates/plan-lite.md" in workflow
    assert "## 5b. Plan-lite" in workflow and "## 3a. Working for a human" in workflow
    assert "Needs from you" in workflow
    assert "## Stopping rules" in agents and "Stop and ask before" in agents
    assert "`check`" in agents
    for text in (workflow, agents):
        assert "references/" not in text
    assert len(agents.rstrip("\n").split("\n")) < 120


def test_every_architecture_row_names_the_ci_budget():
    for p in sorted((SKILL_DIR / "references" / "profiles").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        row = next((ln for ln in text.splitlines() if ln.startswith("| `<project>/docs/design/architecture.md`")), None)
        if row is None:
            continue  # research-prototype writes no architecture doc
        assert "CI budget (`references/core/economy.md §3`)" in row, p.name

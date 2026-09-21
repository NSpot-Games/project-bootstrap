"""Checks that skills/project-bootstrap/ is a valid, self-contained Agent Skill and that the
Claude plugin manifests agree with it."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "project-bootstrap"
SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
HOOKS = ROOT / "hooks" / "hooks.json"
STOP_SH = ROOT / "hooks" / "stop.sh"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Backticked skill-relative paths: `references/...`, `assets/...`, `scripts/...`, with an
# optional ` §N.M` anchor before the closing backtick.
SKILL_PATH_RE = re.compile(r"`((?:references|assets|scripts)/[A-Za-z0-9_./<>-]*)(?:\s*§[\d.a-z]+)?`")


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def frontmatter() -> dict[str, str]:
    text = _text(SKILL_MD)
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    block = text.split("---\n", 2)[1]
    out: dict[str, str] = {}
    parent = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and parent:
            k, v = line.strip().split(":", 1)
            out[f"{parent}.{k.strip()}"] = v.strip().strip('"')
        else:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v:
                out[k] = v.strip('"')
                parent = None
            else:
                parent = k
    return out


def test_name_matches_directory_and_spec_rules():
    fm = frontmatter()
    assert fm["name"] == SKILL_DIR.name
    assert 1 <= len(fm["name"]) <= 64
    assert NAME_RE.match(fm["name"])


def test_description_is_present_and_bounded():
    fm = frontmatter()
    assert 1 <= len(fm["description"]) <= 1024


def test_skill_md_is_under_500_lines():
    assert len(_text(SKILL_MD).splitlines()) < 500


def test_every_skill_relative_path_in_skill_md_exists():
    missing = []
    for m in SKILL_PATH_RE.finditer(_text(SKILL_MD)):
        p = m.group(1)
        if "<" in p:
            continue  # generic name such as references/profiles/<name>.md
        if not (SKILL_DIR / p.rstrip("/")).exists():
            missing.append(p)
    assert missing == []


def test_version_agrees_across_skill_and_manifests():
    fm = frontmatter()
    plugin = json.loads(_text(PLUGIN))
    market = json.loads(_text(MARKETPLACE))
    assert fm["metadata.version"] == plugin["version"] == market["plugins"][0]["version"]


def test_plugin_and_marketplace_name_the_skill():
    plugin = json.loads(_text(PLUGIN))
    market = json.loads(_text(MARKETPLACE))
    assert plugin["name"] == "project-bootstrap"
    assert market["plugins"][0]["name"] == "project-bootstrap"
    assert market["plugins"][0]["source"] == "./"


def test_hooks_json_registers_the_stop_script():
    hooks = json.loads(_text(HOOKS))
    stop = hooks["hooks"]["Stop"]
    cmd = stop[0]["hooks"][0]["command"]
    assert "hooks/stop.sh" in cmd
    assert "${CLAUDE_PLUGIN_ROOT}" in cmd


def _bootstrapped(cwd: Path) -> None:
    """A project past generation: docs/CURRENT.md exists, so the hook is allowed to block."""
    (cwd / "docs").mkdir(exist_ok=True)
    (cwd / "docs" / "CURRENT.md").write_text("# Current focus\n", encoding="utf-8")


def _run_stop(cwd: Path, stdin: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(cwd)}
    return subprocess.run(["sh", str(STOP_SH)], input=stdin, capture_output=True, text=True, cwd=cwd, env=env)


SH = shutil.which("sh")
needs_sh = pytest.mark.skipif(SH is None, reason="no sh on PATH")

# Claude Code writes compact JSON (no space after the colon); the hook must recognize both.
STOP_ACTIVE_JSON = ['{"stop_hook_active": true}', '{"stop_hook_active":true}']


@needs_sh
@pytest.mark.parametrize("stdin", STOP_ACTIVE_JSON, ids=["spaced", "compact"])
def test_stop_hook_exits_zero_when_stop_hook_active(tmp_path, stdin):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_stop(tmp_path, stdin)
    assert r.returncode == 0, r.stderr


@needs_sh
def test_stop_hook_exits_zero_when_project_has_no_linter(tmp_path):
    r = _run_stop(tmp_path, "{}")
    assert r.returncode == 0, r.stderr


@needs_sh
def test_stop_hook_skips_when_no_python_interpreter(tmp_path, tmp_path_factory):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    empty_dir = tmp_path_factory.mktemp("empty-path")
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": str(empty_dir)}
    r = subprocess.run([SH, str(STOP_SH)], input="{}", capture_output=True, text=True, cwd=tmp_path, env=env)
    assert r.returncode == 0, r.stderr
    assert "no python interpreter" in r.stdout + r.stderr


@needs_sh
def test_stop_hook_exits_zero_when_python_passing(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    r = _run_stop(tmp_path, "{}")
    assert r.returncode == 0, r.stderr


@needs_sh
def test_stop_hook_blocks_when_project_linter_fails(tmp_path):
    _bootstrapped(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_stop(tmp_path, "{}")
    assert r.returncode == 2
    assert "check_docs found errors" in r.stdout + r.stderr


@needs_sh
def test_stop_hook_blocks_when_stop_hook_active_is_false(tmp_path):
    _bootstrapped(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_stop(tmp_path, '{"stop_hook_active": false}')
    assert r.returncode == 2
    assert "check_docs found errors" in r.stdout + r.stderr


@needs_sh
def test_stop_hook_does_not_crash_on_non_json_stdin(tmp_path):
    _bootstrapped(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_stop(tmp_path, "")
    assert r.returncode == 2, r.stderr


PROJECT_STOP_SH = SKILL_DIR / "scripts" / "hooks" / "stop.sh"


def _run_project_stop(cwd: Path, stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(["sh", str(PROJECT_STOP_SH)], input=stdin, capture_output=True, text=True, cwd=cwd)


@needs_sh
@pytest.mark.parametrize("stdin", STOP_ACTIVE_JSON, ids=["spaced", "compact"])
def test_project_stop_hook_exits_zero_when_stop_hook_active(tmp_path, stdin):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_project_stop(tmp_path, stdin)
    assert r.returncode == 0, r.stderr


@needs_sh
def test_project_stop_hook_blocks_when_stop_hook_active_is_false(tmp_path):
    _bootstrapped(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_project_stop(tmp_path, '{"stop_hook_active": false}')
    assert r.returncode == 2
    assert "check_docs found errors" in r.stdout + r.stderr


@needs_sh
def test_project_stop_hook_does_not_crash_on_non_json_stdin(tmp_path):
    _bootstrapped(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_project_stop(tmp_path, "")
    assert r.returncode == 2, r.stderr


@needs_sh
def test_project_stop_hook_exits_zero_when_python_passing(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    r = _run_project_stop(tmp_path, "{}")
    assert r.returncode == 0, r.stderr


@needs_sh
def test_project_stop_hook_skips_when_no_python_interpreter(tmp_path, tmp_path_factory):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    empty_dir = tmp_path_factory.mktemp("empty-path-project")
    env = {**os.environ, "PATH": str(empty_dir)}
    r = subprocess.run([SH, str(PROJECT_STOP_SH)], input="{}", capture_output=True, text=True, cwd=tmp_path, env=env)
    assert r.returncode == 0, r.stderr
    assert "no python interpreter" in r.stdout + r.stderr


def test_hooks_readme_snippet_matches_project_script():
    readme = _text(SKILL_DIR / "scripts" / "hooks" / "README.md")
    m = re.search(r"```sh\n(#!/bin/sh\n.*?)```", readme, re.S)
    assert m, "no ```sh fenced block starting with #!/bin/sh found in README.md"
    fence = m.group(1).rstrip("\n")
    script = _text(PROJECT_STOP_SH).rstrip("\n")
    assert fence == script


def test_skill_lints_clean_when_copied_alone(tmp_path):
    copy = tmp_path / "project-bootstrap"
    shutil.copytree(SKILL_DIR, copy, ignore=shutil.ignore_patterns("__pycache__"))
    (copy / "docs").mkdir(exist_ok=True)
    (copy / "docs" / ".check_docs.toml").write_text(
        'citation_exclude = ["assets/templates/"]\n'
        'exclude = ["assets/templates"]\n',
        encoding="utf-8",
    )
    r = subprocess.run(
        [sys.executable, "scripts/check_docs.py", "--root", "."],
        cwd=copy,
        capture_output=True,
        text=True,
    )
    bad_lines = []
    for line in (r.stdout + r.stderr).splitlines():
        if "E001" in line or "E002" in line:
            if "E001" in line and "SKILL.md" in line and "BOOTSTRAP.md" in line:
                continue
            bad_lines.append(line)
    assert bad_lines == [], "unexpected citation errors:\n" + "\n".join(bad_lines) + "\n\nfull output:\n" + r.stdout + r.stderr


def test_skill_directory_works_when_copied_alone(tmp_path):
    copy = tmp_path / "project-bootstrap"
    shutil.copytree(SKILL_DIR, copy, ignore=shutil.ignore_patterns("__pycache__"))
    for m in SKILL_PATH_RE.finditer(_text(copy / "SKILL.md")):
        p = m.group(1)
        if "<" not in p:
            assert (copy / p.rstrip("/")).exists(), p
    r = subprocess.run([sys.executable, "scripts/check_docs.py", "--help"], cwd=copy, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


# --------------------------------------------------------------------------- release A: hooks warn until CURRENT.md exists

PROJECT_STOP_SH = SKILL_DIR / "scripts" / "hooks" / "stop.sh"


def _failing_linter(cwd: Path) -> None:
    (cwd / "tools").mkdir(exist_ok=True)
    (cwd / "tools" / "check_docs.py").write_text("import sys; print('E001 boom'); sys.exit(1)\n", encoding="utf-8")


@needs_sh
@pytest.mark.parametrize("script", [STOP_SH, PROJECT_STOP_SH], ids=["plugin", "project"])
def test_stop_hook_warns_but_does_not_block_before_current_md_exists(tmp_path, script):
    _failing_linter(tmp_path)
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    r = subprocess.run([SH, str(script)], input="{}", capture_output=True, text=True, cwd=tmp_path, env=env)
    assert r.returncode == 0, r.stderr
    assert "E001 boom" in r.stdout + r.stderr
    assert "bootstrap" in (r.stdout + r.stderr).lower()


@needs_sh
@pytest.mark.parametrize("script", [STOP_SH, PROJECT_STOP_SH], ids=["plugin", "project"])
def test_stop_hook_blocks_on_errors_once_current_md_exists(tmp_path, script):
    _failing_linter(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "CURRENT.md").write_text("# Current focus\n", encoding="utf-8")
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    r = subprocess.run([SH, str(script)], input="{}", capture_output=True, text=True, cwd=tmp_path, env=env)
    assert r.returncode == 2, r.stderr

# project-bootstrap

A bootstrap kit: docs, templates, and a linter that a software project copies in, or is pointed
at, so a human and their AI agents — Claude Code, Codex, others — share one set of design docs,
one workflow, and one source of truth for progress. It fits new projects and existing
codebases, solo weekend builds and multi-agent, multi-phase efforts, by picking a profile and a
tier instead of assuming one fixed shape of project.

The kit ships as one Agent Skill, `skills/project-bootstrap/`, that follows the
[Agent Skills](https://agentskills.io) layout: the procedure in `SKILL.md`, the rules in
`references/`, the templates in `assets/`, the linter in `scripts/`. Install it into your agent
or just read it.

## Install

**Any agent, via the `skills` CLI** (Claude Code, Codex, Cursor, Gemini CLI, Copilot, Cline
and others):

```
npx skills add NSpot-Games/project-bootstrap
```

**Claude Code, as a plugin** (adds a Stop hook that runs the linter in projects built on the
kit):

```
claude plugin marketplace add NSpot-Games/project-bootstrap
claude plugin install project-bootstrap@project-bootstrap
```

A freshly installed plugin is not visible to the running session: run `/reload-plugins`, or
start a new session, before asking for the skill.

or `/plugin marketplace add NSpot-Games/project-bootstrap` and
`/plugin install project-bootstrap@project-bootstrap` inside a session.

**By hand:** clone this repo and copy `skills/project-bootstrap/` into your agent's skills
directory (`.claude/skills/`, `.agents/skills/`, `~/.codex/skills/`, or wherever it reads
them). Or skip installing and hand your agent `BOOTSTRAP.md`.

## Use

Tell your agent to bootstrap the project. The skill classifies the repo as greenfield or
brownfield, asks five setup questions, writes the design docs one per session with a review
gate after each, generates the process files for the chosen tier, copies the linter into the
project, and opens the first session. Without a skill-aware agent, read `BOOTSTRAP.md` for the
idea in one page and follow `skills/project-bootstrap/references/core/adoption.md` by hand.

Projects built on the kit run the linter and generator as
`python tools/check_docs.py --root . --fix` at the end of every session. It is Python 3.11+,
standard library only. `skills/project-bootstrap/scripts/hooks/README.md` shows how to run it
from a Stop hook, a pre-commit hook, or CI.

## Repository layout

- `BOOTSTRAP.md` — the idea and the machinery, one page each, with pointers into the skill.
- `skills/project-bootstrap/SKILL.md` — the guided procedure.
- `skills/project-bootstrap/references/core/` — document kinds, layers, lifecycle,
  long-horizon rules, parallel agents, tiers, adoption, lessons.
- `skills/project-bootstrap/references/profiles/` — seven project profiles and how to pick one.
- `skills/project-bootstrap/assets/templates/` — the files a project copies in.
- `skills/project-bootstrap/scripts/` — `check_docs.py` and hook snippets.
- `tests/` — the linter's test suite and fixture project.
- `.claude-plugin/`, `hooks/` — Claude Code plugin manifests and the plugin Stop hook.

## Develop

- `python -m pytest tests -q` — test suite.
- `python skills/project-bootstrap/scripts/check_docs.py --root .` — lint this repo's own
  docs; must report zero errors and zero warnings.

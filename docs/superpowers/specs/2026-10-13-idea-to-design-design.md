# idea-to-design — design (v2.11.0)

**Date:** 2026-10-13
**Status:** approved in brainstorm, awaiting spec review

## 1. Intent

A raw idea ("a match-3 RPG where items change how matches deal damage") is not yet something a
project can be bootstrapped from. This release adds a second skill, `skills/idea-to-design/`,
that turns a raw idea into a design that can work — the hook, the purpose, the pillars, every
structural decision and the options not taken — written into `<project>/docs/vision/`, which
project-bootstrap's docs-first path already reads. The chain becomes
*idea-to-design → project-bootstrap → build*.

The method is distilled from the session that designed Glyphfall (NSpot-Games/glyphfall,
2026-10-13): place the idea among existing products and name what is new; ask the purpose
first; decide structure top-down, one multiple-choice question per message with a recommendation;
derive pillars and test every later choice against them; write each agreed area at once and
record every option not taken; keep rules apart from content and numbers; finish with a
consistency pass across all files. One failure of that session is designed against: the agent
drifted into prototype scope and engine architecture before the design was agreed, and the
owner had to pull it back.

**Decided in the brainstorm (owner):**

1. The skill is general — any product idea, not games only. Games are one example among others.
2. It is a second skill in the same plugin, `skills/idea-to-design/` beside
   `skills/project-bootstrap/`; one install gives both; both share one version.
3. The name is `idea-to-design`.
4. Output goes to `<project>/docs/vision/`.
5. No scripts: the skill is a conversation that writes Markdown.

**Success criteria**

- `python -m pytest tests -q` passes; `check_docs.py --root .` reports 0 errors, 0 warnings.
- All existing eval assertions still pass.
- The six `idea-to-design` scenarios of §7 are run once against a baseline (an agent with the
  scenario prompt and no skill) before `SKILL.md` is written, and pass in full after.

**Out of scope:** a linter for `docs/vision/`; any game-specific reference file; generating
code, prototypes or plans; changes to how project-bootstrap derives design docs from vision
notes (`skills/project-bootstrap/references/core/adoption.md` is unchanged).

## 2. Triggering

`description` in the frontmatter names the trigger phrases: "I have an idea for…", "turn this
idea into something that works", "design this product / game / tool", "is this idea any good".
It names what is not its job: building, code changes, and bootstrapping a project that already
has design notes — those go to project-bootstrap or a brainstorming skill.

## 3. The procedure (`SKILL.md`)

Nine numbered steps, in order. Each is short in `SKILL.md`; the method behind steps 3 and 8 lives
in references (§4).

1. **Find the hook.** Restate the idea; place it among existing products ("this mix already
   exists in A, B, C"); name the one thing that is new. If nothing is new, say so plainly and help
   find an angle that is. Nothing else is asked until the hook is stated.
2. **Purpose first.** One question, multiple choice, with a recommendation: what the product is
   for (commercial, internal tool, learning, …). Asked before any feature, because it changes most
   later answers.
3. **Structural decisions, top-down, one per message.** 2–4 options that genuinely differ, each
   with its trade-off and a real product as a reference point; the recommendation first, with its
   reason. Biggest structure first, details later. Method: `references/questions.md`.
4. **Pillars.** Once the shape is visible, derive 3–5 short rules every later feature is checked
   against. From then on, a recommendation that breaks a pillar says so; an option rejected for
   breaking one names the pillar.
5. **Write as you go.** Each agreed area goes into its own `docs/vision/<area>.md` at once and is
   committed. Every option not taken goes into `docs/vision/alternatives.md` with a note on where
   it might fit later; ideas parked on purpose go under "Possible additions". If the repository
   does not exist yet, the skill offers to create it before the first write; it never pushes or
   creates a remote without the person's yes.
6. **Rules apart from content and numbers.** Rules are agreed first. Content lists and numbers
   are recorded as "still to design" in the area file and never block the next decision.
7. **Technology waits.** No engine, stack or architecture decision until the design is agreed.
   A technical question raised mid-design is answered briefly, recorded as a parked note in
   `docs/vision/README.md` under "Parked for later", and the conversation returns to design. A hard
   technical limit that shapes the design (a platform's rules, a regulation) is recorded as a
   constraint, not as design.
8. **Consistency pass.** Read every file together; find rules that cannot happen, numbers that
   clash, timings that conflict, stale summaries, and fairness or abuse gaps. Fix each in the
   files, commit, and report each fix so the person can check it. Method:
   `references/consistency-pass.md`.
9. **Hand off.** Summarize what is decided and what is still to design; offer the next step:
   project-bootstrap (which reads `docs/vision/`) or a first prototype.

**Conduct, stated once in `SKILL.md`:** plain language; one question per message; always a
recommendation with its reason; a change of direction from the person is taken at once, without
arguing back; a choice against the recommendation is accepted and the recommended option is
recorded in `alternatives.md` like any other.

## 4. The package

```
skills/idea-to-design/
  SKILL.md
  references/
    questions.md
    consistency-pass.md
  assets/templates/
    vision-readme.md
    alternatives.md
    area.md
```

| File | Holds |
|---|---|
| `SKILL.md` | frontmatter (`name`, `description`, `license: MIT`, `metadata.author`, `metadata.version`); the nine steps of §3; the conduct rules |
| `references/questions.md` | building a question: options that genuinely differ; one reference product per option; trade-offs stated as what is gained and what is lost; recommendation first with its reason; checking each option against the pillars once they exist; ordering decisions from structure to detail; when a question is too small to ask (pick the conventional default and say so) |
| `references/consistency-pass.md` | the checklist: rules that assume an impossible state; numbers or timings that conflict across files; limits that trigger inside the intended normal case; summaries (README, the decided table) that no longer match the area files; fairness and abuse gaps (paid or random advantages leaking into ranked or competitive parts); each finding fixed and reported |
| `assets/templates/vision-readme.md` | sections: the hook; purpose; pillars; how it fits together; decided (a table linking each area file); still to design (a table with status); parked for later |
| `assets/templates/alternatives.md` | per question: the question as a heading, the chosen option in bold, a table of options not taken with notes; a final "Possible additions" section |
| `assets/templates/area.md` | the rule of the area in one paragraph; its rules; "Still to design" |

Paths inside the skill are relative to the skill root, as in project-bootstrap, so the skill works
installed alone. Templates use `<angle-bracketed>` names, not double-brace placeholders, since they
are filled by conversation, not generated.

## 5. Changes to project-bootstrap and the repository

- **`skills/project-bootstrap/SKILL.md` §1:** when the request is to bootstrap a project that has
  only an idea — no code and no design notes — offer `idea-to-design` first, in one line, and
  continue with bootstrap if the person declines.
- **`README.md`:** the kit ships two skills; a short "Use" paragraph for `idea-to-design` and the
  chain *idea-to-design → project-bootstrap*.
- **`BOOTSTRAP.md`:** one paragraph naming the step before bootstrap.
- **`AGENTS.md`:** the repository holds two skills; the path rule (skill-relative inside each
  skill, full at the repo root) applies to both; the version line names both `SKILL.md` files.
- **`.claude-plugin/plugin.json` and `marketplace.json`:** description mentions both skills;
  keywords gain `ideation`, `product-design`; version 2.11.0.

## 6. Tests

**`tests/test_skill_package.py`** checks every directory under `skills/` rather than only
`project-bootstrap`: valid frontmatter, a name matching its folder and `NAME_RE`, every
backticked skill-relative path existing inside that skill, no path escaping the skill, and the
version agreeing with the plugin manifests. A test proves the generalised check fails on a
broken second skill (a missing reference path) before it is trusted.

**`tests/test_kit_consistency.py`:** its checks concern project-bootstrap's linter, tokens and
templates, and stay as they are. One test is added: no file under `skills/idea-to-design/`
carries a double-brace placeholder, since its templates are filled by conversation.

## 7. Evals

Six scenarios in `evals/evals.json`, each a fresh agent with the skill installed and a fixture
repository (a new `evals/fixtures/idea-only/`: an empty repo with a one-paragraph README):

| Scenario | Prompt | Assertions |
|---|---|---|
| `raw-idea` | a one-line idea | the first message places the idea among named existing products and states what is new; the first question is the purpose; exactly one question in the message; a recommendation with a reason |
| `tech-drift` | a design in progress (fixture transcript summary) and the person asks "which database should we use?" | answered briefly; recorded under "Parked for later"; the message returns to the open design question; no stack decision recorded as design |
| `against-recommendation` | the person picks the non-recommended option | accepted without counter-argument; `alternatives.md` records the recommended option as not taken |
| `nothing-new` | an idea identical to an existing product | the message says plainly that it exists and names it; offers at least two angles that would make it new |
| `consistency` | a finished `docs/vision/` fixture with three planted contradictions (an impossible rule, a limit inside the normal case, a stale summary) | all three found, fixed in the files, and each reported |
| `handoff` | design agreed, the person says "that's everything" | `docs/vision/README.md` has decided and still-to-design tables linking every area file; `alternatives.md` exists; project-bootstrap is offered |

**Baseline first:** each scenario is run once with no skill installed, before `SKILL.md` is
written; failures are recorded in `evals/baseline-idea-to-design-<date>.md` as the target
assertions. The release run records results in `evals/release-k-<date>.md`.

## 8. Release

Version 2.11.0 in `skills/project-bootstrap/SKILL.md`, `skills/idea-to-design/SKILL.md`,
`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the repository's
`AGENTS.md`.

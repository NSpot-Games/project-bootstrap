# evals/

Behavioural evals for the skill: what an agent *does* when it follows the procedure, which the
linter's unit tests cannot see. A full bootstrap is multi-session and human-gated, so each
scenario is one step of it, run against a synthetic starting repository, ending where the
procedure would wait for a human. The setup answers an agent would ask for are supplied in the
prompt; the agent stops at the first gate not answered there.

Everything here is invented. The fixtures describe Fieldnote, a made-up CLI and library that
turns a folder of markdown field notes into a static site; no content from any real project is
used, so the suite is project-agnostic and safe to publish with the kit.

## Layout

- `evals.json` — the fifteen scenarios: fixture, setup, prompt, expected outcome, and typed
  assertions. The prompt substitutes `{answers}` and `{brainstorm}` from the top-level fields.
- `fixtures/<name>/` — starting repositories: `plain-greenfield` (a README), `docs-rich-greenfield`
  (no code, three vision docs with one deliberate contradiction), `after-roadmap` (design docs and
  roadmap written, no process files), `generated` (a project the moment generation finished,
  nothing claimed), `idea-only` (a README), `vision-in-progress`, `vision-flawed` and `vision-clean`
  (Tidepool, an invented tool-lending app, at three points of an idea-to-design conversation;
  `vision-flawed` carries three planted contradictions).
- `harness.py` — `prepare`, `grade`, `report`. Standard library only.
- `fake_gh.py` — a stand-in for the gh CLI that the tracker scenarios put in `<project>/.fake-gh/`;
  it answers from a JSON state file and logs every call with the number of plan files present.
- `runs/` — ignored by git; one directory per scenario and label holding the scratch project,
  the prompt, the grading and timing.
- `seeds/` — ignored by git except its README; snapshots of real repositories, each a clone with
  no remote, for acceptance runs (`harness.py seed add|refresh|prepare|list`); their runs go to
  `runs/acceptance/<name>-<date>/`. See `seeds/README.md`.

## The fifteen scenarios

| Scenario | Step under test | What it measures |
|---|---|---|
| `docs-rich-greenfield` | classification, C1 | a repo with no code but existing docs is inventoried and reconciled, not brainstormed from blank |
| `first-session` | SKILL.md §5 | the first claim flips the milestone, creates one plan, regenerates the indexes, creates no stubs |
| `git-guidance` | the whole run's git shape | a bootstrap branch, the pre-bootstrap SHA recorded, no transitional rules in AGENTS.md |
| `compressed-mode` | the one-doc-per-session override | dependency order, a green linter, and a record of which docs got the least scrutiny |
| `one-design-doc` | C2 and its gate | header, numbering, changelog, no in-doc open-questions section, the verbatim gate message |
| `generation` | SKILL.md §4 | every process file, no tokens, no stubs, config and line-ending files, a green linter |
| `ci-default` | CI written in feature work | one workflow, a fast job on PRs and a slow one on main or a schedule, a path filter, no deploy step, a local `check` command in AGENTS.md |
| `tracker-claim` | SKILL.md §5 with a tracker | `claim` runs before the plan is written and assigns the feature |
| `tracker-held` | the claim lock | a feature assigned to someone else is not claimed, and the human is told who holds it |
| `raw-idea` | idea-to-design steps 1–3 | the idea placed among existing products, its hook named, one purpose question with a recommendation, no stack |
| `tech-drift` | idea-to-design step 7 | a technical question parked under "Parked for later", the conversation returned to design |
| `against-recommendation` | idea-to-design step 5 and conduct | a choice against the recommendation accepted without argument and recorded with the recommended option as not taken |
| `nothing-new` | idea-to-design step 1 | an idea that already exists named plainly, with angles offered |
| `consistency` | idea-to-design step 8 | three planted contradictions found, fixed and reported |
| `handoff` | idea-to-design steps 8–9 | a clean design left unchanged, a summary, project-bootstrap offered |

The first nine exercise project-bootstrap; the last six exercise idea-to-design (`"skill": "idea-to-design"`), and their prompts give the user's turn of an ongoing conversation.

Some assertions are *targets*: they fail against the current skill on purpose and pass once the
procedure change they measure has shipped. A baseline run records which.

## Running

1. Prepare every scenario into a runs directory, pointing at the skill version under test:

   ```
   python evals/harness.py prepare all evals/runs --label <label>
   python evals/harness.py prepare all evals/runs --label baseline --skill <path to a snapshot of the old skill>
   python evals/harness.py prepare <scenario> evals/runs --label baseline --no-skill
   ```

   A scenario names the skill it exercises with an optional `"skill"` key (default `project-bootstrap`); `--no-skill` writes a prompt with no skill at all, the baseline for a new skill.

2. For each `evals/runs/<scenario>/<label>/prompt.md`, hand the prompt to a fresh agent
   (a subagent, or a separate session) and let it work inside `project/`. The agent must write
   `<project>/final_message.md` before it stops. Save its token and time usage as
   `timing.json` (`total_tokens`, `duration_ms`) next to the prompt if the harness reports them.

3. Grade and report:

   ```
   python evals/harness.py grade all evals/runs --label <label>
   python evals/harness.py report evals/runs
   ```

`grade` writes `grading.json` per run with `text`, `passed`, `evidence` per assertion, the
shape the skill-creator viewer reads, so `generate_review.py` from that skill can render the
outputs for a human pass when one is wanted.

## Adding a scenario

Add a fixture directory, an entry in `evals.json`, and assertions using the checks
`harness.py` knows: `file_exists`, `files_exist`, `file_absent`, `grep`, `not_grep`,
`grep_any`, `none_grep`, `mentions_each`, `unchanged`, `count_glob`, `no_tokens`, `lint`,
`git_branch_prefix`, `git_commits_min`, `git_clean`, `sha_recorded`, `final_contains`,
`final_not_contains`, `final_count`. Prefer assertions the linter or a grep can decide; leave judgement
calls (is the doc deep enough?) to a human reading the outputs.

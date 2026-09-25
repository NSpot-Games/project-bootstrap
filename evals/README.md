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

- `evals.json` — the seven scenarios: fixture, setup, prompt, expected outcome, and typed
  assertions. The prompt substitutes `{answers}` and `{brainstorm}` from the top-level fields.
- `fixtures/<name>/` — starting repositories: `plain-greenfield` (a README), `docs-rich-greenfield`
  (no code, three vision docs with one deliberate contradiction), `after-roadmap` (design docs and
  roadmap written, no process files), `generated` (a project the moment generation finished,
  nothing claimed).
- `harness.py` — `prepare`, `grade`, `report`. Standard library only.
- `runs/` — ignored by git; one directory per scenario and label holding the scratch project,
  the prompt, the grading and timing.
- `seeds/` — ignored by git except its README; snapshots of real repositories, each a clone with
  no remote, for acceptance runs (`harness.py seed add|refresh|prepare|list`); their runs go to
  `runs/acceptance/<name>-<date>/`. See `seeds/README.md`.

## The seven scenarios

| Scenario | Step under test | What it measures |
|---|---|---|
| `docs-rich-greenfield` | classification, C1 | a repo with no code but existing docs is inventoried and reconciled, not brainstormed from blank |
| `first-session` | SKILL.md §5 | the first claim flips the milestone, creates one plan, regenerates the indexes, creates no stubs |
| `git-guidance` | the whole run's git shape | a bootstrap branch, the pre-bootstrap SHA recorded, no transitional rules in AGENTS.md |
| `compressed-mode` | the one-doc-per-session override | dependency order, a green linter, and a record of which docs got the least scrutiny |
| `one-design-doc` | C2 and its gate | header, numbering, changelog, no in-doc open-questions section, the verbatim gate message |
| `generation` | SKILL.md §4 | every process file, no tokens, no stubs, config and line-ending files, a green linter |
| `ci-default` | CI written in feature work | one workflow, a fast job on PRs and a slow one on main or a schedule, a path filter, no deploy step, a local `check` command in AGENTS.md |

Some assertions are *targets*: they fail against the current skill on purpose and pass once the
procedure change they measure has shipped. A baseline run records which.

## Running

1. Prepare every scenario into a runs directory, pointing at the skill version under test:

   ```
   python evals/harness.py prepare all evals/runs --label <label>
   python evals/harness.py prepare all evals/runs --label baseline --skill <path to a snapshot of the old skill>
   ```

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
`final_not_contains`. Prefer assertions the linter or a grep can decide; leave judgement
calls (is the doc deep enough?) to a human reading the outputs.

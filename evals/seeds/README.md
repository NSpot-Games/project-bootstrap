# evals/seeds/

Starting points for acceptance runs on real repositories. A seed is a snapshot of a real
project at a pinned commit, kept as a git clone with its remote removed, so a run can bootstrap
it exactly as the skill would in the field and a push is impossible by construction. Seeds are
local only: everything in this directory except this file is ignored by git, because the
projects are real and their content stays out of the kit.

## Layout

```
evals/seeds/<name>/            the clone, on the branch it was taken from, no remote
evals/seeds/<name>/.seed.json  where it came from: source path, branch, commit, date taken
evals/runs/acceptance/<name>-<date>/   one run's working copy, produced from the seed
```

`<name>` is the project's kebab-case name, never a number: a number says nothing to the next
reader and breaks the moment seeds are reordered.

## Commands

```
python evals/harness.py seed add <name> <path-to-local-repo> [--branch main]
python evals/harness.py seed refresh <name>        re-snapshot from the recorded source
python evals/harness.py seed prepare <name>        copy the seed into a dated run directory
                                                   and write the owner-conversation prompt
python evals/harness.py seed list
```

`seed prepare` never touches the seed itself; it writes a fresh working copy under
`evals/runs/acceptance/`, so the same seed can be bootstrapped by every later version of the
skill and the outputs compared. A run's working copy is itself a git repository with no
remote; the agent commits there and nowhere else.

## Scoring

An acceptance run is scored by hand with `evals/rubric.md`, the reviewer acting as the owner
at each gate. Record the numbers and the triaged improvisations in a dated file under `evals/`,
never the project's content: the write-up describes the shape of the run (docs-first or not,
how many documents, which profile and tier) and its results, and nothing else.

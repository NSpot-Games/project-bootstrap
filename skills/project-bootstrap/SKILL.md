---
name: project-bootstrap
description: Bootstrap a new project or adopt an existing one into the docs-as-contract workflow. Use when the user says "bootstrap a project", "set up docs for this repo", "adopt the bootstrap kit", or pastes BOOTSTRAP.md.
license: MIT
compatibility: Requires Python 3.11+ for scripts/check_docs.py
metadata:
  author: NSpotGames
  version: "2.3.0"
---

# Project Bootstrap

Runs the greenfield or brownfield adoption procedure as a guided conversation: classify the
project, ask the setup questions, write the design docs one per session with a human review
gate after each, generate the process files, run the linter, and open the first session. Follow
the sections below in order; do not skip ahead to generation before the docs it depends on exist.

Every file this skill names lives inside its own directory: rules in `references/core/`,
profiles in `references/profiles/`, templates in `assets/templates/`, the linter in
`scripts/check_docs.py`. Paths are relative to the skill root, so the skill works when installed
on its own. Paths written `<project>/...` are in the project being bootstrapped.

## 1. Announce and classify

Look at the target repository and say which of these it is, per `references/core/adoption.md §3`:

- **Greenfield** — an empty repository, no code, nothing to recover.
- **Docs-first** — no code, but the repository already carries thinking: vision notes, research,
  specs, journals. Say so in those words ("docs-first: no code, existing docs under
  `<project>/docs/vision/`" or wherever they are), because the brainstorm step changes shape.
- **Brownfield** — any repository with real code in it, even rough or partial, or with code but
  no docs.

Greenfield follows §1a through §5 below. Docs-first follows §1a, then §6a, then §3(b) onward.
Brownfield follows §1a, then §6.

## 1a. Record the starting point in git

Before writing anything, make the pre-bootstrap state a commit and put the bootstrap on its own
branch, so the whole thing is reviewable as one diff and reversible with one command:

1. If the repository has no commits, `git init` and commit what is there as
   `pre-bootstrap: the repository before the docs-as-contract bootstrap`.
2. Record `git rev-parse --short HEAD`. Create `bootstrap/<codename>` from it. The first commit
   on the branch names that SHA in its message (`bootstrap: starting from <sha>`), so the
   starting point survives even if the branch is squashed.
3. Commit after every step that ends in a file: one commit per design doc, one for the roadmap,
   one for generation. Open one pull request when §5 is reached.
4. Never write a rule about the bootstrap branch into `<project>/AGENTS.md` or
   `<project>/docs/WORKFLOW.md`. The branch expires at merge; a rule about it would outlive it.
   If the user asks for such a rule anyway, add a row to `<project>/docs/OPEN-QUESTIONS.md` to
   remove it at merge.

The linter knows the bootstrap is running because `<project>/docs/CURRENT.md` does not exist
yet: until then a citation to a file under `docs/` that a later step will create is a warning
(`W007`), not an error. Cite the real path the procedure will create; do not angle-bracket it.

## 2. C0: five questions, one at a time

Ask these one per message, in this order, and wait for the answer before asking the next.
Record each answer in a scratch list; write nothing to disk yet.

1. **Name and codename.** What is the project called?
2. **Naming convention.** Recommend kebab-case, unnumbered — numbered prefixes look tidy and
   then break every cross-reference the first time something is reordered.
3. **Example location.** Where will the example instance live — `<project>/cases/<id>/`,
   `<project>/fixtures/`, or similar? The architecture doc will cite it.
4. **Tier.** Recommend one from `references/core/tiers.md`, based on scope: solo, one phase,
   under ten features suggests lite; most projects land on standard; multi-phase, multi-agent,
   or regulated suggests full.
5. **Profile.** Recommend one from `references/profiles/README.md`, based on the project's
   central artefact.

Do not write any file until all five are answered.

## 3. Brainstorm, design docs, roadmap — one document per session

This section runs C1 through C8 of `references/core/adoption.md §1`, one session per step
below, in order.

**(a) Brainstorm (C1).** Hold this as its own session, with no file written: what the project
is, who it's for, what's hard, what the real alternatives are, what will not be built. Push on
the hardest technical constraint early. End the session with a list of decisions made and
questions left open, held in the scratch list alongside C0's answers.

**(b) Design docs (C2 through C7), one per session.** State the rule and the reason to the
user: this skill writes at most one design doc per session, because a one-shot bootstrap that
writes several docs back to back produces shallow docs — each later one gets less scrutiny
than the last. Write the docs the chosen profile calls for (`references/profiles/<name>.md`),
phase 1 only, in the order the profile lists.

A design doc never carries an open-questions section. Every question goes to
`<project>/docs/OPEN-QUESTIONS.md` — create it from `assets/templates/OPEN-QUESTIONS.md` the
first time a question arises, before generation — and the doc carries one line pointing there
(`references/core/lessons.md §1`, lesson 5). A question inside a doc is the one place nobody
looks for it again.

After finishing each doc, stop and post exactly:

> Review `<path>`. Say 'next' to continue or tell me what to change.

Do not start the next doc, or move on to the roadmap, until the user replies.

**(c) Roadmap (C8), its own session.** Decide phase 1's exit, then the current and next
milestones' goals and measurable exits; everything beyond those two is `sketch` — a goal
sentence and nothing more. Write `<project>/docs/roadmap.md` from
`assets/templates/roadmap.md`, then apply the same review gate as (b): stop and post the message
above. Do not move on to generation (§4) until the user replies.

## 3a. Compressed bootstrap

When the user explicitly asks to finish in one sitting, the one-doc-per-session rule is
overridden, but not the reason for it: the later docs will get less scrutiny, and that fact
must be recorded rather than lost. In compressed mode:

1. Write in dependency order: the example instance (or golden example) before any doc that
   cites it; the profile's primary design doc before the surface, runtime or architecture docs;
   the roadmap last.
2. Post one review gate per group instead of per doc — one after the design docs, one after the
   roadmap — unless the user has also waived the gates, in which case post none and carry on.
3. Before generation, add one row to `<project>/docs/OPEN-QUESTIONS.md`: *Question* "Revisit
   `<the docs written last>`: written in a compressed bootstrap with the least review";
   *Blocks* the first milestone that depends on them; *Needed by* before that milestone starts.
4. In the message that ends the run, name which docs got the least scrutiny and point at that
   row. Every design doc written this way stays `draft`.

## 4. Generation

Once the brainstorm, phase 1's design docs, and the roadmap are all written and reviewed:

1. Copy the files `assets/templates/` provides for the chosen tier into the project;
   `references/core/tiers.md` lists which files each tier gets.
2. Copy `scripts/check_docs.py` to `<project>/tools/check_docs.py`. If the user wants the
   linter to run without being remembered, also copy `scripts/hooks/stop.sh` to
   `<project>/tools/hooks/stop.sh` and wire it as `scripts/hooks/README.md` shows.
3. Substitute every `{{token}}` using the table in `assets/templates/README.md`; values come
   from C0's answers, the brainstorm's decisions, the design docs, and the roadmap just written.
4. Create the milestone files for the current and next milestone; everything beyond stays
   `sketch` in the roadmap only.
5. From the project root, run `python tools/check_docs.py --root . --fix` and fix whatever it
   reports. `--fix` writes the four generated files before it checks, so a clean project passes
   on the first run; a warning about an evidence file not written yet (`W005`) is expected
   until the milestone closes.

## 5. First session

Open `<project>/docs/CURRENT.md` and claim `M0-01`: write its plan from `assets/templates/plan.md`
with `**Status:** in progress` and a session stamp, append the plan's path to the feature line
in `<project>/docs/milestones/M0.md`, and — because this is the milestone's first claim — set
`M0` itself to `in progress` in the same edit (`references/core/parallel-agents.md §1`). Run
`python tools/check_docs.py --root . --fix` so `<project>/docs/CURRENT.md` shows the claim.
Follow `<project>/docs/WORKFLOW.md` from there.

## 6. Brownfield variant

Follow the seven steps of `references/core/adoption.md §2`, in order: inventory;
reverse-engineer the architecture doc from the code; recover the data model and an anonymised
example instance; backfill ADRs from git history; write the design doc as a
vision-and-current-state document; build the roadmap from the issue tracker; generate, lint,
and open on a feature named "close the gaps the inventory found". Generation follows §4 steps
1 through 5. The same one-doc-per-session gate from §3 applies to every doc this variant
writes — stop after each one and post the review-gate message before continuing.

## 6a. Docs-first variant

Follow `references/core/adoption.md §4`. In outline:

1. **Inventory and classify** every existing document as *contract* (it becomes, or feeds, a
   design doc), *history* (a dated record of thinking: vision, journals, research; frozen, never
   edited, cited as history), or *external reference* (someone else's material). Hold the
   classification in the scratch list; it is written into `<project>/DOCS.md §1` at generation.
2. **Fix names and inbound links first**, in one commit, if any file will be renamed or moved,
   so no later doc cites a path that then changes.
3. **Reconcile instead of brainstorming from blank.** C1 becomes a reconciliation pass over the
   history: the decisions already taken (with their dates), the questions still open, and every
   contradiction between documents. Each contradiction is a decision the user makes before the
   design doc that depends on it is written; put them to the user first, hardest constraint
   first, as C1 would.
4. **Derive, and say what supersedes what.** Each design doc is derived from the history with
   citations back to it, and its first paragraph states what it supersedes ("supersedes
   `<project>/docs/vision/<file>.md` for <topic>"). History is never edited to match.
5. **Keep the linter off frozen prose.** History folders go into `citation_exclude` in
   `<project>/docs/.check_docs.toml`, so an anchor that no longer resolves in a dated note never
   forces a rewrite of the record.

Then continue with §3(b): the profile's design docs, one per session, each behind its gate.

## 7. What this skill never does

- Write more than one design doc in a single session, unless the user explicitly says to —
  and then only as §3a describes, with the least-reviewed docs recorded.
- This skill never ticks a box; ticking happens in feature work, with verification evidence.
- Accept an ADR — an ADR moves from `proposed` to `accepted` by human decision, never by this
  skill.
- Edit a generated file by hand (`<project>/docs/CURRENT.md`,
  `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`,
  `<project>/docs/decisions/README.md`); only the project's `tools/check_docs.py --fix` writes
  those.

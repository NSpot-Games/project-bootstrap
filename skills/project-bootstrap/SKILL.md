---
name: project-bootstrap
description: Bootstrap a new project or adopt an existing one into the docs-as-contract workflow. Use when the user says "bootstrap a project", "set up docs for this repo", "adopt the bootstrap kit", or pastes BOOTSTRAP.md.
license: MIT
compatibility: Requires Python 3.11+ for scripts/check_docs.py
metadata:
  author: NSpotGames
  version: "2.6.0"
---

# Project Bootstrap

Runs the greenfield, docs-first or brownfield adoption procedure as a guided conversation:
classify the project, ask the setup questions, write the design docs one per session with a
human review gate after each, generate the process files, run the linter, and open the first
session. Follow the sections below in order; do not skip ahead to generation before the docs it
depends on exist.

Every file this skill names lives inside its own directory: rules in `references/core/`,
profiles in `references/profiles/`, templates in `assets/templates/`, the linter in
`scripts/check_docs.py`. Paths are relative to the skill root, so the skill works when installed
on its own. Paths written `<project>/...` are in the project being bootstrapped. Inside the
project's own docs, cite root-relative paths (`docs/design/<name>.md §N`); the linter resolves
them from the project root.

## 1. Announce and classify

Look at the target repository and say which of these it is, per `references/core/adoption.md §3`:

- **Greenfield** — an empty repository, or one with nothing but a README: no code, nothing to
  recover, no thinking written down yet.
- **Docs-first** — no code, but the repository already carries thinking: vision notes, research,
  specs, journals, a notes file. Any written thinking counts, however small; a six-line notes
  file is docs-first. Say so in those words ("docs-first: no code, existing docs under
  `<project>/docs/vision/`" or wherever they are), because the brainstorm step changes shape.
- **Brownfield** — any repository with real code in it, even rough or partial, or with code but
  no docs.

Every path runs §1a and §2 first. Greenfield then follows §3 through §5. Docs-first runs §6a in
place of §3(a) and continues with §3(b) onward. Brownfield follows §6. The first setup question
may follow the announcement in the same message.

## 1a. Record the starting point in git

The bootstrap is reviewable as one diff and reversible with one command because it lives on its
own branch, starting from a commit that captures the repository as it was:

1. If the repository has no commits, `git init` and commit what is there as
   `pre-bootstrap: the repository before the docs-as-contract bootstrap`.
2. Record `git rev-parse --short HEAD` now. Create `bootstrap/<codename>` from it as soon as the
   codename is known (§2, question 1); nothing is written to disk before then, so nothing is
   lost by waiting. The first commit on the branch, whatever it contains — in docs-first it is
   the rename-and-relink commit of §6a — names the SHA in its subject (`bootstrap: starting from
   <sha>`), so the starting point survives even if the branch is squashed.
3. Commit after every step that ends in a file: one commit per design doc, one for the roadmap,
   one for generation, one for the first claim. Open one pull request when §5 is reached; with no
   remote configured, say so in one line and leave the branch for the user.
4. Never write a rule about the bootstrap branch into `<project>/AGENTS.md` or
   `<project>/docs/WORKFLOW.md`. The branch expires at merge; a rule about it would outlive it.
   If the user asks for such a rule anyway, add a row to `<project>/docs/OPEN-QUESTIONS.md` to
   remove it at merge.

The linter knows the bootstrap is running because `<project>/docs/CURRENT.md` does not exist
yet: until then a citation to a project file that a later step will create — a design doc, the
example instance's folder, a milestone file — is a warning (`W007`), not an error. Cite the real path the procedure will create; do not angle-bracket it.
A doc the profile schedules for a later phase is different: it is not created by the bootstrap,
so name it in prose until it exists. Before the project has its own linter copy, run the kit's
read-only after each commit (`python <skill>/scripts/check_docs.py --root <project>`); never
`--fix` before generation.

## 2. C0: five questions, one at a time

Ask these one per message, in this order, and wait for the answer before asking the next.
Record each answer in a scratch list; write nothing to disk yet.

1. **Name and codename.** What is the project called? The codename is a kebab-case slug used
   for the branch (`bootstrap/<codename>`) and the primary design doc
   (`docs/design/<codename>-design.md`).
2. **Naming convention.** Recommend kebab-case, unnumbered — numbered prefixes look tidy and
   then break every cross-reference the first time something is reordered.
3. **Example location.** Where will the example instance live? Recommend `<project>/cases/<id>/`
   when instances are named things (a tenant, a garden, a level, a customer) and
   `<project>/fixtures/` when they are anonymous samples. `<id>` is a kebab-case name for the
   instance; when the real one is anonymised, invent a plausible one. The instance is written in
   the schema's native format when the data model names one (CSV, SQL, YAML); otherwise one
   JSON file per collection plus a manifest listing them, which also fits an ORM's models. It
   carries a README stating where it came from, with a numbered *Gaps* section (see §3(b)), and,
   when the project imports data, the source the import reads (the spreadsheet sheets as CSV)
   beside it, so the import journey can be exercised; the architecture doc will cite the folder.
4. **Tier.** Recommend one from `references/core/tiers.md`, based on scope: solo, one phase,
   under ten features suggests lite; most projects land on standard; multi-phase, multi-agent,
   or regulated suggests full. No feature list exists yet: estimate from whatever notes or
   requests exist, and default to standard when nothing does.
5. **Profile.** Read the candidate in `references/profiles/README.md §1`, then the profile file
   itself, and recommend it naming the design docs it writes at bootstrap and what its M0 does.

Do not write any file until all five are answered. The technology stack, hosting and runtime
are not setup questions; they are brainstorm decisions (§3(a)).

## 3. Brainstorm, design docs, roadmap — one document per session

This section runs C1 through C8 of `references/core/adoption.md §1`, one session per step
below, in order.

**(a) Brainstorm (C1).** Hold this as its own session, with no file written: what the project
is, who it's for, what's hard, what the real alternatives are, what will not be built. Push on
the hardest technical constraint early, and settle the stack before the session ends —
language, runtime, hosting, the one or two libraries the architecture doc will commit to — since
that doc cannot be written without them and should not invent them. End the session with a list
of decisions made and questions left open, held in the scratch list alongside C0's answers.

The user may batch: answer several questions in one message, or ask to close the brainstorm and
write the first design doc in the same session. Do so; one design doc per session still holds.
The user may delegate ("take your recommendation"): record each recommendation as a decision
marked *recommended, not confirmed* in the Decisions section of the doc that rests on it
(§3(b)), and put every one that a wrong guess would make expensive to change into
`<project>/docs/OPEN-QUESTIONS.md` with the user as owner.

**(b) Design docs (C2 through C7), one per session.** State the rule and the reason to the
user: this skill writes at most one design doc per session, because a one-shot bootstrap that
writes several docs back to back produces shallow docs — each later one gets less scrutiny
than the last. Write the docs the chosen profile calls for (`references/profiles/<name>.md`),
phase 1 only, in the order the profile lists.

The example instance (C4: the profile's seed fixture, golden example or worked instance) is
written in the session of the doc it belongs with — the data-model doc for most profiles —
before that doc is finished, so the gaps it exposes are folded in while the doc is open. Every
gap goes into the instance README's numbered *Gaps* section, marked *folded*, *held for M0*, or both
when the model change is folded and the policy behind it is held;
the data-model doc points at that section, and the held ones are copied into M0's notes at
generation (§4, step 4). Fold the clear gaps at once; hold the ones that need a decision. When
the real instance cannot be obtained at bootstrap, write a constructed stand-in in the actual
schema, say so in its README, and make replacing it with the real one an M0 feature. Any script
that generated the instance stays out of the project unless it becomes a tool.

Every design doc, whatever its profile outline says, ends with two things before its changelog:
a numbered *Decisions* section listing the decisions the doc rests on — each marked *owner*,
*recovered* (from pre-bootstrap history, with the date) or *recommended, not confirmed* — and
the one-line pointer to the open-questions file (`references/core/doc-kinds.md §3`). The
primary design doc's Decisions section is where the brainstorm's decision list is written down;
the ADR backfill (§4, step 4a) reads these sections and nothing else. When a decision taken in
a later session contradicts an earlier doc, edit the earlier doc in the same commit, with a
changelog line naming the decision; a design doc is never left saying something the project has
decided against. When a later doc extends the schema, the data-model doc and the example
instance change in the same commit too, and the instance README gains a numbered gap for it.

A design doc never carries an open-questions section. Every question goes to
`<project>/docs/OPEN-QUESTIONS.md` — create it from `assets/templates/OPEN-QUESTIONS.md` the
first time a question arises, before generation — and the doc carries one line pointing there
(`references/core/lessons.md §1`, lesson 5). A question inside a doc is the one place nobody
looks for it again. Editing that file alongside a design doc is normal; commit them together.
When a doc depends on a question still open, ask once; if no answer comes, write the doc on a
stated assumption, name it in the doc's first paragraph and its Decisions section, and move the
row's *Needed by* to the first thing the assumption would make expensive to change. A row the
user decides during the bootstrap is not deleted at once: mark it *decided* with the answer, so
the ADR backfill (§4, step 4a) writes its ADR and deletes the row then. Before the roadmap
exists, *Blocks* names the design doc that needs the answer, or the event that does ("the
first deployment") when no doc depends on it; a decided row keeps its question and says
*decided: <answer>* in *Needed by*. §4 step 4 rewrites every row to milestone and feature IDs
once they exist.

After finishing each doc, stop and post exactly:

> Review `<path>`. Say 'next' to continue or tell me what to change.

Do not start the next doc, or move on to the roadmap, until the user replies.

**(c) Roadmap (C8), its own session.** Decide phase 1's exit, then the current and next
milestones' goals and measurable exits; everything beyond those two is `sketch` — a goal
sentence and nothing more. Write `<project>/docs/roadmap.md` from
`assets/templates/roadmap.md`. At the standard tier the roadmap still carries `P1` as its one
phase and sketches anything after it; a single non-sketch phase is how the linter tells
standard from full. Decide the current and next milestones' feature lines here — ID and title —
ordered so that `M0-01` is claimable at once (no open-question row blocks it), and list them in
the gate message so the user reviews them now; they are written into the
milestone files at generation. Then apply the same review gate as (b): stop and post the message
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
   `references/core/tiers.md` lists which files each tier gets. Skip `assets/templates/CURRENT.md`;
   the linter writes that file. Copy the object templates `assets/templates/plan.md`,
   `assets/templates/milestone.md`, `assets/templates/adr.md` and `assets/templates/evidence.md`
   unchanged to `<project>/tools/templates/`; sessions copy and fill one each time they create a
   plan, a milestone, an ADR or an evidence file.
2. Copy `scripts/check_docs.py` to `<project>/tools/check_docs.py`, and
   `assets/templates/check_docs.toml` to `<project>/docs/.check_docs.toml` with the tier
   pinned, any history folders (docs-first, §6a) in `citation_exclude`, and any vendored
   bundle in `exclude`. The Stop hook is the user's choice: ask once, in the gate message that
   ends this session, not as a stop in the middle of it. If they want the linter to run at the
   end of every session without being remembered, and the kit is not installed as a Claude Code
   plugin (which already runs it), copy `scripts/hooks/stop.sh` to
   `<project>/tools/hooks/stop.sh` and wire it as `scripts/hooks/README.md` shows.
2a. Copy `assets/templates/gitattributes` to `<project>/.gitattributes` if the project has
   none, and add `tools/__pycache__/` to `<project>/.gitignore` if it is not there, so the
   linter's LF output and a Windows checkout never produce a mixed-ending diff. Add any secrets
   file the security doc names (`.env`, a key file) to the same ignore list.
3. Substitute every `{{token}}` using the table in `assets/templates/README.md`; values come
   from C0's answers, the brainstorm's decisions, the design docs, and the roadmap just written.
   Before any code exists, `{{commands}}` is the linter command plus one line naming the
   milestone that adds the rest; `{{rule}}` and `{{deferred}}` may each expand to several lines.
   A template line written as an instruction ("one line per top-level entry", "note what is
   test-first") is replaced by the content it asks for, never kept. Cite design docs by their
   full path from the project root everywhere, including the layout section of
   `<project>/AGENTS.md`; a bare filename resolves against the citing file's folder and fails.
   If a README already exists, keep whatever it offered a human that the template does not — a
   reading order, related repositories, a per-version map — and add the template's three
   sentences (what it is, for whom, its current state) and its "Where things are" table to it,
   rather than replacing it. Seed the glossary's areas from the profile's vocabulary table and
   the design docs' section headings.
3a. In docs-first and brownfield, write the pre-bootstrap document classification into
   `<project>/DOCS.md §1`: one line per file, its class, and the design doc that supersedes it.
4. Create the milestone files for the current and next milestone from
   `<project>/tools/templates/milestone.md`, with the feature lines decided at the roadmap gate;
   everything beyond stays `sketch` in the roadmap only. Copy the instance README's *held for
   M0* gaps into M0's notes. Rewrite every open-question row's *Blocks* and *Needed by* to the
   milestone or feature IDs that now exist. Add `<project>/docs/evidence/.gitkeep` so the empty
   directory is tracked. Create no plans: a plan is written at the Ground step of the session
   that claims its feature, never at generation.
4a. Backfill the ADRs. One per entry in the design docs' Decisions sections, from
   `<project>/tools/templates/adr.md`, dated today, with the source section under Related.
   Status follows who decided: a decision the owner made — in this bootstrap's conversation, or
   recovered from pre-bootstrap history — is `accepted`, with `**Deciders:**` "the owner" (or
   the note and its date, and `**Date:**` that date or `recovered`), because a human made it and
   asking them to re-decide it would be noise; a decision the bootstrap recommended is
   `proposed`, with `**Deciders:**` "bootstrap recommendation, not confirmed". Merge entries that
   stand or fall together into one ADR, even across docs. Keep the filename to the number plus
   at most sixty characters, cut at a word. Delete every open-question row marked *decided* as
   its ADR is written. Fill the backfill table in `<project>/docs/decisions/AGENTS.md` from the
   same list.
5. From the project root, run `python tools/check_docs.py --root . --fix` and fix whatever it
   reports. `--fix` writes the four generated files before it checks, so a clean project passes
   on the first run; a warning about an evidence file not written yet (`W005`) is expected
   until the milestone closes. Open-question rows that block a later milestone do not appear in
   `<project>/docs/CURRENT.md` until that milestone is listed; that is by design.
6. Commit, then end the session with the review-gate line for `<project>/AGENTS.md` and the
   milestone files, the hook question from step 2, and the ADRs awaiting acceptance. §5 starts
   when the user replies.

## 5. First session

Open `<project>/docs/CURRENT.md` and claim `M0-01`: copy `<project>/tools/templates/plan.md` to
`<project>/docs/plans/M0/M0-01-<slug>.md`, set `**Status:** in progress`, add a session stamp
in the form `<project>/docs/WORKFLOW.md §3` gives (`- <date>T<hh>:<mm>Z — <agent> — <branch>`,
UTC; `<agent>` is the tool's name, `claude-code`, `codex`, and `<branch>` the branch you are on,
the bootstrap branch at this point), fill the header's design-doc and ADR citations and the
Objective, delete the template's placeholder task line, and leave Current state and Tasks for
the Ground step. The header's `**Branch:**` field names the feature branch the work will use
once the bootstrap has merged (`feat/M0-01-<slug>`), not the branch of the stamp. Append the plan's path to the feature line in
`<project>/docs/milestones/M0.md`, and — because this is the milestone's first claim — set `M0`
itself to `in progress` in the same edit (`references/core/parallel-agents.md §1`). Run
`python tools/check_docs.py --root . --fix` so `<project>/docs/CURRENT.md` shows the claim, and
commit. The bootstrap ends here; the feature's Ground step is the next session's work unless
the user says to continue. Follow `<project>/docs/WORKFLOW.md` from there.

## 6. Brownfield variant

Follow the seven steps of `references/core/adoption.md §2`, in order: inventory;
reverse-engineer the architecture doc from the code; recover the data model and an anonymised
example instance; backfill ADRs from git history; write the design doc as a
vision-and-current-state document; build the roadmap from the issue tracker; generate, lint,
and open on a feature named "close the gaps the inventory found". Generation follows §4 steps
1 through 6. The same one-doc-per-session gate from §3 applies to every doc this variant
writes — stop after each one and post the review-gate message before continuing.

## 6a. Docs-first variant

Follow `references/core/adoption.md §4`. In outline:

1. **Inventory and classify** every existing document as *contract* (it becomes, or feeds, a
   design doc), *history* (a dated record of thinking: vision, journals, research, notes;
   frozen, never edited, cited as history), or *external reference* (someone else's material).
   A pre-existing README is none of these: it is merged at §4 step 3. Hold the classification
   in the scratch list; it is written into `<project>/DOCS.md §1` at §4 step 3a.
2. **Fix names and inbound links first**, in one commit, if any file will be renamed or moved,
   so no later doc cites a path that then changes. History goes under `<project>/docs/history/`
   unless it already has a folder of its own, keeping each file's name unless it breaks the
   naming convention, in which case a kebab-case name for what the file is
   (`<project>/docs/history/first-conversations.md`, `<project>/docs/history/market-notes.md`),
   never a date prefix. A plain-text mention of a moved file counts as an
   inbound link: relink it as a citation. This commit is the first on the bootstrap branch and
   carries the starting-SHA subject (§1a); it may share a session with step 3, since it writes
   no design doc.
3. **Reconcile instead of brainstorming from blank.** C1 becomes a reconciliation pass over the
   history: the decisions already taken (with their dates — an undated note's decisions take the
   note's commit date), the questions still open, and every contradiction between documents.
   Each contradiction is a decision the user makes before the design doc that depends on it is
   written; put them to the user one per message, hardest constraint first, as C1 would, unless
   the user batches. Settle the stack here too, as §3(a) says.
4. **Derive, and say what supersedes what.** Each design doc is derived from the history with
   citations back to it, and its first paragraph states what it supersedes ("supersedes
   `<project>/docs/history/<file>.md` for <topic>"). History is never edited to match.
5. **Keep the linter off frozen prose.** History folders go into `citation_exclude` in
   `<project>/docs/.check_docs.toml`, so an anchor that no longer resolves in a dated note never
   forces a rewrite of the record.

Then continue with §3(b): the profile's design docs, one per session, each behind its gate.

## 7. What this skill never does

- Write more than one design doc in a single session, unless the user explicitly says to —
  and then only as §3a describes, with the least-reviewed docs recorded.
- This skill never ticks a box; ticking happens in feature work, with verification evidence.
- Accept an ADR it wrote. An ADR the bootstrap recommends moves to `accepted` by human
  decision, never by this skill. An ADR that records a decision a human made — in this
  bootstrap's conversation, or in pre-bootstrap history — is written `accepted` (§4 step 4a),
  because the human decided it; the skill is recording, not accepting.
- Edit a generated file by hand (`<project>/docs/CURRENT.md`,
  `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`,
  `<project>/docs/decisions/README.md`); only the project's `tools/check_docs.py --fix` writes
  those.

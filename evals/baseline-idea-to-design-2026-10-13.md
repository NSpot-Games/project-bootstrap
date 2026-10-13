# Baseline: idea-to-design with no skill, 2026-10-13

Recorded before `skills/idea-to-design/` existed. The six scenarios (`raw-idea`, `tech-drift`,
`against-recommendation`, `nothing-new`, `consistency`, `handoff`) were prepared with
`harness.py prepare ... --label baseline --no-skill`, run once each by a fresh agent (model:
sonnet) working in its run's `project/`, and graded with `harness.py grade`. Every failure below
is a target: a behaviour `SKILL.md` has to produce. Runs are in `evals/runs/<scenario>/baseline/`.
No `timing.json` was kept; tokens and seconds come from the dispatch results.

| Scenario | Pass | Assertions | Tokens | Seconds |
|---|---|---|---|---|
| raw-idea | 2 | 6 | 64,555 | 39 |
| tech-drift | 3 | 4 | 65,207 | 34 |
| against-recommendation | 4 | 4 | 66,628 | 51 |
| nothing-new | 0 | 3 | 74,997 | 33 |
| consistency | 5 | 5 | 66,631 | 41 |
| handoff | 6 | 6 | 89,520 | 70 |
| **total** | **20** | **28** | **427,538** | **268** |

Two results need a caveat before they are read as evidence.

- **against-recommendation first graded 2/4, and both failures were harness false negatives.**
  The agent wrote the alternatives file in a Windows code page (the dashes are mojibake in the
  file), and the harness's `_read` returned an empty string for it. Commit `8cf9726` fixed the
  harness; the re-grade is 4/4, the figure in the table.
- **The handoff baseline is contaminated.** The agent read the idea-to-design spec in the kit
  repository, outside its project directory. Its 6/6 is not evidence that the skill is
  unneeded there; the scenario has to be re-judged once the skill exists, and ideally re-run
  with the spec out of reach.

## What failed

| Scenario | Failed assertion | What the agent did instead |
|---|---|---|
| raw-idea | the message compares the idea with things that already exist | It named tool libraries, Peerby, Nextdoor and Facebook/WhatsApp groups only inside a question, "what do you think they do badly?", handing the comparison to the user. |
| raw-idea | the message names what is new about the idea | It said what usually makes such apps fail (trust, density, breakage) but never what this idea adds; "that gap is the real product" was left for the user to find. |
| raw-idea | exactly one question is asked | Five numbered groups, about ten questions (place, goal and budget, lending terms, what exists, success in three months). It asked for "short answers" and stopped. |
| raw-idea | a recommendation is given | None. It listed options (deposit, ratings, insurance) without picking one, and promised a plan "once you answer". The one hint of a view, starting with a group chat, was in a to-do list, not an answer. |
| tech-drift | the database question is parked in the vision README | It answered at once ("I'd lean Postgres") and wrote a database note under docs/tech, a new, untracked, uncommitted file. the vision README has no parked item. The placement outside the vision docs was right; the answering and the missing parking were not. |
| nothing-new | the existing product is named | It never said Instagram. It restated the idea as "post square photos with filters, follow friends, like", then went to setup. |
| nothing-new | the message says plainly that it already exists | No word that the idea is an existing product. It treated the repository as greenfield and the idea as a given. |
| nothing-new | at least two angles are offered | None. It picked up the installed `project-bootstrap` skill instead: "Question 1 of 5: name and codename", with `new-idea` as a default. This is the main finding of the scenario: with a skill about setup in reach, the agent did setup and did not look at the idea. |

## Non-targets

- **consistency passed 5/5 without the skill.** The agent found all three contradictions (the
  starter bundle of 3 tools against the limit of 2; "late" after 5 days against 7-day loans; the
  README's stale "free for everyone" against the £2 membership), fixed the stale summary, and
  left the other two for the owner. It is a regression guard for the skill, not a target.
- **against-recommendation, 4/4 after the harness fix.** The agent accepted the request board
  with no argument, recorded the map as "not taken" in the alternatives file, committed, and moved on.
- **handoff, 6/6, contaminated** (see above).

## Seen but not asserted

- **Several questions at once, in raw-idea.** Ten questions in five groups, plus a plan of what
  it would do afterwards. A person with a raw idea gets a form.
- **No recommendation next to the question in raw-idea.** Options were listed with no pick. The
  agents in against-recommendation and tech-drift did recommend; the pattern is that they do so
  when there is a document to anchor on and not when there is only an idea.
- **The agent answers the user's technical aside rather than parking it (tech-drift).** It chose
  Postgres, argued for it against Firebase, and left a doc nobody asked for. It did return to the
  open question with a recommended option, which is good.
- **The technical note is untracked (tech-drift).** a database note under docs/tech was written and not
  committed, so the working tree was left dirty.
- **the final-message file swept into commits.** In against-recommendation and consistency the
  agent's own commit contains the final-message file. This is a harness artefact (the file is the
  message handed to the grader) and not an agent fault, but a skill's commit step should name
  the files it stages.
- **consistency asked about two fixes instead of making them.** The agent fixed the one that
  had a single right answer and asked about the other two. Whether a skill should ask or choose
  and report is a design call; the baseline shows asking is the agent's default.
- **against-recommendation re-argued the choice in a softer way.** It accepted the board, then
  noted the cost to the "under a minute" pillar and offered to reword it. This is acceptable,
  and the assertion about counter-argument passed, but the line is thin.
- **The handoff agent offered a prototype as an alternative** to bootstrap ("the alternative is
  to go straight to a first prototype"), while recommending bootstrap, and it asked to start
  bootstrap with a proposed name. Fine, but it came from reading the spec.
- **Mojibake in files.** Non-ASCII dashes were written in a Windows code page in
  against-recommendation. A skill should keep the documents ASCII-safe or say UTF-8.

## Failure classes

Each failure and each "seen but not asserted" behaviour, classified with writing-skills' "Match
the Form to the Failure", and where `skills/idea-to-design/SKILL.md` answers it.

| Behaviour (scenario) | Class | Form used | Where |
|---|---|---|---|
| No comparison with existing products; handed to the user (raw-idea) | shape | recipe: the first message's parts in order, part 2 "What already exists", named by the agent | step 1 |
| No hook named (raw-idea) | omitted element | required part 3 of the first message, opening "What is new here is…"; "The hook" slot in the vision README template | step 1; `assets/templates/vision-readme.md` |
| About ten questions in five groups (raw-idea) | shape | recipe: "That is the whole message. It holds one question, as its last line." Question messages get the same five-part shape | steps 1 and 3 |
| No recommendation when only the idea exists (raw-idea; seen in the pattern across scenarios) | omitted element + conditional | required "(my recommendation)" option first; conditional "When only the idea exists, the reason rests on the idea itself" | steps 2 and 3 |
| Hijacked into project-bootstrap setup on a raw idea (nothing-new) | shape + trigger | ordering recipe: the first message comes before any setup, setup is step 9; trigger description kept as the brief wrote it | step 1 opening paragraph; description |
| Instagram not named, no "it exists", no angles (nothing-new) | conditional | keyed to "If the products in part 2 already do everything the idea describes": the verdict naming the product, then 2–3 lettered angles with a recommendation | step 1 |
| Technical question answered with a pick, "I'd lean Postgres" (tech-drift) | discipline | firm rule ("not as a lean, not as a provisional pick"), rationalization table in the agent's words, red flag | step 7; Red flags |
| Parked in a `docs/tech` note, not under "Parked for later" (tech-drift) | conditional + omitted element | reply recipe keyed to "If the person asks a technology question before the design is agreed"; the README template's "Parked for later" slot | step 7; `assets/templates/vision-readme.md` |
| Technical note left untracked (tech-drift) | shape | commit recipe: `git add` the changed vision files by name, then commit; step 7 part 3 commits the README change | steps 5 and 7 |
| Final-message file swept into commits (against-recommendation, consistency) | shape (harness artefact) | same commit recipe: stage by name | step 5 |
| Consistency pass asked two questions in one message (consistency) | shape | recipe in the reference: the report lists all findings, the message asks about the first, as its last line | `references/consistency-pass.md` §6 |
| Re-argued the choice softly (against-recommendation) | discipline, borderline; assertion passed | no new wording; Conduct keeps "taken at once in one line" | Conduct |
| Prototype offered at handoff (handoff) | not a failure | no change; step 9 already offers it | step 9 |
| Mojibake in written files (against-recommendation) | omitted element | a line in the write recipe: "Files are written as UTF-8." | step 5 |

Draft wording removed because a recipe replaced it or the baseline did not need it: step 1's
"Do not design a copy." and "Ask nothing else until the hook is stated." (replaced by the
first-message recipe, which also holds the purpose question the raw-idea scenario expects);
Conduct's "One question per message…" (now the step 3 recipe) and "The person's words decide…"
(against-recommendation passed without it; folded into the remaining Conduct line).

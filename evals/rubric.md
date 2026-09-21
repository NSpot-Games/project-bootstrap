# Rubric for a full bootstrap run

Scores one end-to-end run of the skill on a real or invented project: the acceptance test for
a release, complementing the per-step scenarios in `evals.json`. It is project-agnostic; the
rows come from the kit's own rules, each cited. Score every row `fine`, `stretched` (the rule
was followed in letter but not in spirit, or with a workaround) or `violated`. Two headline
numbers come out: the fine / stretched / violated count, and the number of improvisations —
points where the procedure did not say what to do and the agent decided alone.

## Procedure

| # | Rule | Where |
|---|---|---|
| P1 | The classification is announced in the skill's words before anything is written: greenfield, docs-first or brownfield | `SKILL.md §1` |
| P2 | The pre-bootstrap state is a commit; work runs on `bootstrap/<codename>`; the first branch commit names the starting SHA; one commit per step; no branch rule in the project's files | `SKILL.md §1a` |
| P3 | The five setup questions are asked one per message, in order, with the recommendation each carries, and nothing is written before all five are answered | `SKILL.md §2` |
| P4 | The brainstorm ends in a list of decisions and open questions and writes no file | `SKILL.md §3(a)` |
| P5 | One design doc per session, in the profile's order, each followed by the verbatim review-gate line, and nothing further until the user replies | `SKILL.md §3(b)` |
| P6 | The example instance (or the profile's equivalent) is written before the docs that depend on it | `references/core/adoption.md §1`, C4 |
| P7 | The roadmap has its own session and gate; current and next milestones `planned` with measurable exits, everything beyond `sketch` | `SKILL.md §3(c)` |
| P8 | Generation follows §4 in order: tier files, object templates, linter and config, gitattributes, tokens filled, milestone files, `--fix` green on the first run | `SKILL.md §4` |
| P9 | The first session claims `M0-01`, flips `M0` to `in progress` in the same edit, regenerates the indexes | `SKILL.md §5` |
| P10 | The skill never ticks a box, accepts an ADR, or hand-edits a generated file | `SKILL.md §7` |

## Output

| # | Rule | Where |
|---|---|---|
| O1 | Every design doc has the header (Project, Status, Audience, Related), numbered sections and a closing changelog | `references/core/doc-kinds.md §3` |
| O2 | Every status is inside its vocabulary | `references/core/layers.md §3` |
| O3 | IDs never reused or renumbered; status lives in one place; the four generated files carry the marker and match `--fix` | `references/core/layers.md §1`, `§4` |
| O4 | The roadmap has no checkboxes; the rolling wave holds | `references/core/doc-kinds.md §2`, `references/core/long-horizon.md §1` |
| O5 | Each planned or in-progress milestone holds 3–10 features | `references/core/layers.md §5` |
| O6 | No plan exists for an unclaimed feature; the claimed plan is filled, not a stub | `references/core/layers.md §1` |
| O7 | The declared tier matches the linter's, and the file set matches the tier | `references/core/tiers.md §1` |
| O8 | The glossary is seeded with the profile's vocabulary and the design docs' areas, and terms cite where they live | `assets/templates/GLOSSARY.md` |
| O9 | One open-questions file; no design doc has an open-questions section; each doc points at the file | `references/core/lessons.md §1`, lesson 5 |
| O10 | ADRs are `proposed`, never accepted by the agent; the backfill list is filled from decisions the design docs already state | `SKILL.md §7`, `assets/templates/decisions-AGENTS.md` |
| O11 | `<project>/docs/CURRENT.md` is generated, under forty lines, and points the next session at real work | `references/core/long-horizon.md §7` |
| O12 | Evidence paths cited by unfinished milestones are real paths (a warning, not angle-bracketed), and the profile's vocabulary is used in headings and prose | `references/core/doc-kinds.md §3`, `references/profiles/<name>.md §3` |
| O13 | Docs that existed before the bootstrap are classified in `<project>/DOCS.md` and left unedited; the naming convention is applied with inbound links fixed | `references/core/adoption.md §4`, `SKILL.md §2` |
| O14 | The linter reports zero errors at the end, and every warning is one the procedure names as expected | `SKILL.md §4` |

## Improvisations

List every point where the agent had to decide something the procedure did not cover, with
the section that should have covered it. The count is the headline number; the list is the
input to the next release. An improvisation the agent got right is still an improvisation.

## Scoring a run

1. Run `python tools/check_docs.py --root .` in the project; record the output.
2. Walk the commits in order; score P1–P10 from what each commit and each message shows.
3. Read the final tree; score O1–O14.
4. Take the agent's own list of improvisations, add any the reviewer saw that the agent did
   not, and count.
5. Record fine / stretched / violated and the improvisation count in a dated results file
   next to this rubric, with one line of evidence per row that is not `fine`.

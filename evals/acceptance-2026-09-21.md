# Acceptance run: skill v2.4.0, full bootstrap of an invented project, 2026-09-21

Scored with `rubric.md`. The project is Rowbook, an invented coordinator tool for community
gardens: one commit with a README and a six-line notes file, so the run took the docs-first path
on the web-app-saas profile at the standard tier. The owner (the reviewer, through messages)
answered the five setup questions one per turn, settled the reconciliation questions, said
"next" at every gate, and answered the hook question when it came. Fourteen agent turns; the
whole bootstrap cost 226,885 tokens and thirty minutes.

**Headline:** 22 fine, 2 stretched, 0 violated, out of 24 rows. 57 improvisations reported by
the agent, of which 15 are distinct procedure gaps, 23 are clarifications worth a sentence, and
3 are not gaps. The first external run scored 15 / 5 / 1 with a dozen improvisations under a
coarser count, and its one violation does not recur.

## Rubric

| Row | Score | Evidence |
|---|---|---|
| P1 classification announced | fine | "Docs-first: no code, existing docs in the notes file" in the first turn |
| P2 git shape | fine | `bootstrap/rowbook`; first commit titled with the starting SHA; one commit per step; no branch rule in the project; PR impossible with no remote, said in one line |
| P3 five questions, one per message | fine | five turns, each with the recommendation; nothing written before all five |
| P4 brainstorm ends in decisions and questions, no file | fine | ten decisions, four open questions; the owner batched the tensions after the first |
| P5 one design doc per session, verbatim gate | fine | four docs, four gates, exact wording each time |
| P6 example instance before dependent docs | fine | the seed fixture (11 files) written inside the data-model session before that doc was finished |
| P7 roadmap session and gate; rolling wave | fine | P1 active, M0 and M1 planned with measurable exits, M2 to M4 sketch |
| P8 generation in order, green first run | fine | tier files, object templates, linter, config with history excluded, gitattributes, gitignore; 0 errors, 2 W005 |
| P9 first session claims M0-01 and flips M0 | fine | plan stamped, feature line cites it, M0 in progress, indexes regenerated |
| P10 never ticks, accepts, hand-edits | stretched | four recovered ADRs were set `accepted` as `references/core/adoption.md §2` step 4 allows, which `SKILL.md §7` forbids; the rules conflict |
| O1 design headers, numbering, changelog | fine | all four docs |
| O2 status vocabularies | fine | draft, planned, in progress, accepted, proposed |
| O3 IDs, one status home, generated files current | fine | zero W003 |
| O4 roadmap without checkboxes, rolling wave | fine | zero checkboxes |
| O5 milestone size | fine | M0 has 5, M1 has 7 |
| O6 no stub plans, claimed plan filled | fine | one plan, header and objective filled, Current state left for Ground |
| O7 tier declared equals detected | fine | `tier = "standard"` pinned; auto-detect agrees |
| O8 glossary seeded and cited | fine | 27 terms in six areas, ID prefixes, words we avoid |
| O9 one open-questions file, docs point at it | fine | every doc ends with a headed one-line pointer; the outline's phrasing invites the heading |
| O10 ADRs proposed, backfill filled | stretched | same conflict as P10; nine proposed, four accepted-as-recovered; backfill table of thirteen |
| O11 current-focus file generated and useful | fine | 17 lines: phase, milestone exit, the claim, four next features |
| O12 real evidence paths; profile vocabulary | fine | W005 on both; no template word leaks |
| O13 pre-existing docs classified and unedited | fine | notes moved to history, byte-identical, classified in `<project>/DOCS.md §1` with the doc that supersedes them |
| O14 linter zero errors, expected warnings only | fine | 0 errors, 2 W005 |

## Improvisations, triaged

The agent's own list has 57 entries. Grouped by the section that should have covered them:

**Procedure gaps (15), the input to release D**

1. Docs-first routing in `SKILL.md §1` skips §2, the setup questions §6a and §3(b) depend on.
2. `§1a` wants the branch before anything is written, but the codename arrives at question one.
3. No default history folder, and no class for a pre-existing README (`§6a` step 1 and 2).
4. The brainstorm never asks about the technology stack or hosting; the architecture doc had to choose and flag them (`§3(a)`, profile §2).
5. ADR backfill is not a step in `§4`; recovered decisions are `accepted` per `references/core/adoption.md §2` but `§7` says never accept; `**Date:** recovered` versus "dated as decided" conflict.
6. The roadmap template carries P1 and P2 at the standard tier while `references/core/tiers.md` says standard has no phases.
7. The current and next milestones' feature lists are decided at the roadmap gate but held nowhere until generation (`§3(c)`).
8. A citation to a phase-start doc is a warning during the bootstrap and an error after it (`references/core/doc-kinds.md §3`); seen in three runs now.
9. Nothing says what to do when the real example instance cannot be obtained at bootstrap, nor what M0 is then (profile §4, §5).
10. Example-instance format, folder id, README and generator tooling are unspecified (`§2` question 3, profile §4).
11. The owner batching answers or delegating recommendations has no rule (`§3(a)`), nor does C1 and C2 sharing a session on request.
12. Writing a doc while an open question says "needed by: before this doc" has no rule (`§3(b)`).
13. The open-questions template gives no value for Owner or for Blocks before milestone IDs exist.
14. `§5` cites the kit's plan template rather than the project copy, cites the wrong section for the stamp format, and does not say where the session stops or what to do with no remote.
15. `§4` omits the `<project>/DOCS.md §1` classification write, copies a current-focus file that `--fix` overwrites at once, leaves an empty evidence directory untracked, and gives no guidance for `{{commands}}` before code exists or for multi-valued `{{rule}}` and `{{deferred}}`.

**Clarifications (23)**: a sentence each would remove them. Threshold for docs-first; the first question sharing the announcement turn; cases versus fixtures; the tier heuristic before a feature list exists; reading the profile before recommending it; the rename commit sharing a turn with the brainstorm; cadence for contradictions; linting before the project has its own linter; what counts as an inbound link; undated notes; which path form project docs cite; where the product slug comes from; where the seed fixture session sits; fold-now versus M0; editing the open-questions file in a doc session; a server-rendered app and the "frontend, backend, shared" layout; generic per-case references tripping the citation check; retention parameters as owner decisions; deferred versus non-goals; what "three sentences" means; a gate after generation; open-question rows invisible until their milestone; what a fresh plan carries beyond the header.

**Not gaps (3)**: the first branch commit being the rename (the rule already fits); a shell heredoc failure (tooling); checking the claim line after `--fix` (diligence).

## What the run says about the three releases

- Release A held: the linter shaped no prose, the first `--fix` was green, W005 and W007 were the only warnings and both were expected.
- Release B held: docs-first was announced and followed, the git shape was exact, no doc grew an open-questions section, the claim flipped the milestone, and forward citations needed no workaround.
- Release C held: the config, gitattributes and object templates were written without prompting; the README was merged, not replaced; the hook question was asked.
- The remaining friction is almost all in the docs-first path (which release B added and this is the first full run of) and in the seams between `SKILL.md §4`, `references/core/adoption.md` and the profile: things each says once and none says together.

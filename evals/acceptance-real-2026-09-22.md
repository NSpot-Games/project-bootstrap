# Acceptance run on a real repository, skill v2.6.0, 2026-09-22

The first run of the finished skill on a repository it had not seen, scored with `rubric.md`
like the three invented runs. The repository is a real project of the kit's owner; this file
records only the shape of the run and its numbers, never the project's content, and nothing
from it enters the kit. The run happened in a scratch clone with its remote removed, so nothing
could be pushed; the real repository was not touched.

**Shape of the run.** Docs-first: no product code, forty-six existing documents in three
folders (vision, dated research reports, one external note), a vendored design bundle with
component source, and a pre-existing agents file carrying a review workflow. Profile
curated-directory, the seventh profile release C added for exactly this class of product, plus
an architecture doc borrowed from web-app-saas. Tier standard. The reviewer acted as owner at
every gate, delegated the product decisions the owner alone could make, and left two rows for
the founder rather than answering them on their behalf. Twenty agent turns, thirteen commits,
eight phase-one design docs, seventy backfilled ADRs, a green linter at zero errors and zero
warnings. Cost: 490,624 tokens and 48 minutes, roughly twice an invented run, in proportion to the
material read.

## Rubric

| | Invented project, third run (v2.6.0) | Real repository (v2.6.0) |
|---|---|---|
| fine / stretched / violated | 23 / 1 / 0 | 23 / 1 / 0 |
| improvisations reported | 31 | 40 |
| of which procedure gaps | 0 | 7 |
| linter at the end | 0 errors, 0 warnings | 0 errors, 0 warnings |

The stretched row is the same one as in the third invented run: milestone evidence written
as a sentence rather than a path, so the expected warning never fired. The milestone template
should say "a path" in one sentence.

Everything else scored fine, including the rows the first external run failed or stretched:
the classification was announced in the skill's words; the numbered research files were
renamed with their inbound links fixed in the first commit; the frozen history was never
edited beyond those links and was excluded from the citation check; every design doc has its
header, Decisions section, pointer and changelog; no design doc has an open-questions section;
the pre-existing agents file was merged, not replaced; the seventy ADRs were split into
fifty-five accepted (recovered or owner-made) and fifteen proposed; the roadmap gate listed
eighteen feature lines with their exits for review; generation ended with a gate; the first
claim flipped the milestone.

## The seven gaps, all in the profile layer

The forty reported improvisations triage into seven distinct procedure gaps, twenty-seven
clarifications and four that are not gaps. Every gap is in the seams between the
curated-directory profile and the procedure, which had never been exercised together:

1. **The curated-directory profile has no architecture doc.** For a repository whose richest
   document is architecture, the run had to borrow one from web-app-saas. The profile's
   outline should carry its own.
2. **The example entry is placed twice.** The profile makes it a design doc; the procedure makes
   it a data folder with a README that holds the gaps. The run did both, in two sessions. The
   profile's row should say the doc is the walkthrough that cites the folder, and the gaps live
   in the folder's README; the same applies to the data-driven-product profile.
3. **A pre-existing agents file has no merge rule.** The README has one; the agents file does
   not. The run kept its non-negotiables as rules and moved its workflow into the workflow doc
   as an appended section, recorded as an ADR. That should be the rule.
4. **The roadmap template's fixed IDs do not fit a long first phase.** Eight sketched
   milestones in phase one pushed the template's sketched second-phase milestone from its
   printed number to the next free one. The template should say IDs continue.
5. **Profile outlines still position the open-questions pointer** in the middle of the outline
   while the procedure puts it after the Decisions section. Drop the pointer entries from the
   outlines; the procedure already mandates it.
6. **Project docs must never cite kit files.** A citation to a reference or to the skill file
   resolves during the bootstrap and breaks after installation elsewhere. One sentence in the
   procedure's path rules.
7. **The profile line with a borrowed doc needs the doc's full project path**, not a bare
   filename, or the linter reads it as a broken citation. One word in the composition rule.

Two clarifications deserve a sentence too: a vendored design reference with component source
is not code for the purpose of classification, and a renamed history file keeps its old title.

## What this run says

The three invented runs measured the procedure; this one measured the procedure meeting a
profile and a repository shape it had never met. The procedure held: zero of the seven gaps is
in the setup, the git shape, the gates, generation or the first session. All seven are where
a profile's outline and the procedure's rules say slightly different things, which only a
profile's first real use can find. A release F closing them is about a day of text and one
rerun; the runs that would find the next such seams are the first real use of each remaining
profile.

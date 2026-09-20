# Audit: project-bootstrap v2.1.0 on the Merindar run (2026-09-20)

The skill was run end to end on `NSpot-Games/merindar` (greenfield in code, ~20 vision and research docs already present; solo founder; tier `full`; profile `data-driven-product` plus a borrowed security-and-privacy doc). The output is reviewable as one piece in merindar PR #1. Two inputs feed this synthesis: the running agent's first-hand notes (`2026-09-20-merindar-run-firsthand.md`) and an independent review of the skill's rules against the output (`2026-09-20-merindar-run-review.md`, with reproductions). This file is the verdict and the ranked changes.

## 1. Verdict

The skill produced a usable docs-as-contract repo: seven design docs with headers and changelogs, an example instance that exposed 15 schema gaps, a rolling-wave roadmap with phases, two planned milestones, a grounded first plan, a glossary, a single open-questions file, generated indexes and `CURRENT.md`, a green linter, and a first session claimed. Where the output is good it is because the procedure forced the right artefacts in the right order; the example-instance-first rule alone paid for the run.

It also cost the agent a dozen improvisations the skill should have made for it, and the linter shaped content in ways nobody intended. The most serious defects are in the linter's contract with the rules (a documented tier it cannot see, false-positive citations that deleted useful content, a `CURRENT.md` that was empty at the moment it mattered) and in a missing adoption path for repositories that already have docs.

Compliance: 15 rules fine, 5 stretched, 1 violated (open questions duplicated in every design doc, caused by the profiles contradicting `lessons.md`).

## 2. What the run exposed, grouped

**Procedure**
- No path for "no code, rich docs". Greenfield assumes a blank brainstorm; brownfield assumes code. The agent invented the reconciliation: vision = history, design docs = contract, a supersession rule, a DOCS.md classification for folders the kit has no kind for.
- No git guidance. The founder asked mid-run for a branch, a PR and the pre-bootstrap commit; the run then wrote a transitional branch rule into `AGENTS.md` and `WORKFLOW.md` that expires at merge.
- Claiming a feature does not flip its milestone, and `gen_current()` only lists features of `in progress` milestones, so `CURRENT.md` said "next unclaimed: none" with five features waiting.
- The one-doc-per-session rule has an exception ("unless the user says so") but no procedure for it; the run wrote four docs back to back and nothing recorded which got less scrutiny.
- Borrowing a doc from another profile has no rule. The data-driven-product vocabulary (player, playtest, centrepiece) fits a guide poorly; a curated-directory profile would fit this class of product.
- Plugin install needs a reload before the skill is visible; the README does not say so.

**Templates**
- Every profile's design-doc outline prescribes an "open questions" section, contradicting `lessons.md` §1.5; the run ended with 25 in-doc questions and 14 central rows.
- The milestone template puts the plan path on every feature line, so E001 fails until a plan exists; the run created twelve stub plans that now dominate the plans index. `**Evidence of exit:**` cites a file that cannot exist before close.
- The WORKFLOW stamp hint uses `{{date}}T{{hh}}:{{mm}}Z`, which E005 flags if left; format hints and substitution tokens share one syntax.
- `decisions-AGENTS.md` says "see `adr.md`", which is not copied into the project.
- `PROJECT-README` is three sentences; a repo with an existing README gets no merge rule, and the run dropped the old reading table under E001 pressure.
- No `docs/.check_docs.toml` template; five of seven keys are documented only in the Python source. No `.gitattributes` or `.gitignore`; 17 files landed CRLF including an unwired `stop.sh`.

**Linter**
- `full` is unknown to `detect_tier()`; pinning it disables every milestone, plan, dependency and claim check and turns sketch sections into E005 (reproduced: 23 findings, 0 milestones). The run stayed green only by not declaring its tier. `minimal` is returned and documented nowhere.
- `--fix` checks before it generates: the first run reports E001 for the four generated files, the second passes.
- Markdown link text is parsed as a citation (`[IDEA.md](docs/vision/IDEA.md)` fails). E002 fires on citations to numbered list items (`technology.md §1.6`), which forced rewrites of a frozen historical audit.
- No check of `**Status:**` vocabulary (a typo silently removes a file from E007/E009), of the design header, of a closing `## Changelog`, of milestone size, of `AGENTS.md` length; no phase checks at all. None of the 63 tests covers these.
- The plugin Stop hook blocks on a red linter, which is the normal state during a multi-session bootstrap.

**Output quality**
- Next-session-ready: `example-casa-din-vale.md` (15 numbered gaps), `M0-01`'s plan, `OPEN-QUESTIONS.md` (it collected founder actions scattered across three docs), the glossary.
- Clutter: twelve identical stub plans; the profile's game headings on a guide.
- `CURRENT.md` would be more useful with the in-progress milestone's exit criteria and the open questions that block a listed feature.

## 3. Changes, ranked

| # | Change | Where | Size |
|---|---|---|---|
| 1 | Make `full` a real tier: `detect_tier` returns it from config or from `P<n>` headings; every `== "standard"` guard becomes `in ("standard", "full")`; E012 on an unknown tier; phase checks at full; document or drop `minimal`; a consistency test that `tiers.md` names exactly the tiers the linter returns | `scripts/check_docs.py`, `references/core/tiers.md`, tests + `tests/fixture/full/` | L |
| 2 | Fix citation false positives: skip the `[...]` span of markdown links; accept a numbered list item for `§N.M` or downgrade to a warning; a `--bootstrap` flag or `allow_missing` config that makes E001 a warning under `docs/plans/`, `docs/evidence/`, `docs/design/` while the procedure runs | `scripts/check_docs.py`, tests | M |
| 3 | `--fix` generates first, then checks | `scripts/check_docs.py` `run()` | S |
| 4 | A docs-first adoption variant: inventory and classify existing docs (contract / history / research / external reference) into `DOCS.md`; a reconciliation pass instead of a blank brainstorm; supersession rule stated in each design doc; renames and inbound links fixed in one commit first | `references/core/adoption.md` §4, `SKILL.md` §1 and a new §6a, `assets/templates/DOCS.md` | M |
| 5 | Claim flips the milestone: WORKFLOW §3 and SKILL §5 say the first claim in a milestone sets it `in progress`; `gen_current` additionally lists the first `planned` milestone's features, the in-progress milestone's exit criteria, and open-questions rows whose *Blocks* names a listed feature | `assets/templates/WORKFLOW.md`, `SKILL.md`, `scripts/check_docs.py`, `references/core/long-horizon.md` §7 | S |
| 6 | Open questions as pointers: remove the section from every profile's outline, replace with "one-line pointer to `docs/OPEN-QUESTIONS.md`"; profile composition rule ("plus <doc> from <profile>", listed in DOCS.md and on AGENTS' Profile line) | all `references/profiles/*.md` §2, `references/profiles/README.md` §3, `assets/templates/AGENTS.md` | S |
| 7 | Status-vocabulary and design-doc checks: E013 status outside vocabulary; E014 design header missing or bad status; E015 no `## Changelog`; W004 milestone outside 3–10 features; W006 `AGENTS.md` over 120 lines | `scripts/check_docs.py`, tests, `references/core/doc-kinds.md` §3 | M |
| 8 | Stub-plan policy: either a feature line cites its plan only once it exists (linter warns, not errors, on a missing plan for an unticked feature), or a minimal stub form exists and the plans index lists stubs under "Not yet grounded" | `references/core/layers.md` §1, `assets/templates/plan.md`, `scripts/check_docs.py` | S |
| 9 | Git guidance: a `SKILL.md` §0 — record the pre-bootstrap commit, branch `bootstrap/<slug>`, commit per step, one PR; never write transitional branch rules into `AGENTS.md`/`WORKFLOW.md`, or add an open question to remove them at merge | `SKILL.md`, `references/core/parallel-agents.md` §5 | S |
| 10 | Ship `docs/.check_docs.toml` as a template with every key commented; SKILL §4 writes it, naming `citation_exclude` for historical folders and `exclude` for vendored bundles | `assets/templates/`, `SKILL.md` §4 | S |
| 11 | Repository hygiene at generation: `.gitattributes` (`* text=auto eol=lf`, `*.sh text eol=lf`), `.gitignore` entries for `__pycache__`; skip the project Stop hook when the plugin is installed | `SKILL.md` §4, new template, `scripts/hooks/README.md` | S |
| 12 | Compressed-bootstrap mode: when the user asks to finish in one sitting, write docs in dependency order, one review gate per group, and record which docs got least scrutiny as an open question | `SKILL.md` §3b, §7 | S |
| 13 | Template fixes: format hints as `<date>T<hh>:<mm>Z` not `{{ }}`; copy the ADR template into `docs/decisions/` or inline it; `PROJECT-README` gains a "Where things are" table and a merge rule for an existing README; the glossary scaffold seeded with the profile's areas | `assets/templates/*` | S |
| 14 | Plugin Stop hook warns instead of blocks until `docs/CURRENT.md` exists | `hooks/stop.sh`, `scripts/hooks/stop.sh`, tests | S |
| 15 | README: say that a plugin install needs `/reload-plugins` or a restart before the skill is callable | `README.md` | S |
| 16 | A `curated-directory` profile (entities with provenance, editorial rules, a public site, an internal tool, a legal/privacy doc by default) for guides, directories and catalogues; vocabulary: visitor, session, key moment | `references/profiles/curated-directory.md`, `references/profiles/README.md` | M |
| 17 | Tests for every item above, plus CRLF input and the link-text case | `tests/` | M |

Items 1, 2, 3, 5 and 7 are linter correctness and should ship together as one release; 4, 6, 9, 12 are procedure; the rest are templates and hygiene. Doing 1–7 would have removed every improvisation in this run except the profile fit.

## 4. What to keep

The procedure's order (name → naming → example location → tier → profile; example instance before runtime and architecture; roadmap with a rolling wave; generation last; lint; claim). The design header and changelog rule. The single open-questions file (once the profiles stop contradicting it). The generated `CURRENT.md`. The review-gate wording. The refusal to accept ADRs or tick boxes. Nothing in the run argued for changing any of these.

# First-hand findings from running project-bootstrap v2.1.0 on Merindar

Recorded by the agent that ran it, before reading the independent review.

## Procedure (SKILL.md, adoption.md)

1. **No path for "greenfield in code, rich in docs".** Merindar had 1.2 MB of vision and research before the skill ran. Greenfield's C1 assumes a blank brainstorm; brownfield assumes code. The agent improvised: "the vision folder is the brainstorm output; design docs are derived from it." Needed: a third classification (docs-first greenfield) with steps: inventory existing docs, classify each as design/decision/direction/reference/history, map them to the profile's docs, extract decisions and open questions, then write the design docs as derivations with citations back.
2. **No git strategy.** The founder asked mid-run to move all bootstrap output onto a branch with a PR and to record the pre-bootstrap commit. SKILL.md §1 should start with: record `git rev-parse HEAD`, create `bootstrap/<slug>`, open a draft PR, commit after each step.
3. **Claiming a feature does not flip its milestone.** `gen_current` lists "next unclaimed features" only for milestones with status `in progress`; SKILL.md §5 says "claim M0-01" and nothing about the milestone, so `docs/CURRENT.md` said "none" with five features waiting. Either the claim step sets the milestone to `in progress` (rule in WORKFLOW §3 and SKILL §5) or the generator should consider the first `planned` milestone.
4. **Every feature line cites a plan path, and E001 fails until the plan exists.** The milestone template puts the path on the line; the linter resolves it. The run created twelve stub plans at `grounding` to pass. Either the linter treats an unticked feature's missing plan as a warning, or the skill says to create stubs, or the template omits the path until claim.
5. **Evidence of exit cites files that cannot exist yet.** `**Evidence of exit:** docs/evidence/x.md` fails E001 until close. The template should show the `<name>.md` convention or the linter should exempt that field until the milestone is `done` (E007 already checks it then).
6. **Tier `full` is documented but unknown to the linter.** `detect_tier` returns standard / lite / minimal; `tier = "full"` in the toml would load no milestones. Either alias full → standard in the linter or drop `tier` from the config docs.
7. **One-doc-per-session vs a founder who wants to finish.** The skill allows an explicit override; the founder used `/goal`. Worked, but the review-gate message could offer the choice up front ("say 'all' to write the rest without gates").
8. **Borrowing a doc from another profile** (security-and-privacy) has no rule. profiles/README could say optional docs may be borrowed and must be listed in DOCS.md §1.
9. **The data-driven-product vocabulary (player, playtest, centrepiece) fits a guide poorly.** A "curated-directory / content platform" profile (entities with provenance, editorial rules, a public site, an internal tool) would fit Merindar and many directories better.
10. **Plugin install needs a reload** before the skill is visible; README's install section should say `/reload-plugins` (or restart).

## Templates

11. **WORKFLOW.md's stamp example uses `{{date}}T{{hh}}:{{mm}}Z`** as a format hint; left as-is it fails E005. Format hints should use `<date>T<hh>:<mm>Z`, reserving `{{ }}` for tokens to substitute.
12. **decisions-AGENTS.md says "Template: See `adr.md`"** but `adr.md` is not copied into the project. Inline the template or copy it as `docs/decisions/_template.md`.
13. **PROJECT-README is three sentences**; a repo with an existing README needs a merge rule ("keep the existing map, add the three sentences and the pointers").
14. **GLOSSARY.md's `{{Area}}` scaffold gives no hint of the areas a profile implies**; the profile could seed them (entities, trust, pipeline, geography for this run).
15. **No `.gitattributes`** (`* text=auto eol=lf`) in the generated set; on Windows every commit prints CRLF warnings and the linter's `\r\n` normalisation hides the issue until someone diffs.

## Linter

16. **`--fix` checks before it generates.** The first run reports E001 for `docs/CURRENT.md` and the three READMEs, then creates them; a second run passes. Generate first when `--fix` is set.
17. **Link text as a bare filename is a false positive.** `[IDEA.md](docs/vision/IDEA.md)` fails E001 because the bracket text matches CITE_RE. Exclude tokens preceded by `[` or followed by `](`.
18. **Historical docs need `citation_exclude`** and the config keys are documented only in the script's docstring. Document `docs/.check_docs.toml` in the hooks README or DOCS.md template, and have SKILL.md generation write it.
19. **No check that a design doc has the header line and ends with `## Changelog`**; no check of `**Status:**` vocabulary on milestones and plans; no check that `Related:` cites resolve (they do via E001, fine) — add E0xx for header/changelog/status vocabulary.
20. **Sketch detection when a phase is `sketch` but a milestone under it has no status line**: worked here; add a test.
21. **`minimal` tier** is returned by the linter and documented nowhere.

## Quality of the output the skill drove

22. The design docs are useful because they were derived from a deep vision; on a truly blank project the profile's section outlines would produce thinner docs. The profile could ask for the example instance's walkthrough to be written before §7 (centrepiece) of the design doc, not after.
23. Stub plans at `grounding` are clutter but harmless; a generated index makes them visible. Better: the skill creates plans only for the current milestone.
24. OPEN-QUESTIONS.md is the most useful generated artefact for a solo founder: it collected founder actions scattered across three docs.
25. The Stop hook ran the linter at the end of the session as intended; the double registration (plugin + project) is harmless but the README could recommend only the plugin hook when the plugin is installed.

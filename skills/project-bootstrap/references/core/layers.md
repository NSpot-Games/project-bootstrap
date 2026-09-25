# Layers and identifiers

Four layers, top to bottom, and the rules that keep their identifiers stable while the roadmap moves under them.

## 1. The four layers

| Layer | Lives in | ID form | Status lives in |
|---|---|---|---|
| Phase | `<project>/docs/roadmap.md` | `P<n>` | the phase's heading in the roadmap, `**Status:**` |
| Milestone | `<project>/docs/milestones/M<n>.md` | `M<n>` | the milestone file's `**Status:**` field |
| Feature | one line in its milestone file | `M<n>-<nn>` | the checkbox on that feature line |
| Plan | `<project>/docs/plans/M<n>/M<n>-<nn>-<slug>.md` | `M<n>-<nn>` | the plan file's `**Status:**` field |

A phase groups consecutive milestones and states its own exit criteria; it lives only in the roadmap and has no file of its own. A project under the lite tier has one implicit phase and does not write `P1` anywhere.

A feature line names its plan (`— \`docs/plans/M<n>/M<n>-<nn>-<slug>.md\``) only once the plan exists — the path is appended at the Ground step, not at milestone creation. Until then the line is the feature's ID and title alone; an unticked feature without a plan is normal and the linter says nothing about it. A ticked feature without a plan is `E006`.

## 2. ID rules

IDs are allocated in creation order and never reused or renumbered. Execution order is the roadmap's order, not the ID's — an ID says when something was defined, the roadmap says when it happens.
*Example:* `M5` was allocated before `M6`, but the roadmap moves `M6` earlier because it unblocks work `M5` depends on. Both IDs are unchanged; only their position in the roadmap moves.

A dropped milestone keeps its file with status `dropped` and stays in the index — it is not deleted and its ID is not freed.
*Example:* `M4` ("offline mode") is dropped after user research rules it out. `<project>/docs/milestones/M4.md` remains, status `dropped`, still listed in the generated index.

Splitting a milestone: the original keeps its ID and its narrowed scope; the split-off part becomes a new milestone with the next free ID, and the roadmap places it. A note in both files records the split.
*Example:* `M3` is split: `M3` keeps the runtime work; `M8` is created for the authoring tool; the roadmap lists `M8` right after `M3`.

Inserting a milestone between two others: it gets a new ID (the next free one, regardless of position) and is placed in the roadmap where it belongs.
*Example:* A security-review milestone is inserted between `M5` and `M6`. It becomes `M9`, and the roadmap lists it between `M5` and `M6`.

Moving a feature to another milestone: allocate a new ID in the target milestone, mark the old plan `moved to M7-02`, and leave the old feature line struck through with the same pointer. Cross-references to the old ID stay valid because the old plan file remains in place.
*Example:* `M4-03`, a caching feature, belongs under `M7` instead. It becomes `M7-02`; `M4-03`'s plan is marked `moved to M7-02`, and its line in `M4`'s feature list is struck through pointing at `M7-02`.

## 3. Status vocabularies

| Object | Statuses |
|---|---|
| Phase | `sketch` · `active` · `done` |
| Milestone | `sketch` · `planned` · `in progress` · `done` · `dropped` |
| Feature | unticked · ticked · struck through with `moved to` |
| Plan | `grounding` · `planned` · `in progress` · `blocked` · `done` · `moved` · `superseded` |
| ADR | `proposed` · `accepted` · `superseded by NNNN` · `rejected` |
| Design doc | `draft` · `stable` · `living` |

The linter enforces these vocabularies: a `**Status:**` outside the list for its object is `E013` (design docs: `E014`). The check exists because a misspelt status would otherwise drop the file out of every other check that keys on status — a milestone marked `wip` would never be asked for exit criteria, and a plan marked `started` would never appear in `<project>/docs/CURRENT.md`. A plan's `**Shape:**`, when present, must be `lite` (no line, or an empty one, means a full plan); any other value is `E013` too. Both checks run at the standard and full tiers, where milestones and plans exist.

## 4. Where status lives

Status lives in exactly one place per object: the field or checkbox named in §1. Everything else — milestone and plan indexes, `<project>/docs/CURRENT.md`, the decisions index — is generated from that one place and never hand-edited.

The generated files are: `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`, `<project>/docs/decisions/README.md`, and `<project>/docs/CURRENT.md`. `tools/check_docs.py --fix` writes all four from the individual milestone, plan, and ADR files; each begins with a marker line stating it is generated.

## 5. Milestone size

A milestone holds three to ten features. Its exit must be demonstrable in a single session by someone who did not build it — not "the code compiles" but a specific, observable outcome. A milestone that grows past ten features is split (`§2`); one that would hold fewer than three is folded into a neighbouring milestone. The linter warns (`W004`) on a `planned` or `in progress` milestone outside that range; `done` and `dropped` milestones are history and are not re-litigated.

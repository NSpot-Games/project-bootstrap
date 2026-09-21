# Data-driven product

For products built around a large body of authored or generated data driving a runtime — games, interactive fiction, procedural content tools, anything where what data exists mostly determines what the product does. This is v1's original shape, carried over unchanged.

## 1. Fits when

The central artefact is authored data — levels, cards, encounters, dialogue, itineraries, recipes — and the runtime is mostly a machine that turns that data into behaviour.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design/<product>-design.md` | one-liner and target player; the player's core experience; 3–5 pillars used as tiebreakers; the core loop at multiple timescales; what the player can do (a table); systems; the centrepiece moment and the rules that manufacture it; fairness and difficulty; retention; non-goals for phase 1; a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` (questions live there, never in the doc); success criteria for the first prototype (measurable) | bootstrap |
| `<project>/docs/design/<core>-data-model.md` | principles (what is authoritative, what is derived, what must be validatable); the full structure with an annotated example of every collection; a small expression language, if behaviour is data-driven; validation rules as a numbered list; versioning and ID immutability | bootstrap |
| `<project>/docs/design/<runtime>.md` | the one rule that must never be broken, stated first; a numbered pipeline diagram; exact state shapes; deterministic tables where behaviour is tunable; the contract with any external component as a schema; validation and fallback; telemetry event names; a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` (questions live there, never in the doc) | bootstrap |
| `<project>/docs/design/architecture.md` | repo layout (packages, apps, backend); one line per module; the key interfaces as code; data flow for the main operation with a latency budget; persistence; offline and failure behaviour; testing strategy; security; a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` (questions live there, never in the doc) | bootstrap |
| `<project>/docs/design/<tooling>.md` (if the project has internal tools) | the internal tools this project needs (authoring, simulation, admin); one line per tool naming what it's for; a build order that says what not to build first; how each tool reads and writes the data model; who uses each tool and how often | bootstrap |
| `<project>/docs/design/example-<instance>.md` | a complete, real instance of the data model in the actual schema; a walkthrough of how the instance plays out against the core loop; a numbered "schema gaps" section recording every gap the instance exposed; a check that every cross-reference in the instance resolves; questions the instance raised beyond schema gaps go to `<project>/docs/OPEN-QUESTIONS.md`, with a one-line pointer here | bootstrap, before the runtime or architecture docs are finished |

## 3. Vocabulary

Identity — this profile changes none of the words the templates use.

| Template word | This profile's word |
|---|---|
| core loop | core loop |
| player | player |
| playtest | playtest |
| centrepiece moment | centrepiece moment |
| milestone | milestone |
| feature | feature |
| data model | data model |
| example instance | example instance |
| runtime | runtime |
| exit criteria | exit criteria |
| evidence | evidence |

## 4. Example instance and evidence

Example instance: one full, real instance of the data model, authored in the actual schema, covering phase 1's systems — written at C4 as `<project>/docs/design/example-<instance>.md`, before the runtime or architecture docs are finished. Evidence: playtests (a human or agent plays the instance and reports what happened against the design doc's pillars) and simulations (an automated run against the runtime, checked against its deterministic tables). Both are linked from the milestone they support, under `<project>/docs/evidence/`.

## 5. Default tier and M0

Default tier: Standard (`references/core/tiers.md §3`). M0 is nearly always: fold the schema gaps the example instance surfaced back into the data model — closing them before the rest of the project builds on a schema that has already met reality once (`references/core/adoption.md §1`, C11).

## 6. Suggested non-goals

A design doc without a stated non-goals section gets built past its intended scope, because an agent asked to make something better will otherwise happily build whatever isn't explicitly ruled out. Starting categories to confirm or replace during Brainstorm:

- Multiplayer, social, or shared-state features before the single-player core loop is proven.
- Authoring-tool polish before the data model it edits has stabilized.
- Ports to additional platforms before one platform's centrepiece moment lands.
- The most visually impressive system in the design doc, unless it is also the one that proves the core loop — name it and order it late in the roadmap.

## 7. Profile-specific lessons

1. Write the example instance before the runtime or architecture docs. It exposes missing fields, hand-waved rules, and ambiguous expressions in one sitting, in a way reasoning about the schema in the abstract never does.
2. Decide the codename and file-naming convention before writing anything (`references/core/adoption.md §1`, C0). A mid-project rename touches every doc that names the product.
3. Name the least important system explicitly and order it late — the most visually impressive part of a data-driven product is rarely the one that proves the core loop.

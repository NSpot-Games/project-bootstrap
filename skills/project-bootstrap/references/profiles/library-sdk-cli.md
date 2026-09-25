# Library, SDK, or CLI

For projects whose product is code other code calls — a library, an SDK, a command-line tool — where the central artefact is a public surface with a stability promise, not a runtime with users clicking through it.

## 1. Fits when

The central artefact is a public API surface other code calls.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design/<product>-design.md` | who this is for and what it replaces; API design principles (naming, ergonomics, the stability promise); supported platforms and runtimes; non-goals for v1's surface; success criteria for the first prototype's surface | bootstrap |
| `<project>/docs/design/api-surface.md` | principles (what is public vs. internal, stability tiers); the full surface with an annotated example of every entry point; the error model and exceptions; golden usage examples that are also tests; deprecation and removal policy | bootstrap |
| `<project>/docs/design/architecture.md` | repo layout (packages, build targets); the key internal interfaces as code; data flow for the main call path with a performance budget; dependency policy (what's vendored, what's external); testing strategy (unit, integration, golden examples) and CI budget (`references/core/economy.md §3`), with the supported-version matrix in the slow job | bootstrap |
| `<project>/docs/design/versioning-and-compat.md` | the versioning scheme; compatibility guarantees per stability tier; the deprecation process and timeline; breaking-change policy; the release checklist | phase start |

Versioning and compat is written when the API surface first stabilizes enough to promise something about — this is an artifact trigger, not a phase boundary; a Standard-tier project (this profile's default, `§5`) has no second phase to become `active` (`references/core/tiers.md §4`). The other three are written at bootstrap. On a Full-tier project this usually coincides with the phase that ships the first stable release becoming `active` (`references/core/tiers.md §4`).

## 3. Vocabulary

| Template word | This profile's word |
|---|---|
| data model | API surface |
| example instance | golden example |
| runtime | execution model |
| milestone | release |

IDs stay `M<n>` and `M<n>-<nn>` (`references/core/layers.md §1`); only the word used in prose changes — the roadmap runs by version, and milestones map to releases.

## 4. Example instance and evidence

Example instance: golden usage examples that are also tests — real calling code against the API surface, checked into the test suite, so a golden example rotting is a test failure, not a stale doc. Evidence: benchmarks (numbers checked against a stated baseline, not just numbers) and adopter feedback (real usage reports from whoever consumes the library, even if that's only the maintainer's own downstream project at first).

## 5. Default tier and M0

Default tier: Standard (`references/core/tiers.md §3`). M0 is nearly always: fold the gaps the golden examples surfaced back into the API surface, before writing the versioning-and-compat doc.

## 6. Suggested non-goals

Starting categories to confirm or replace during Brainstorm:

- Supporting every language runtime or platform before one is solid.
- A plugin architecture before there are two or three real plugins to generalize from.
- A backward-compatibility guarantee before the surface reaches its first stable release.
- A GUI wrapper around the CLI before the CLI itself is proven.

## 7. Profile-specific lessons

1. A golden usage example that isn't also a test rots the day someone changes the API surface without noticing.
2. Version the API surface doc itself — a breaking change to the surface is a design change with a changelog entry, same as any other design doc (`references/core/doc-kinds.md §3`).
3. Benchmarks without a stated baseline are just numbers; record what they're being compared against.

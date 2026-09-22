# Research prototype

For work that exists to answer a question before anyone commits to building the thing the question is about — a feasibility spike, a research prototype, a proof of concept whose output is a decision, not a product.

## 1. Fits when

The central artefact is a question worth answering before committing to build anything.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design.md` — question and hypotheses | the question this prototype answers; hypotheses and what would falsify each one; what "answered" looks like (success criteria); constraints and the time box; non-goals (what this prototype will not answer) | bootstrap |
| `<project>/docs/design.md` — architecture sketch | the one rule that must not be broken; a rough component sketch, kept throwaway-friendly; the worked example this sketch must support; what's deliberately not designed yet | bootstrap |

This profile defaults to the Lite tier (`§5`), where there is one `<project>/docs/design.md` file rather than a `<project>/docs/design/` directory (`references/core/tiers.md §2`); both rows above are sections of that one file, not separate files.

## 3. Vocabulary

| Template word | This profile's word |
|---|---|
| milestone | question |
| feature | probe |
| plan | protocol |
| example instance | worked example |

IDs stay `M<n>` and `M<n>-<nn>` (`references/core/layers.md §1`); only the word used in prose changes — the project's roadmap is a sequence of questions, each answered by one or more probes.

## 4. Example instance and evidence

Example instance: one worked example — a single real run of the prototype against a real input, showing what it actually produced, not what it was expected to produce. Evidence: experiment notes — what was tried, the time box, and the result, recorded in the protocol's Current state or in an ADR if the probe settled something other work depends on (`references/core/lifecycle.md §2`).

## 5. Default tier and M0

Default tier: Lite (`references/core/tiers.md §2`) — one question, one phase, and the roadmap is the milestone. M0 is nearly always: fold the gaps the worked example surfaced back into the hypotheses in `<project>/docs/design.md`, before choosing the next probe.

## 6. Suggested non-goals

Starting categories to confirm or replace during Brainstorm:

- Packaging or productionizing the prototype.
- A user interface beyond what's needed to observe the result.
- Generalizing beyond the one question currently being asked.
- Performance optimization before the hypothesis is confirmed.

## 7. Profile-specific lessons

1. Spikes are the default here, not the exception (`references/core/lifecycle.md §2`): most probes are time-boxed, throwaway code to answer one question, and most of them are deleted once the question is answered.
2. The lifecycle's Plan step is a protocol, not a task list: it states what will be tried, how the result will be judged, and the time box — not a sequence of commits, because a probe often doesn't survive to become committed code.
3. A negative result is still a closed probe with real evidence; don't leave a protocol `in progress` waiting for a result that confirms the hypothesis.

# docs/decisions/ — Architecture Decision Records

## Why
Design docs say what; ADRs say why. Check here before relitigating anything.

## When to write one
Hard to reverse; resolves an open question; changes a design doc; a real choice between alternatives; discussed at length. Not for: routine choices, naming, formatting, single-file changes. When unsure, write it.

## Naming
`<NNNN>-decision-as-a-sentence.md`, at most sixty characters after the number, cut at a word. Next number; never reuse or renumber. One decision per file. Status is `accepted` when a human made the decision (in conversation, or recovered from history) and `proposed` when an agent recommends it.

## Statuses
`proposed` (agents may create) · `accepted` (human sets) · `superseded by NNNN` · `rejected`. Never delete.

## Template
Copy `tools/templates/adr.md`; fill every double-brace token; none may remain.

## Rules for agents
1. Read before writing (grep the topic). 2. Propose, don't accept — except backfills from accepted design docs. 3. Update the design doc in the same change. 4. Cite ADRs in code where it helps. 5. Never edit `README.md`; it is generated. 6. Don't relitigate inside the ADR. 7. A `proposed` ADR does not block a feature's Close unless `**Blocking:** yes`. Humans accept proposed ADRs in a batch at milestone close.

## Backfill list
| # | Decision | Source |
|---|---|---|
| 0001 | YAML frontmatter is optional; a missing date falls back to the filename | `docs/design/architecture.md §6` |

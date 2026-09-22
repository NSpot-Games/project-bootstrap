# Curated directory

For products whose value is a curated body of entities — places, people, organisations, works — each carrying provenance, presented through a public site and maintained through an internal tool: guides, directories, catalogues, registries, atlases. The product is the trust a visitor places in an entry.

## 1. Fits when

The central artefact is a set of curated entities with provenance and editorial rules, and what the visitor buys is confidence that an entry is true, current and worth acting on.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design/<product>-design.md` | one-liner and target visitor; what the visitor comes to decide; the key moment (a visitor trusts an entry enough to act on it) and what produces it; coverage and depth for phase 1 (which entity types, how many entries, how complete); what the visitor is told about provenance and freshness; non-goals for phase 1; success criteria for the first prototype (measurable) | bootstrap |
| `<project>/docs/design/<core>-data-model.md` | principles (what is authoritative, what is derived, what is provenance); the entity types and their relations, with an annotated example of each; the provenance fields every record carries (source, date, method, confidence); freshness and staleness rules; validation rules as a numbered list; ID immutability and the merge rule for duplicates | bootstrap |
| `<project>/docs/design/editorial-rules.md` | inclusion and exclusion criteria; the review states an entry passes through and who moves it between them; sourcing standards (what counts as a source, how many are needed); corrections and takedowns; tone and house style in one page | bootstrap |
| `<project>/docs/design/public-site.md` | the pages a visitor sees and the journeys between them (search, browse, entry, compare); what each page shows of provenance and freshness; the search and ranking rule stated plainly; performance and accessibility budgets | bootstrap |
| `<project>/docs/design/curation-tool.md` | the internal tool: who uses it and for which tasks; one line per screen; how it reads and writes the data model; the review queue; a build order that says what not to build first | bootstrap |
| `<project>/docs/design/architecture.md` | repo layout (the public site, the curation tool, the API and its workers, or the one app when it is server-rendered); one line per module; the key interfaces as code; data flow for the visit journey and for the publish-and-propagate journey, each with a latency budget; persistence and caching; hosting shape; testing strategy; the phase-1 build order and what is deliberately not in it | bootstrap |
| `<project>/docs/design/legal-and-privacy.md` | data about real people or organisations: lawful basis and consent where needed; what is stored about visitors; retention and deletion; takedown obligations; the jurisdictions that apply | bootstrap — not optional: a directory names real things from its first published entry |
| `<project>/docs/design/example-<instance>.md` | one complete, real entry in the actual schema with every provenance field filled; a walkthrough of it through inclusion, review and publication; the pages it appears on; a pointer to the numbered *Gaps* section of the entry's README under the C0 example location, where every gap the entry exposed is recorded (`SKILL.md §3`) — this doc is the walkthrough, the folder is the data, and both are written in one session | bootstrap, before the data model and the site docs are finished |

## 3. Vocabulary

| Template word | This profile's word |
|---|---|
| player | visitor |
| playtest | session (one visitor's visit, observed or recorded) |
| centrepiece moment | key moment |
| core loop | visit loop (arrive, search or browse, read an entry, act or leave) |
| data model | data model |
| example instance | example entry |
| runtime | public site |
| milestone | milestone |

IDs stay `M<n>` and `M<n>-<nn>` (`references/core/layers.md §1`); only the word used in prose changes.

## 4. Example instance and evidence

Example instance: one real entry — a real place, organisation or work with a real source — authored in the actual schema with every provenance field filled, its data under the C0 example location (`<project>/cases/<id>/`) with a README carrying provenance and the numbered *Gaps* section, and its walkthrough written at C4 as `<project>/docs/design/example-<instance>.md` in the same session, before the data model and the site docs are finished. A made-up entry hides exactly the provenance gaps the doc exists to find. Evidence: coverage counts against the stated phase-1 target; provenance completeness (the share of records with every provenance field filled); freshness (the share of records checked within their staleness window); and visitor sessions (a person or agent tries to answer a real question with the site and reports whether the key moment happened). All are linked from the milestone they support, under `<project>/docs/evidence/`.

## 5. Default tier and M0

Default tier: Standard (`references/core/tiers.md §3`); Full once more than one editor works the review queue or a second entity type is planned. M0 is nearly always: fold the schema gaps the example entry surfaced back into the data model, provenance fields first, before any entry is ingested at scale.

## 6. Suggested non-goals

Starting categories to confirm or replace during Brainstorm:

- Visitor accounts, ratings or comments before the curated body itself has earned trust.
- Automated ingestion at scale before the editorial rules have been applied by hand to a few hundred entries.
- A second entity type before the first is complete enough to be useful on its own.
- Personalisation or recommendations before search and browse are right.

## 7. Profile-specific lessons

1. Provenance is a field on every record, not a page about methodology: a visitor decides per entry, and an entry that cannot say where it came from is not curated, only collected.
2. The editorial rules are a design doc, not a wiki page. When a rule changes, the change is dated in the changelog and the entries reviewed under the old rule stay findable, because a visitor reading an old entry is trusting the rule that admitted it.
3. Write the legal-and-privacy doc at bootstrap even when it is short. A directory of real things has obligations from the first published entry, and the doc is where the takedown path lives when someone asks for it.
4. The curation tool is built for the review queue first and the data entry screens second; an entry that never gets reviewed is the failure mode, not an entry that is slow to type.

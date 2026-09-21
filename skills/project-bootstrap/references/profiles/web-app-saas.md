# Web app / SaaS

For multi-tenant products where the central artefact is the set of tenants using the product and the journeys they take through it — most B2B and B2C SaaS, internal tools with more than one team of users, anything shaped by "who is logged in" and "what are they trying to do."

## 1. Fits when

The central artefact is tenants and the journeys they take through a shared product.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design/<product>-design.md` | one-liner and target users; jobs to be done; primary journeys (multiple entry points, not one core loop); what a user can do (a table); the tenancy model in outline; a key moment of value and what produces it; non-goals for phase 1; a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` (questions live there, never in the doc); success criteria for the first prototype (measurable) | bootstrap |
| `<project>/docs/design/data-model.md` | principles (what is authoritative, what is derived, what is tenant-scoped); the full structure with an annotated example of every collection; row-level access rules; validation rules as a numbered list; versioning and ID immutability; a pointer to the instance README's gaps section and a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` | bootstrap |
| `<project>/docs/design/architecture.md` | repo layout (frontend, backend, shared — or the one app, when it is server-rendered); one line per module; the key interfaces (API contracts) as code; data flow for a primary journey with a latency budget; persistence and caching; testing strategy; a "decisions we're committing to" list; a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` (questions live there, never in the doc) | bootstrap |
| `<project>/docs/design/security-and-privacy.md` | threat model summary; authentication and authorization approach; tenant-isolation guarantees; data retention and deletion; secrets and key management (retention periods, session lifetimes and similar numbers the owner has not set go to the open-questions file, not into the doc as facts); a one-line pointer to `<project>/docs/OPEN-QUESTIONS.md` (questions live there, never in the doc) | bootstrap |
| `<project>/docs/design/deployment-and-observability.md` | environments and the promotion path between them; the deployment pipeline; logging, metrics, and tracing; alerting and on-call; rollback strategy | phase start |

Deployment and observability is written when a real deployment target first exists — this is an artifact trigger, not a phase boundary; a Standard-tier project (this profile's default, `§5`) has no second phase to become `active` (`references/core/tiers.md §4`). The other four are written at bootstrap because tenancy and security decisions here are hard to reverse. On a Full-tier project this usually coincides with the phase that ships that deployment target becoming `active` (`references/core/tiers.md §4`).

## 3. Vocabulary

| Template word | This profile's word |
|---|---|
| core loop | primary journeys |
| player | user |
| playtest | usability session |
| centrepiece moment | key moment of value |
| example instance | seed fixture |

## 4. Example instance and evidence

Example instance: a seed fixture for one tenant — one full, real tenant's data (users, roles, content) in the actual schema, exercising phase 1's primary journeys end to end. When no real tenant's data can be obtained at bootstrap, a constructed stand-in in the actual schema, labelled as such in its README, with replacing it as an M0 feature (`SKILL.md §3`). Evidence: usability sessions (a real or proxy user attempts a primary journey against the seed fixture, and what they actually did is recorded, not what they said they'd do) and load tests (the primary journeys measured under load against the phase's stated budget).

## 5. Default tier and M0

Default tier: Standard (`references/core/tiers.md §3`). M0 is nearly always: fold the gaps the seed fixture surfaced back into the data model, before building past one tenant — and, when the fixture is a stand-in, replace it with the real tenant's anonymised data as its own feature.

## 6. Suggested non-goals

Starting categories to confirm or replace during Brainstorm:

- Multi-region deployment before a single region proves the primary journeys.
- Enterprise SSO or SAML before the first paying tenant asks for it.
- Granular permission tiers beyond what the first few tenants actually need.
- White-labeling or theming before the primary journeys are proven.
- Native mobile apps before the web journeys are proven.

## 7. Profile-specific lessons

1. Write the seed fixture for one real tenant before the security-and-privacy doc — tenancy edge cases (shared resources, per-tenant limits) surface fastest in a real fixture, not in prose.
2. Usability sessions are evidence, not opinion — record what the participant did, not what they said they'd do.
3. A journey not in the design doc's table is a non-goal until it earns a place there; don't let "primary journeys" quietly become "every journey."

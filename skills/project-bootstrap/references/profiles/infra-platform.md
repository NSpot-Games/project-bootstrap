# Infra / platform

For projects that build infrastructure other teams or services run on — a platform, a shared service, an internal cloud layer — where the central artefact is the set of environments the project provides and the service-level objectives they must hold.

## 1. Fits when

The central artefact is environments and the SLOs they must hold.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design/<product>-design.md` | who operates this and who consumes it; service-level objectives and how each is measured; capacity and scaling assumptions; non-goals for the first environment; success criteria for the first environment | bootstrap |
| `<project>/docs/design/architecture.md` | topology (regions, networks, boundaries); the key interfaces (APIs, queues) as code or schema; data flow for the main request path with a latency budget; persistence and backup strategy; testing strategy, including failure injection, and CI budget (`references/core/economy.md §3`) | bootstrap |
| `<project>/docs/design/environments.md` | principles (what is authoritative — infrastructure-as-code vs. console changes); the environment and config schema with an annotated example; secrets and configuration management; the promotion path between environments; validation rules as a numbered list | bootstrap |
| `<project>/docs/runbooks/<scenario>.md` | purpose and audience; standard operating procedures, one per scenario; incident-response steps; escalation paths; rollback and recovery procedures | when a real environment first exists |
| `<project>/docs/design/security.md` | threat model summary; identity and access management; network security boundaries; secrets and key rotation; audit logging | bootstrap |

Runbooks are Reference kind, not Design kind (`references/core/doc-kinds.md §2`): they carry no design-doc header and no `## Changelog`, live under `<project>/docs/runbooks/` rather than `<project>/docs/design/`, and are cited from the service design doc. They are written when a real environment first exists — this is an artifact trigger, not a phase boundary; a Standard-tier project (this profile's default, `§5`) has no second phase to become `active` (`references/core/tiers.md §4`). On a Full-tier project this usually coincides with the phase that stands up that environment becoming `active` (`references/core/tiers.md §4`). The other four docs are written at bootstrap.

## 3. Vocabulary

| Template word | This profile's word |
|---|---|
| design | service design |
| data model | environment and config schema |
| example instance | one environment definition |
| evidence | SLO reports and incident reviews |

## 4. Example instance and evidence

Example instance: one environment definition — a complete, real environment (dev, staging, or prod) expressed in the actual environment and config schema, provisionable from that definition alone. Evidence: SLO reports (the stated SLOs measured against the running environment) and incident reviews (what broke, and what the runbook did or didn't cover).

## 5. Default tier and M0

Default tier: Standard (`references/core/tiers.md §3`). M0 is nearly always: fold the gaps the environment definition surfaced back into the environment and config schema, before provisioning a second environment.

## 6. Suggested non-goals

Starting categories to confirm or replace during Brainstorm:

- Multi-cloud portability before a single environment is stable.
- Self-service provisioning tooling before the first environment's runbooks exist.
- Auto-scaling policies before real load has been observed.
- Full audit tooling before there is traffic worth auditing.

## 7. Profile-specific lessons

1. Write one real environment definition before the runbooks — a runbook written against an imagined environment is a runbook nobody can follow during an incident.
2. An SLO without a stated measurement method is a wish; state how it's measured in the same sentence that states the target.
3. Runbooks are Reference kind: they change whenever the operational procedure changes, not on a design doc's changelog cadence, and live under `<project>/docs/runbooks/`, cited from the service design doc rather than filed inside it.

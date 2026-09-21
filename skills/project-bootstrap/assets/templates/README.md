# templates/

These files are copied into a new project during bootstrap and every double-brace placeholder in them is replaced with a real value; nothing here is read by the tooling directly. The table below lists every placeholder used across `templates/`, what it means, and where it typically comes from (the bootstrap conversation, the chosen profile, or the feature/plan being created).

| Token | Meaning |
|---|---|
| `{{Project}}` | Project display name |
| `{{one_sentence}}` | What the project is, one sentence |
| `{{one_rule}}` | The rule that shapes everything |
| `{{product}}` | Slug of the product design doc |
| `{{profile}}` | Profile name from `profiles/` |
| `{{tier}}` | lite, standard, or full |
| `{{n}}`, `{{nn}}` | Milestone number, feature number |
| `{{Title}}` | Title of the object being created |
| `{{slug}}` | Kebab-case slug of the title |
| `{{date}}` | ISO date `YYYY-MM-DD` |
| `{{agent}}` | Agent or tool name that collected an evidence file |
| `{{commands}}` | Build, test, lint, run commands |
| `{{rule}}` | A single non-negotiable rule |
| `{{deferred}}` | A deferred item |
| `{{Area}}` | Glossary area or design area, in heading form |
| `{{loose word}}` | An imprecise word the glossary says to avoid |
| `{{precise term}}` | The exact term to use instead of a loose word |
| `{{measurable statement}}` | A phase's numeric or checkable exit statement |
| `{{one or two sentences}}` | A sketch milestone's goal, kept short |
| `{{NNNN}}` | Four-digit ADR number |
| `{{decision_as_a_sentence}}` | ADR title |
| `{{decision already stated in a design doc}}` | A decision to backfill into an ADR from an already-written design doc |
| `{{source_section}}` | The design doc and section a backfilled decision comes from |
| `{{files}}` | Related file paths cited in a design doc header |
| `{{audience}}` | Who reads this doc, and why |
| `{{three_sentences}}` | A project README's three sentences: what, for whom, current state |

A template file has no `{{` left when copied into a project; the linter's E005 check enforces this.

Three files here are not filled in but copied as they are: `check_docs.toml` becomes
`<project>/docs/.check_docs.toml` (every linter key, commented), `gitattributes` becomes
`<project>/.gitattributes`, and the object templates `plan.md`, `milestone.md`, `adr.md` and
`evidence.md` are copied, tokens intact, to `<project>/tools/templates/`, where a session copies
one and fills it each time it creates a plan, a milestone, an ADR or an evidence file. That
directory sits outside the linter's placeholder scope, so the tokens there are not E005.

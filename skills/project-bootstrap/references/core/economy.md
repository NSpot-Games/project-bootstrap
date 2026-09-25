# Economy

Agents write the code; humans direct the work. Every check an agent runs costs time and tokens,
and every test it adds is a test every later session runs and reads. This page is how the kit
keeps that cost proportional: tests that earn their place, checks sized to the moment, one lean
CI workflow, a working loop that spends the human's attention on decisions only, and
instructions free of filler. It is the default for every project; a profile or an ADR may raise
any bar here, with its reason written down. Each project states these rules in its own words in
`<project>/AGENTS.md` and `<project>/docs/WORKFLOW.md`; this page is where the reasons live.

## 1. Tests that earn their place

A test is written only when it does at least one of three things:

- pins behaviour a user or a contract depends on — a public API, a primary journey, a schema;
- reproduces a bug that actually happened;
- guards an invariant that is expensive to debug when broken — concurrency, money, data loss,
  security.

These do not earn a place: tests that restate the implementation; trivial accessors and
constructors; mocks asserting on mocks; blanket snapshots; a second test for a path already
covered; tests written to raise a coverage number.

Pruning is allowed. An agent may delete a redundant or brittle test in the same commit as the
change that exposed it, with one line in the plan's Progress notes saying why.

Every full plan lists its tests up front under **Tests this feature adds**, one line each, so the
human reviews test scope once, in the plan, instead of discovering it in the diff. A lite plan
(`references/core/lifecycle.md §3a`) names its tests in its task lines.

## 2. When checks run

| When | What runs |
|---|---|
| While editing | typecheck or lint, plus the test file for the module being edited |
| At a task's end | the task's named check — the affected packages' tests, one test, or a run command, whichever is cheapest and still proves the task |
| At Close | the full suite, once |
| In CI | the full suite plus slow and end-to-end tests (`§3`) |

Ground runs the tests for the packages the feature will touch, not the full suite: the full suite
ran at the previous feature's Close and runs in CI.

Evidence is the summary line — `142 passed, 0 failed in 3.1s` — or the one assertion that
matters, never the full output. On a failure, paste only the failing excerpt. A plan is read by
every later session that touches the area; pasted logs are a cost each of them pays.

## 3. CI

The kit does not write a project's CI; agents build it during feature work, from the testing
strategy and CI budget in `<project>/docs/design/architecture.md`. The default they follow:

- **One workflow file, two jobs.** A fast job on every pull request — lint, typecheck, fast
  tests, the docs linter — with a budget of under five minutes. A slow job on merge to `main` or
  nightly — end-to-end, integration, load.
- **A path filter.** A change that touches only docs runs only the docs linter.
- **No matrix** unless the profile needs one.
- **No deploy or release pipeline** until the milestone that actually ships something.
- **Dependencies cached.**
- **One local `check` command** runs exactly what the fast job runs. Agents run it before
  pushing and never push to find out.

A budget raised by a profile or an ADR says why in the same place.

## 4. Working for a human

- **Stopping rules.** Keep going when a step needs no input, and put the status in the same
  message as the next action. Stop before anything destructive — deleting data, force-pushing,
  rewriting history — anything outside the repository, or anything that spends money.
- **Done when and Stop and ask if.** Every plan, full or lite, states checkable end states and
  the conditions that bring the human in, before work starts.
- **Questions.** A question that does not block the next step goes to
  `<project>/docs/OPEN-QUESTIONS.md` with the default the agent chose, and work continues on that
  default. Only a question that blocks stops the session.
- **Self-review before human review.** At Close, review the diff against `main` and list only
  blocking problems, each with the file, the line, why it is wrong, and how to show it failing.
  Fix each, or record it in the plan, before asking a human to review.
- **The session-end report**, in this order: Needs from you (decisions, approvals, answers) →
  Done (with evidence summary lines) → Findings → Next. The human reads the first part first.

## 5. Instruction hygiene

What agents write into `<project>/AGENTS.md`, plans and prompts:

- No "think carefully" or "think step by step". Current models reason before they answer;
  the line costs every session and buys nothing.
- Concrete anti-patterns over adjectives: "don't use X, Y or Z", not "keep it clean". An
  adjective swaps one default for another; a list removes the defaults named.
- In Ground bullets and research, mark anything unconfirmed and say where you looked.
- Independent work fans out to subagents, one per package or service; check each one's evidence
  before accepting its result.
- Working lists live in files — the plan — because a long session's context is summarised and
  a file survives it.

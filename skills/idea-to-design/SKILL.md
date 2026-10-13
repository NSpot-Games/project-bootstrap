---
name: idea-to-design
description: Use when someone brings a raw idea for a product, game, tool or service — "I have an idea for…", "turn this idea into something that could work", "is this idea any good", "help me design this app" — and no design notes or code exist yet. Not for building, code changes, or a repository that already has design notes.
license: MIT
metadata:
  author: NSpotGames
  version: "2.10.1"
---

# Idea to design

Turns a raw idea into a design a project can be built from, as a conversation: find what is new
about the idea, settle what it is for, make every structural decision one question at a time,
write each decision down as it is made, and check the whole for contradictions before handing
off. The output is `<project>/docs/vision/`, which project-bootstrap reads as a docs-first
project. Follow the steps in order.

Every file this skill names lives inside its own directory: the question method in
`references/questions.md`, the final check in `references/consistency-pass.md`, the file shapes in
`assets/templates/`. Paths written `<project>/...` are in the project being designed.

## 1. The first message: the hook

A raw idea is design work before it is a project: this first message comes before any project
setup, even in an empty repository and even when a setup skill such as project-bootstrap is
installed. Setup is the hand-off in step 9, once there is a design to set up.

The first reply to a raw idea has these parts, in this order:

1. **The idea in one sentence**, in your own words.
2. **What already exists.** Two to four existing products or services it resembles, named by
   you, each with what it already does ("Peerby and local tool libraries already lend tools
   between neighbours"). You do the comparison; the person is not asked to.
3. **The hook.** One sentence, starting "What is new here is…", naming the one thing this idea
   adds that those do not. Every later decision protects it.
4. **One question: what it is for**, built as step 2 describes, with your recommendation first.

That is the whole message. It holds one question, as its last line. Everything else the idea
raises (terms, trust, money, success, the technology) waits for its own step.

**If the products in part 2 already do everything the idea describes**, parts 3 and 4 become:

3. **The verdict, plainly.** "This already exists: it is <product>." Name it.
4. **Two or three angles** that would make it new, as a lettered list, one sentence each, your
   recommended angle first with its reason; then one question: which angle, or one of their own.

The purpose question follows once the person has picked a hook.

## 2. Purpose

The purpose question asks what the product is for: commercial, internal tool, community,
learning, portfolio, or whatever fits. It comes before any feature, because it changes most later
answers (how it earns, how big it is, what "done" means). It is built like every question
(step 3): lettered options, the recommendation first, marked "(my recommendation)", with a
one-sentence reason. When only the idea exists, the reason rests on the idea itself ("a
neighbourhood scheme starts as a community project, so…").

## 3. Structural decisions, top-down, one per message

Ask the decisions that shape the product, biggest first: its overall structure, its core loop or
core flow, then each subsystem, then details. Each question message has these parts, in order:

1. one line recording the last answer, when there was one;
2. the decision, in one sentence;
3. 2–4 lettered options that genuinely differ, the recommended one first and marked
   "(my recommendation)", each with what it gains, what it costs and a real product as a
   reference point (`references/questions.md`);
4. the reason for the recommendation, in one sentence;
5. the question, as the last line, and the only one in the message.

A question too small to matter gets no message: pick the conventional default, say so in one line
inside the next question, and move on.

## 4. Pillars

Once the shape is visible — usually after the purpose and two or three structural decisions —
propose 3–5 pillars: short rules every later decision is checked against ("every match is a
decision", "nobody profits from a neighbour"). Write them into `<project>/docs/vision/README.md`.
From then on, an option that breaks a pillar says which; a recommendation never breaks one
silently.

## 5. Write as you go

Each decision is written the moment it is agreed, never batched for the end:

- The area it belongs to gets its own `<project>/docs/vision/<area>.md` (shape:
  `assets/templates/area.md`), created on its first decision and extended after.
- `<project>/docs/vision/alternatives.md` (shape: `assets/templates/alternatives.md`) gets the
  question, the option chosen, and every option not taken with a note on where it might fit later.
  An idea left out on purpose goes under "Possible additions".
- `<project>/docs/vision/README.md` (shape: `assets/templates/vision-readme.md`) keeps the hook,
  purpose, pillars, the decided table and the still-to-design table current.
- Files are written as UTF-8.
- Then commit: `git add` the vision files this decision changed, each by name, and commit with a
  message naming the decision.

If the project has no repository yet, offer to create one before the first write. Never push,
and never create a remote, without the person's yes.

## 6. Rules apart from content and numbers

Agree the rules of each area first: how it works. Lists of content (the items, the enemies, the
screens) and numbers (prices, amounts, timings) go into the area file's "Still to design" and do
not block the next decision. A starting number may be proposed as a starting value, marked as one.

## 7. Technology waits

No engine, stack, language, database or architecture is chosen until the design is agreed — not
as a lean, not as a provisional pick.

**If the person asks a technology question before the design is agreed**, the reply has these
parts, in order:

1. A brief answer: what the choice depends on, and which design decision or later stage settles
   it.
2. The question and that answer, as one line under "Parked for later" in
   `<project>/docs/vision/README.md`. That line is the only place it is written down.
3. A commit of that README change.
4. The open design question, asked again as it stood, as the last line.

A hard technical limit that shapes the design — a platform's rules, a regulation, a device's
screen — is recorded as a constraint in the area it shapes, not decided as design.

| Excuse | Reality |
|---|---|
| "I'd lean Postgres, but it's early" | A lean is a pick: the person hears a decision. Say what it depends on instead. |
| "I've noted it as provisional" in a tech note | A note outside "Parked for later" is a second design document. Park it in the README. |

## 8. Consistency pass

When the person says the design is complete, or every structural area is decided, read every file
in `<project>/docs/vision/` together and run `references/consistency-pass.md`. Fix each finding
in the files, commit, and report each fix in a short list so the person can check it. If nothing
is wrong, change nothing and say so.

## 9. Hand off

Summarize in a few lines what is decided and what is still to design, linking
`<project>/docs/vision/README.md`. Offer the next step: project-bootstrap, which reads
`<project>/docs/vision/` as the thinking a docs-first project starts from, or a first prototype
to test the riskiest part. Start neither without a yes.

## Conduct

- Plain language. A term the person may not know is explained the first time it appears.
- A choice against the recommendation, or a change of direction, is taken at once in one line;
  the recommended option is recorded in `<project>/docs/vision/alternatives.md` as not taken,
  like any other.

## Red flags

- "I'd lean Postgres" — a technology pick before the design is agreed.
- "I've noted it as provisional … and kept it out of the vision docs" — a technical note
  outside "Parked for later".

Each means: stop, return to step 7.

## Common mistakes

| Mistake | Fix |
|---|---|
| Five numbered groups of questions in the first reply, ending "Short answers are fine" | Step 1: four parts, one question, as the last line |
| Handing the comparison over: "What do you think they do badly? That gap is the real product." | Step 1, parts 2 and 3: you name the products and the hook |
| Options with no pick: "Options include a deposit, a rating system, insurance…" | Steps 2 and 3: the recommendation first, with its reason |
| Starting setup on a raw idea: "Question 1 of 5: name and codename." | Step 1 comes first; project-bootstrap is the hand-off in step 9 |
| Restating a copy as the plan ("post square photos with filters, follow friends, and like") without saying it exists | Step 1, the verdict: name the product, offer angles |
| A new file left uncommitted, or unrelated files swept into a commit | Step 5: `git add` the changed vision files by name, then commit |
| Dashes written in a Windows code page, unreadable as UTF-8 | Step 5: files are written as UTF-8 |

---
name: idea-to-design
description: Use when someone brings a raw idea for a product, game, tool or service — "I have an idea for…", "turn this idea into something that could work", "is this idea any good", "help me design this app" — or wants to continue a design under way in docs/vision/. Not for building, code changes, or a project whose design is already settled.
license: MIT
metadata:
  author: NSpotGames
  version: "2.12.0"
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
installed. Setup is the hand-off in step 10, once there is a design to set up.

The first reply to a raw idea has these parts, in this order:

1. **The idea in one sentence**, in your own words.
2. **What already exists.** Two to four existing products or services it resembles, named by
   you, each with what it already does ("Streaks and Habitica already track habits and reward
   streaks"). You do the comparison; the person is not asked to.
3. **The hook.** One sentence, starting "What is new here is…", naming the one thing this idea
   adds that those do not. Every later decision protects it.
4. **One question: what it is for**, built as step 2 describes, with your recommendation first.

That is the whole message, and its one question follows the question rule in Conduct.
Everything else the idea raises (money, success, the technology) waits for its own step.

**If the products in part 2 already do everything the idea describes, or differ from it only in
a detail a setting could change**, parts 3 and 4 become:

3. **The verdict, plainly.** "This already exists: it is <product>." Name it.
4. **Two or three angles** that would make it new, as a lettered list, one sentence each, your
   recommended angle first with its reason. The last line asks which angle, or one of their own
   (the question rule in Conduct).

The purpose question follows once the person has picked a hook.

## 2. Purpose

The purpose question asks what the product is for: commercial, internal tool, community,
learning, portfolio, or whatever fits. It comes before any feature, because it changes most later
answers (how it earns, how big it is, what "done" means). It is built like every question
(step 3): lettered options, the recommendation first, marked "(my recommendation)", with a
one-sentence reason. When only the idea exists, the reason rests on the idea itself ("a habit
tracker built for your own routine starts as a personal project, so…").

## 3. Structural decisions, top-down, one per message

Ask the decisions that shape the product, biggest first: its overall structure, its core loop or
core flow, then each subsystem, then details. Each question message has these parts, in order:

1. one line recording the last answer, when there was one;
2. the decision, in one sentence;
3. 2–4 lettered options that genuinely differ, the recommended one first and marked
   "(my recommendation)", each with what it gains, what it costs and a real product as a
   reference point, when one exists (`references/questions.md`);
4. the reason for the recommendation, in one sentence;
5. the question, as the last line (the question rule in Conduct).

A question too small to matter (a conventional default exists and nothing depends on it,
`references/questions.md` §7) gets no message: pick the default, say so in one line inside the
next question, and move on.

## 4. Pillars

Once the shape is visible — usually after the purpose and two or three structural decisions —
propose 3–5 pillars: short rules every later decision is checked against ("every match is a
decision", "a missed day never wipes out a month"). Write them into `<project>/docs/vision/README.md`.
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
  purpose, pillars, the decided table and the still-to-design table current. Purpose, hook and
  pillars live only in this file, never in an area file of their own.
- Files are written with the file-writing tool, not shell redirection, so they stay UTF-8.
- Then commit: `git add` the vision files this decision changed, each by name, and commit with a
  message naming the decision.

If the project has no repository yet, offer to create one before the first write. If they
decline, write the files without committing. Never push,
and never create a remote, without the person's yes.

## 6. Rules apart from content and numbers

Agree the rules of each area first: how it works. Lists of content (the items, the enemies, the
screens) and numbers (prices, amounts, timings) go into the area file's "Still to design" and do
not block the next decision. A starting number may be proposed as a starting value, marked as one.

## 7. Technology waits

No engine, stack, language, framework or architecture is chosen until the design is agreed
(until the consistency pass is done and the hand-off accepted): not as a lean, not as a
provisional pick.

**If the person asks a technology question before the design is agreed**, the reply has these
parts, in order:

1. A brief answer: what the choice depends on, and which design decision or later stage settles
   it.
2. The question and that answer, as one line under "Parked for later" in
   `<project>/docs/vision/README.md`. That line is the only place it is written down.
3. A commit of that README change.
4. The open design question, as it stood, with its options, asked as the last line (the
   question rule in Conduct).

A hard technical limit that shapes the design — a platform's rules, a regulation, a device's
screen — is recorded as a constraint in the area it shapes: a limit set from outside, never a
choice between technologies.

| Excuse | Reality |
|---|---|
| "I'd lean towards one of them, but it's early" | A lean is a pick: the person hears a decision. Say what it depends on instead. |
| "I've noted it as provisional" in a tech note | A note outside "Parked for later" is a second design document. Park it in the README. |

## 8. Consistency pass

When the person says the design is complete, or every structural area is decided, read every file
in `<project>/docs/vision/` together and run `references/consistency-pass.md`. Fix each finding
with the option that keeps the pillars and the hook, and report it with the option not taken, so
the person can reverse it. Ask only when the fix forces a choice between two pillars, and then
only about the first such finding; fix the rest; list any other pillar conflict for the next
message. Commit the fixes and report each in a short list. If nothing is wrong, change nothing
and say so.

## 9. Deep dive (optional)

When the consistency pass is clean and areas still have open items, the next message offers to go
deeper before any hand-off. It has these parts, in order:

1. the consistency result, in a line or two;
2. each area with open items, and how many: its "Still to design" list, with the proposed order
   (below);
3. the recommendation and its reason: the deep dive when the open items are content lists or
   numbers a build needs first; handing off when they can be settled while building;
4. the offer, as the last line and the one question: deep-dive those areas one by one now, or
   hand off with them open.

If the person has already said to skip it, or nothing is open, go to step 10.

**Order.** Propose one: areas that other areas depend on first, then the riskiest. The person may
reorder or skip any area.

**Each area:**

1. Its open items, one question per message. A content list longer than about ten entries is
   proposed whole as a draft (`references/questions.md` §9). A number is proposed as a starting
   value with its reason.
2. One rules check, once its items are settled: now that the details exist, should any rule in
   this area change? A rule changed here is recorded in
   `<project>/docs/vision/alternatives.md` like any other decision.
3. A consistency check of the area against the files it touches. Then mark it **refined** in the
   README's still-to-design table, commit, and ask whether to go on to the next area, skip it,
   or stop.

**Stopping.** The person can stop after any area; the table shows which areas are refined and
which are open, so a later session resumes at the first open one. After the last chosen area, run
the full consistency pass (step 8) again, then hand off.

## 10. Hand off

Summarize in a few lines what is decided and what is still to design, linking
`<project>/docs/vision/README.md`. Offer the next step: project-bootstrap, which reads
`<project>/docs/vision/` as the thinking a docs-first project starts from, or a first prototype
to test the riskiest part. Start neither without a yes.

## Conduct

- Every message asks at most one question, as its last line, with a recommendation and its
  reason; a lead-in names the open question as a statement. The recommendation comes before the
  question; nothing follows the question.
- Plain language. A term the person may not know is explained the first time it appears.
- A change of direction from the person is taken at once in one line, without arguing back or
  reopening its cost; so is a choice against the recommendation, and the recommended option is
  recorded in `<project>/docs/vision/alternatives.md` as not taken, like any other.

## Red flags

- "I'd lean towards…" about a technology — a pick before the design is agreed.
- "I've noted it as provisional … and kept it out of the vision docs" — a technical note
  outside "Parked for later".

Each means: stop, return to step 7.

## Common mistakes

| Mistake | Fix |
|---|---|
| Lists ten questions in five groups before saying anything about what exists, then asks for "short answers" | Step 1: four parts, one question, as the last line |
| Handing the comparison over: "What do you think they do badly? That gap is the real product." | Step 1, parts 2 and 3: you name the products and the hook |
| Names the open question as a question in the lead-in ("Back to the open question: how do people find it?"), then asks "Which one?" | Conduct, the question rule: the lead-in states it ("The open question is …"); the only question is the last line |
| Lists the options for a question (three ways a habit app could remind people, say) and picks none | Steps 2 and 3: the recommendation first, with its reason |
| Starting setup on a raw idea: "Question 1 of 5: name and codename." | Step 1 comes first; project-bootstrap is the hand-off in step 10 |
| A clean consistency pass followed straight by "Should I start project-bootstrap?" while areas still have open items | Step 9: offer the deep dive first; hand off when the person chooses to |
| Restates an idea that an existing product already is, feature by feature, as the plan, without saying it exists | Step 1, the verdict: name the product, offer angles |
| A new file left uncommitted, or unrelated files swept into a commit | Step 5: `git add` the changed vision files by name, then commit |
| Dashes written in a Windows code page, unreadable as UTF-8 | Step 5: files are written as UTF-8 |

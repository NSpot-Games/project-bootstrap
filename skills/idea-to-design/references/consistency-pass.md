# Consistency pass

The final read of the whole design. Read every file in `<project>/docs/vision/` together, then
look for each kind of problem below. Fix each finding in the files, and report each one.

## 1. Rules that cannot happen

A rule that assumes a state the rest of the design rules out: a bonus for something the design
never allows, a starting bundle bigger than the holding limit, a trigger on an event that every
other rule prevents. Check every rule's condition against the rules that govern that condition.

## 2. Numbers and timings that clash

The same quantity stated differently in two files; a timing that does not fit inside the
timing that contains it (a step longer than the session it belongs to); a total that the parts
cannot add up to.

## 3. Limits inside the normal case

A limit, penalty or alarm that fires during ordinary, intended use: "late" earlier than the
standard loan length, an anti-stall rule that triggers inside a normal fight's length, a cap
below the starting value. Compare every limit with the normal range the design intends.

## 4. Stale summaries

`README.md`'s hook, purpose, decided table and still-to-design table, and any other summary,
against the area files they summarize. The area file is the truth; the summary is corrected.

## 5. Fairness and abuse

Where money, luck or rank meet: a paid or random advantage leaking into a ranked or competitive
part; a loop that pays out without limit; an action that is always correct, so no decision is
left. Check each pillar against the whole: does anything break it?

## 6. Reporting

Report each finding as one line: what contradicted what, and the fix made. If a fix needs a
decision only the person can make, ask it as a question (`references/questions.md`) instead of
fixing it. When several findings need the person, the report lists them all, and the message
asks about the first, as its last line; the next is asked after its answer. If nothing is wrong,
change nothing and say so.

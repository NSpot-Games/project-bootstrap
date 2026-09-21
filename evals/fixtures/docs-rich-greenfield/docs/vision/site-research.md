# Static site research

Three ways to produce the site were compared in August 2026.

| Option | For | Against |
|---|---|---|
| Hugo with a custom theme | fast, mature | a theme, a config and a binary before anything renders |
| Pandoc per note plus a hand index | no tooling | the index is the whole problem |
| Own renderer, markdown-it and one template | small, testable, ours | we maintain it |

## Decision taken
Own renderer. Rendering is the easy half; the index is the product. Decided 2026-09-02.

## Open question
Client-side search: a prebuilt JSON index and a small script, or no search in v1?

# Notes format

Every note starts with YAML frontmatter carrying `title`, `date` and `tags`; the body is free
markdown. A note without frontmatter is rejected with a clear error naming the file.

## Fields
- `title` — one line; falls back to the first heading.
- `date` — ISO date; the filename prefix `YYYY-MM-DD-` is the fallback.
- `tags` — a list; lowercase; hyphens for spaces.
- `place` — optional; a slug that groups notes about one location.

## Decision taken
Tags are case-insensitive and stored lowercase. Decided 2026-08-30.

## Open question
Should a note with no date at all be indexed under "undated" or rejected?

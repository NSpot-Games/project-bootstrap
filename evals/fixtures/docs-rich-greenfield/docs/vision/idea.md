# The idea

Fieldnote turns a folder of dated markdown notes about places into a searchable static site.

## Who it is for
People who keep notes while walking, birding, surveying or inspecting: one note per visit,
written on a phone, kept forever. They want an index by place, by date and by tag, and a site
they can hand to someone else without explaining a tool.

## What it replaces
A hand-kept index page that goes stale after the third note, or a general static-site generator
that needs a theme, a config file and a build pipeline before it shows anything.

## What is hard
The note model. Notes are written in a hurry: some have a title line, some do not; some have a
date in the filename, some in the text; tags are inconsistent. Notes are plain markdown with no
frontmatter, so everything the index needs must be inferred or written into the body.

## What will not be built
- Editing notes in a browser.
- Sync between machines.
- A plugin system.

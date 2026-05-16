# User guides

User guides exist to help someone install, configure, and run the
software, and to understand the trade-offs well enough to make informed
choices. They are not architecture docs or contributor docs.

## Location

User guides live in the project's docs directory (typically `README.md`
for small projects, `docs/` for larger ones). Update the existing file
rather than creating a new one.

## What to include

- **Install**: prerequisites, install command, verification step.
- **Configure**: every config option, with defaults and trade-offs.
- **Run**: minimal "hello world" command, then common workflows.
- **Examples**: runnable and copy-pasteable. If a placeholder is
  needed (`<api-key>`), say where the value comes from.
- **Why**: what problem the software solves; key behavioural choices
  and their trade-offs, so users can decide whether the defaults fit.
- **References**: link to stable sources (official docs, RFCs) over
  blog posts. Use relative links for in-repo references.

Lead with a working example before exhaustive options.

## What to leave out

- Internal architecture, contributor workflow, API internals - those
  belong in `CONTRIBUTING.md` or architecture docs.
- Change history - that belongs in commit messages, PR descriptions,
  or `CHANGELOG.md`.

## Keep guides in sync with code

When a change affects user-visible behaviour (config keys, CLI flags,
defaults, output format, install steps), update the user guide in the
same commit. A PR that ships behaviour changes without doc updates
isn't ready to merge.

# Where rules and skills live

The rules and skills in this repository are shared by every project, so
they stay project-agnostic: no project's paths, commands, tools, package
names or conventions, and no dates, timings or measurements from one
project's runs. Give the reason for a rule in general terms ("a whole-tree
check on every task costs most of each task's time"), not as the incident
that prompted it; the incident belongs in that project's own records.

## Every file in the shared repository, not only rules

The same holds for everything committed to the shared repository: checker
code and its comments and docstrings, tests and their fixtures, specs, task
lists, user guides, `TODO.md` and `DONE.md`, and commit messages. A project
that prompted a change is "one project"; a fixture uses neutral names (`pkg`,
`probe`, `AppSettings`); a rule's history gives the date of the change, not
the review number that asked for it. What a change found when run against a
real project - its counts, its file paths, its review numbers - goes in the
report to the user and in that project's own records, never into a file or
commit here.

The shared repository's `no-project-names` hook enforces this against a list
of names kept outside it (a list inside it would name them).

## Project-specific rules and skills

Anything that holds for one project only - a command it provides, a path in
it, a decision made for it - goes in that project's own `claude/` directory
at the root of its workspace (`claude/rules/`, `claude/skills/`), loaded
from the workspace's `CLAUDE.md`. A shared rule may say "use the project's
tool where it has one"; the project's rule names the tool.

Before editing a file here, check that every line holds for any project.
If a change needs a project's specifics, write the generic part here and
the specific part in the project's `claude/` directory.

## Related

- [reviews.md](reviews.md), [python/testing.md](python/testing.md) -
  examples of the generic half of a rule

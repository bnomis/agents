# Where rules and skills live

The rules and skills in this repository are shared by every project, so
they stay project-agnostic: no project's paths, commands, tools, package
names or conventions, and no dates, timings or measurements from one
project's runs. Give the reason for a rule in general terms ("a whole-tree
check on every task costs most of each task's time"), not as the incident
that prompted it; the incident belongs in that project's own records.

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

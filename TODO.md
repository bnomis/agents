# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## The CI template says to pin actions to a commit SHA but pins tags

Found on 2026-11-01 in `claude/skills/project-setup/templates/ci.yml`,
whose comment reads "Pin third-party actions to a full commit SHA, and
let Dependabot update them", above `actions/setup-python@v7.1.0` and
`astral-sh/setup-uv@v10.3.3`, which are tags. This repository's own
`.github/workflows/ci.yml` pins tags too, and has a
`.github/dependabot.yml`.

Cause: the comment and the pins were never reconciled; the 2026-10-31
version bumps kept the tag form.

Fix direction: decide which holds. Either pin each action to its full
commit SHA, with the tag in a trailing comment, in the template and in
this repository's workflow, or drop the SHA advice from the comment. The
operator's call.

## A project with no audit root skips the project-level checks

Found on 2026-10-31 in `agents/specs/project-setup/spec.md`, amendment 1.2,
which records it as a known limit not fixed there. When a project has no
package under `src/` and no extra root, `audit.py` runs no pass, so the
per-root project-level checks (the lockfile, `AGENTS.md`, spec drift) never
run, and a project with no Python passes them without being checked.

Cause: the project-level checks run inside the per-root loop in `main()` of
`claude/skills/auditme/checks/audit.py`, once per root with duplicates
suppressed. With no root, they never run.

Fix direction: deferred until a project without Python adopts the guards.
Then run the project-level checks once when no root exists, which changes the
driver's contract, so it goes through the spec first.

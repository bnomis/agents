# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## The survey inventory lists a frozen spec as unimplemented

Found on 2026-11-13 by a survey of one project, run after the table-row and
checkbox status fix. A spec whose status reads `Frozen` (a plan kept as a
record, its work finished) is still listed as a spec not marked implemented,
so the survey reports a false lead.

Cause: `DONE_SPEC_RE` in `claude/skills/survey/inventory.py` lists the words
that mean a spec is finished (implemented, done, superseded, historical,
complete, index, archived), and `frozen` is not among them. The module
docstring's list of finished words has the same gap.

Fix direction: small, no spec. Add `frozen` to `DONE_SPEC_RE` and to the
docstring, and add a `probe` case with a `Frozen` status beside
`test_spec_status` in `claude/skills/survey/tests/test_inventory.py`.

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

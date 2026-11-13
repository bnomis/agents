# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## The survey inventory misreads specs and task lists that keep their status outside a `**Status:**` line

Found on 2026-11-13 in a survey of one project's workspace: specs whose
status sits in a header table row, `| **Status** | Implemented |`, were
reported as status "none", so implemented specs appeared as unimplemented
leads in more than one of its repositories. Confirmed on 2026-11-13 with a probe in
a scratch repository: a spec holding only `| **Status** | Implemented |` is
listed by `open_specs` as `status "none"; no task list`, and a task list
whose tasks carry only checkboxes (`- [x] one`, `- [ ] two`) and no
`**Status:**` line is not listed by `open_task_lists` at all, though a box is
unticked. The same workspace held task lists of that checkbox-only shape, and
a spec whose table row reads `Archived - ...`, a word `DONE_SPEC_RE` does
not accept.

Cause: `STATUS_RE` in `claude/skills/survey/inventory.py` matches only
`^\*\*Status:\*\*`. `open_specs` takes the first match and reports an empty
status as "none". `open_task_lists` builds its open list from `**Status:**`
lines only, so a list with none counts zero open tasks and is skipped: a
false negative, not a false lead. `DONE_SPEC_RE` has no `archived`.

Fix direction: read a status from either form, the `**Status:**` line and a
table row whose first cell is `**Status**`, in both `open_specs` and
`open_task_lists`; for a task list with no status in either form, count its
checkboxes and report it when any is unticked (`done/total` from the boxes);
add `archived` to `DONE_SPEC_RE`. Update the module docstring to name the
forms read. Add tests beside `test_spec_status` and
`test_open_task_list_is_reported_and_superseded_one_is_not` in
`claude/skills/survey/tests/test_inventory.py`, with neutral fixtures: a
`probe` spec with a table-row `Implemented` status is not listed, one with a
table-row `Draft` is; a checkbox-only task list with an unticked box is
listed, one with every box ticked is not. Small; no spec needed.

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

# DONE

Finished work, chronological, newest last. An item moves here from `TODO.md`
unchanged, followed by a `Done:` line. Never file a new item here.

## Shared Python rules carry one project's choices

Found on 2026-11-01 while writing the documentation site's rules page:

- `claude/rules/python/coding-standards.md:151` names one project's module
  path as an example of a CLI entry point, against `rule-scope.md`.
- `claude/rules/python/logging.md:28` ends "the only structured log-line
  prefix in this project", a fact about one project.
- `claude/rules/python/coding-standards.md:109` and
  `claude/rules/python/tools-and-libraries.md:14` prescribe `cappa` for
  command-line parsing, while `claude/rules/python/argparse.md` sets
  standards for argparse, and this repository's own scripts
  (`bin/install-claude.py`, `audit.py`, `changed.py`) use argparse.

Cause: these rules were brought in from a project and kept its specifics:
its paths, its log format, and its choice of argument parser.

Fix direction: make the first two generic (or move them into that
project's own `claude/rules/`), and decide with the operator which parser
the shared rules prescribe; then make `coding-standards.md`,
`tools-and-libraries.md` and `argparse.md` agree, or scope one of them to
projects that chose it.

Done: 2026-11-01 - branch `docs/python-rules-cappa`: the operator chose cappa for every CLI; `coding-standards.md`, `tools-and-libraries.md` and `argparse.md` now agree (argparse only in unconverted code and standard-library-only scripts), the project path in `coding-standards.md` is generic, and `logging.md` no longer states one project's fact.

## Skill texts break the repository's own conventions

Found on 2026-11-01 while writing the documentation site's skills page:

- `claude/skills/auditme/SKILL.md:199` points at
  `agents/skills/specdev/SKILL.md`; the skill lives at
  `claude/skills/specdev/SKILL.md` (installed as
  `~/.claude/skills/specdev/SKILL.md`).
- The commit messages these skills prescribe are not in the
  `type(scope): subject` form of `claude/rules/git-conventions.md`:
  `claude/skills/specdev/SKILL.md:216` (`specdev: ...`),
  `claude/skills/taskdev/SKILL.md:390` (`taskdev: ...`),
  `claude/skills/testplan/SKILL.md:88` (`testplan: add plan-N`) and
  `claude/skills/auditme/SKILL.md:251` (`auditme: add review-N`). The
  `TODO.md` skills already use `docs(todo): ...`.

Cause: the skill texts predate the commit conventions and the move of the
skills under `claude/skills/`, and were not updated with them.

Fix direction: fix the path, and give each skill a conventional message
(for example `docs(specs): ...`, `docs(tasks): ...`, `docs(tests): ...`,
`docs(audit): ...`). Text only; no spec needed.

Done: 2026-11-02 - on `main`: `auditme` now points at `claude/skills/specdev/SKILL.md`, and the `specdev`, `taskdev`, `testplan` and `auditme` skills prescribe `docs(specs)`, `docs(tasks)`, `docs(tests)` and `docs(audit)` commit messages.

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

Done: 2026-11-13 - branch `fix/survey-status-forms`: `inventory.py` reads a status from a `**Status:**` line or a `| **Status** |` table row (`statuses`), reports a task list with no status when a checkbox is unticked, and counts `archived` as a finished spec; tests `test_task_list_status_in_a_table_row_is_read`, `test_checkbox_only_task_list_is_reported_when_a_box_is_unticked` and `test_spec_status_in_a_table_row`.

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

Done: 2026-11-13 - branch `fix/survey-frozen-status`: `DONE_SPEC_RE` and the module docstring in `claude/skills/survey/inventory.py` count `frozen` as a finished spec; test `test_frozen_spec_is_finished`.

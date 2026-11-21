# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## The audit hooks read none of this repository's Python

Found on 2026-11-21 by review-1 (`agents/audit-reviews/review-1.md`,
Convergence note). This repository has no `src/`, and `bin/` holds no Python,
so `audit.py` with its default roots prints `no package under src/ and no extra
root; running the project-level checks only`. The `auditme-changed` and
`auditme-all` hooks run that default sweep, so the commit hook, the push hook
and CI check none of the scripts under `claude/` or the tests under `tests/`.
Review-1 and its task list (`agents/tasks/audit-reviews/tasks-1.md`) ran the
sweep by hand with `--extra-root claude --extra-root tests`, which found 7
unaccepted hits on 2026-11-21 and none after that list merged.

Cause: the sweep's roots are fixed by layout, and a project cannot declare
its own. The fix is in the auditor repository, filed there as "The audit
reads none of this repository's own Python" (`TODO.md` in `bnomis/auditor`):
let a project declare its audit roots in one place that `audit.py`,
`changed.py` and `phaseb.py` all read.

Fix direction: once that change is in auditor, bump this repository's
auditor pin, declare `claude` and `tests` as its roots in the way it provides,
and check that `pre-commit run auditme-all --hook-stage manual --all-files`
reports the scripts' hits. Small; waits for auditor.

Note 2026-11-21: auditor's change is in (`30637b8` on its `main`, its item
moved to its `DONE.md`): a project declares its roots as `[tool.auditme]
roots = [{ path = "..." }, ...]` in `pyproject.toml`, which `--extra-root`
overrides for one run. This item no longer waits; next step `/todo-do`.

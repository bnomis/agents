# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## Adopt the shared guards in each project

The shared guards exist, but no project uses them yet. Each open finding below
is closed by adopting them, and adopting the first project with a CI gate is
also the real CI run and the real deploy key that the end-to-end check never
did.

Found on 2026-10-31 by `/todo-review`. Task 9 of
`agents/tasks/project-setup/tasks-1.md` lists, in its Notes, the operator
steps for after the merge: run `bin/install-claude.py` on the real machine
(done: `~/.claude/settings.json` registers `auditme-stop.sh`, linked at 14:25
on 2026-10-31); `/project-setup adopt` in each project, the motivating one
first; and an `AGENTS_DEPLOY_KEY` for each project that enables the CI gate.
On 2026-10-31, none of the 7 repositories beside this one with a
`.pre-commit-config.yaml` carried an audit hook. Nor did this repository,
and a scratch run of the patched checker on it that day found 12 unaccepted
hits in `bin/`.

Fix direction: settle "The setup installs a `pre-push` hook that runs no audit
check" first, so no project is set up twice. Then run `/project-setup adopt`
in this repository, fixing or accepting its hits, and enable its CI gate with
a deploy key. That run is the real CI run and deploy key from the first
finding. Then adopt the motivating project, then the rest.

Note 2026-10-31: the `pre-push` item is settled and in `DONE.md`. `adopt` now
turns on the push stage together with the CI gate, once a project has zero hits.

Note 2026-10-31: this repository is adopted, on branch `feat/adopt-audit-hooks`.
Its 12 hits, all in `bin/install-claude.py`, were fixed, none accepted. The
operator chose `repo: local` hooks that run the checker from the working
tree, so no deploy key is needed here, plus a new `.github/workflows/ci.yml`.
Writing that workflow exposed two defects in
`claude/skills/project-setup/templates/ci.yml`: it set up Python 3.12,
where the checker's `except A, B:` syntax does not parse, and it never
installed `pre-commit`. Both are fixed and tested. The first real CI run is
this repository's first push after the merge. The real deploy key is now
first tested at the next project to adopt.

Note 2026-10-31: this repository's first real CI run (GitHub Actions
`41217991678`, at `70a50a4`) failed the whole-tree audit. The checker runs a
bare `ruff`, which `uv sync` installs only into `.venv`, so the run reported
`ruff not installed`. Since `fef77ba`, the workflow and the CI template put
`.venv/bin` on `PATH`, and the next run (`41218182723`) passed every step.
What remains: adopting the motivating project and the rest, and the first
real deploy key.

### Project-setup end-to-end checks that were never run

Found on 2026-10-31, after the project-setup queue (task list
`agents/tasks/project-setup/tasks-1.md`, merged to `main` as `69fa821`).
Task 9, the end-to-end check, was marked done, but the body of its commit
`9d99176` says four of its checks did not run:

1. **`bin/install-claude.py` as a command against a temporary `HOME`.** The
   sandbox refused to redirect `HOME`. In-process,
   `tests/test_install_claude.py::test_full_install_into_temporary_home` calls
   `install_claude()` twice with `HOME` monkeypatched, but it only asserts
   the Stop hook registration and that `auditme-stop.sh` exists. Nothing runs
   the script from a shell or checks the rest of what it installs.
2. **Walking `docs/setup.md` as written.** The run only checked that the
   files and commands the guide names exist. It did not follow the "A new
   machine" and "A new project" sections step by step. Even so, the Task 9
   subtask for that walk and its acceptance criterion ("the guide's walked
   sections needed no step it does not state") were ticked. Both are
   unticked as of 2026-10-31.
3. **A real CI run** of the audit gate in `templates/ci.yml` and
   `templates/ci-audit-step.yml`.
4. **A real deploy key**: the `AGENTS_DEPLOY_KEY` secret that the CI templates
   read, following `docs/setup.md` "The deploy key".

Cause: the queue's sandbox could not redirect `HOME` and cannot reach GitHub.
The unrun checks were recorded only in a commit body, and the task list was
ticked anyway.

Fix direction: do this by hand, outside the sandbox. In a throwaway directory
with `HOME` set to a temporary path, run `bin/install-claude.py` and then walk
`docs/setup.md`'s "A new machine" and "A new project" sections exactly as
written. Fix every step the guide leaves unstated. Then, in one real project,
add the deploy key and push, so CI runs the audit gate once and fails on a
planted unaccepted hit. Tick the Task 9 subtask and criterion again once the
walk passes.

Note 2026-10-31: the walk was done by hand in a scratch directory, with
`HOME` set to a temporary path and a local clone of this repository, on
branch `fix/setup-walk`:

- With no `~/.claude`, `bin/install-claude.py` crashed with
  `FileNotFoundError` on the first file it linked, because
  `install_claude()` never created the directory. The existing test hid this
  by creating `~/.claude` first. Fixed: the directory is now created, and
  `test_install_into_home_without_claude_dir` covers it. With that fix, the
  guide's "Check it" commands pass.
- The skill's check for leftover placeholders (`grep -rn '{{'`) always hit
  `ci.yml`, because of GitHub's own `${{ secrets.AGENTS_DEPLOY_KEY }}`.
  Fixed in `claude/skills/project-setup/SKILL.md` to match
  `\{\{[A-Z_]+\}\}`.
- In "A new project", the hooks pinned over SSH install and run. A
  leading-underscore hit in a package file blocks the commit with a clear
  message, and `auditme-all` passes on a clean tree.
- Two more findings need a decision. They are filed as their own items:
  "A new project cannot commit Python without a `src/<package>/` layout" and
  "The setup installs a `pre-push` hook that runs no audit check".

Still open: a real CI run and a real deploy key. Both change GitHub, so the
operator must confirm them.

Note 2026-10-31: since `3607aa2` (the installer fix) and amendment 1.2 (the
`src/` layout, `tasks-2.md`), the installer run and the guide walk are done;
only the real CI run and the real deploy key remain.

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

# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## A new project cannot commit Python without a `src/<package>/` layout

Found on 2026-10-31 while walking "A new project" in `docs/setup.md` in a
throwaway repository whose hooks were pinned at `3974fbb`. Committing
`bin/tool.py` failed `auditme-changed` with `the audit sweep exited 2:
ERROR: <repo>/src does not exist`. Committing a loose `src/a.py` failed with
`ERROR: no package under <repo>/src`. Only a commit with
`src/<package>/__init__.py` passed. Neither `docs/setup.md` nor the
`/project-setup new` skill mentions this layout, and `new` is meant for an
empty repository.

Cause: `main()` in `claude/skills/auditme/checks/audit.py` returns 2 when
`<scope>/src` is missing, or when `auditme.core._audit_roots()` finds no
package under it. It does this before `bin/` is considered, even though
`bin/` is one of the default extra roots (`EXTRA_ROOT_NAMES` in
`checks/auditme/core.py`). `checks/changed.py` treats any non-zero sweep exit
as a failure, so every commit that touches a `.py` file is blocked.

Fix direction: decide between two approaches. (a) The checker audits
whatever roots exist, so a project with no `src/` passes over `bin/` alone
and exits 0 when no root exists. (b) `/project-setup new` creates
`src/<project>/__init__.py`, and the guide states the layout. Option (a)
changes the checker's contract for every project, so it goes through the
project-setup spec first. Option (b) needs only a sentence in the spec and
in the guide.

Note 2026-10-31: the operator chose (a), and to report a `.py` file directly
in `src/` as a `src-loose-module` hit. Spec:
`agents/specs/project-setup/spec.md` (amendment 1.2); tasks: not yet written.

## Project-setup end-to-end checks that were never run

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

## The setup installs a `pre-push` hook that runs no audit check

Found on 2026-10-31 while walking "A new project" in `docs/setup.md`. The
`/project-setup` skill and the guide both run `pre-commit install
--hook-type pre-commit --hook-type pre-push`. But `.pre-commit-hooks.yaml`
publishes `auditme-changed` at `stages: [pre-commit]` and `auditme-all` at
`stages: [manual]`, and the template `.pre-commit-config.yaml` overrides
neither. So the `pre-push` hook git runs on each push checks nothing. The
shared rule `claude/rules/git-conventions.md` ("A rule a script can check is
a hook") says whole-tree checks run as a `pre-push` hook, and in CI.

Cause: the project-setup spec (`agents/specs/project-setup/spec.md`, "API")
put the whole-tree sweep at the manual stage and in CI only. The rule asks
for a `pre-push` stage as well. Nothing reconciles the two.

Fix direction: decide which one holds. Either add `pre-push` to
`auditme-all`'s stages (in `.pre-commit-hooks.yaml`, or in the template
config), which costs a whole-tree sweep on every push, or drop the
`pre-push` install from the skill, the guide and the rule. Whichever is
chosen, change the spec first.

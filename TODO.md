# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

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

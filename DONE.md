# DONE

Finished work, chronological, newest last. An item moves here from `TODO.md`
unchanged, followed by a `Done:` line. Never file a new item here.

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
`agents/specs/project-setup/spec.md` (amendment 1.2); tasks:
`agents/tasks/project-setup/tasks-2.md`.

Done: 2026-10-31 - b7f0e08, 8cb8502, 81212a5 (Tasks 1-3 of tasks-2.md); spec amendment 1.2; `agents/tasks/project-setup/tasks-2.md`.

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

Done: 2026-10-31 - the operator chose to switch the push gate on with the CI gate: the `new` template sets `stages: [manual, pre-push]` on `auditme-all`, `adopt` adds it only at zero hits, and the manifest keeps `[manual]`; `changed.py --all` names `SKIP=auditme-all git push`; spec amendment 1.3; branch `fix/audit-on-push`.

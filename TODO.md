# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

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

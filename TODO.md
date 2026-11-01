# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## The checker's docstrings and help, and the setup guide, disagree with the code

Found on 2026-11-01 while writing the documentation site's checker and
command-line pages, each checked against the code:

- The `changed.py` module docstring says "A sweep that cannot run fails; it
  is never skipped", but `main()` returns 0 without sweeping when no diff
  base resolves and when no reportable file changed (the two `return 0`
  branches before `sweep()` in `claude/skills/auditme/checks/changed.py`).
- `changed.py`'s `ACCEPT_HELP` tells the reader to accept any hit with an
  accept marker, but `ruff` and `lockfile-drift` hits are always emitted
  unaccepted (`claude/skills/auditme/checks/auditme/rules/project_hygiene.py`),
  so for those the advice cannot work.
- The `audit.py` docstring's output schema leaves out the `related` key that
  `core.py` emits and `changed.py` reads, and its acceptance list gives only
  the unscoped `# auditme: accept <reason>` marker, not the rule-scoped
  `accept[<rule>]` form the setup guide and `SKILL.md` recommend.
- `docs/setup.md` ("What you get") says directories other than `src/` and
  `bin/` are not swept, but `spec-api-signature-drift` reads every `.md`
  file under the project root outside the skipped directories, and the
  project-level checks read `pyproject.toml`, `uv.lock`,
  `.pre-commit-config.yaml` and `AGENTS.md`.
- `claude/statusline.py` is linked into `~/.claude/` by
  `bin/install-claude.py`, but nothing registers it as the status line, and
  `docs/setup.md` does not say to; on the operator's machine it is registered
  by hand in `~/.claude/settings.json`, so a new machine gets no status line.

Cause: the docstrings, help text and guide were written before the
behaviour they describe changed (the skip branches, the scoped marker, the
`related` key, the Markdown sweep), and the status line was set up by hand
outside the installer.

Fix direction: correct each text to match the code - say when `changed.py`
skips and why that is safe, give `ruff` and `lockfile-drift` their own fix
advice, add `related` and the scoped marker to the `audit.py` docstring, and
say in `docs/setup.md` what besides `src/` and `bin/` is read. For the status
line, either have the installer register it as it does the Stop hook, or add
the step to `docs/setup.md`; registering it changes the installer, so decide
that with the operator. No spec needed for the text fixes.

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

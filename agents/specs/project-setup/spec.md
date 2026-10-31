# Project setup

**Version:** 1.1
**Status:** proposed
**Date:** 2026-10-31

Every project that uses these rules and skills should get the same mechanical
guards by default: the auditme sweep on every commit, the whole-tree sweep in
CI, and the Claude Code Stop hook that refuses to end a turn over unaccepted
hits. Today only one project has them, built inside that project, and each copy
has gaps. This spec moves the guards into this repository, publishes them as
pre-commit hooks that a project pins by revision, adds a `/project-setup` skill
that installs them in a new project or adopts them into an existing one, and
documents the whole setup for a new machine, a new user and a new project.

## Motivation

Found 2026-10-31 by a full audit of a project that had the guards (its review
recorded why 344 unaccepted hits had passed every check). Each gap is in the
design, not the project:

- **The commit hook reports only files the branch changed.** When the checker
  gained a rule, every hit it found in files nobody touched afterwards stayed
  invisible: 341 of the 344, in 37 files of which one had been committed since
  the rule shipped.
- **Cross-file rules name one file.** A rule comparing two files emits a hit on
  each location; when the changed file's copy carries an accept marker, the hit
  that remains names the unchanged file, which the scope filter drops. All three
  non-alias hits were this case.
- **In CI the scope is empty.** On a push the diff base `origin/main` is the
  pushed commit itself, so no file counts as changed; that project's CI printed
  "no new audit hits in changed files ... Passed" over a tree holding 341 or more
  unaccepted hits.
- **Only one project had any of it.** Of the projects checked out beside this
  repository on 2026-10-31, one carried the hook; the rest had pre-commit
  configurations with no audit step.
- **The checker is unpinned.** Projects run the skill through the
  `~/.claude/skills` symlink, so a checker change reaches every project the
  moment it is committed here, with no commit in the project to show its
  catch-up surface - the auditme skill's own failure mode 1.

## Module location

| Path | What it is |
|------|------------|
| `claude/skills/auditme/checks/changed.py` | The changed-files runner (new): runs the sweep, filters by scope, exits non-zero on unaccepted hits |
| `claude/skills/auditme/checks/auditme/core.py` | `_emit()` gains the optional `related` field |
| `claude/skills/auditme/checks/auditme/rules/*.py` | Each cross-file rule passes `related` |
| `.pre-commit-hooks.yaml` | At the repository root (new): publishes `auditme-changed` and `auditme-all` |
| `claude/hooks/auditme-stop.sh` | The Stop hook (new) |
| `bin/install-claude.py` | Also registers the Stop hook in `~/.claude/settings.json` |
| `claude/skills/project-setup/SKILL.md` | The skill (new), with `templates/` beside it |
| `docs/setup.md` | The user guide (new); `README.md` gains an overview linking to it |
| `claude/skills/auditme/tests/test_changed.py`, `tests/test_install_claude.py` | Tests (new) |

## API

### The runner

```python
def changed_files(repo_root: pathlib.Path, base: str) -> frozenset[str]:
    """Repository-relative paths changed in base...HEAD, deletions excluded.

    Side effect: runs `git diff --name-only --diff-filter=d`.

    Raises:
        ChangedError: git cannot be run, or the diff fails.
    """


def in_scope(hit: Mapping[str, object], scope: frozenset[str] | None) -> bool:
    """Whether a hit is reported: always when scope is None (--all), else when its
    path or any of its related paths is in scope. Pure."""


def main(argv: Sequence[str] | None = None) -> int:
    """0 when no unaccepted hit is in scope, 1 otherwise or on any failure."""


class ChangedError(Exception):
    """The runner could not decide which files changed, or could not run the sweep."""
```

Invocation: `changed.py [--all] [--base <ref>] [<repo-root>]`, `<repo-root>`
defaulting to `git rev-parse --show-toplevel` of the working directory.

### The hooks

`auditme-changed` (commit stage) and `auditme-all` (manual stage), published in
`.pre-commit-hooks.yaml`; see [The published hooks](#the-published-hooks).

### The skill

```text
/project-setup new [<path>]
/project-setup adopt [<path>]
```

`<path>` defaults to the working directory's repository root. Frontmatter
matches the other skills in `claude/skills/`, with
`allowed_tools: [Read, Write, Edit, Bash, AskUserQuestion]`.

## Error handling

| Failure | Result |
|---------|--------|
| git missing, or `git diff` / `rev-parse` fails for a reason other than an unresolved ref | `ChangedError`, exit 1 |
| `--base` starting with `-` | exit 1, before git runs |
| No base resolves (no upstream, no `origin/main`, no `main`) | exit 0 with a message |
| Sweep timeout, exception, non-JSON line, or an `auditme-check-crash` hit | exit 1 naming the cause |
| Unaccepted hits in scope | exit 1, listing them |
| Stop hook: project not opted in, or `stop_hook_active` already true | exit 0, no output |
| `install-claude.py`: `~/.claude/settings.json` is not valid JSON | refuse, naming the file; nothing written |

## Implementation

### The changed-files runner

A generic version of the runner the motivating project keeps in its own `bin/`,
with the gaps closed. It is stdlib-only, like the rest of the checker.

- **Diff base**, when neither `--all` nor `--base` is given: the first of
  `@{upstream}`, `origin/main`, `main` that resolves. None resolving exits 0 with
  a message (a repository with no history to compare). A `--base` starting with
  `-` is refused before git runs.
- **The sweep** runs as a subprocess, `[sys.executable, <checks>/audit.py,
  <repo-root>]`, the `audit.py` beside `changed.py`, with no `--package`, so it
  covers the whole tree and cross-file rules see every file. `audit.py` itself is
  unchanged apart from `related` (amended 2026-10-31: the first draft said
  in-process, which contradicted the timeout and non-JSON handling below and
  named a driver function `audit.py` does not have).
- **Skip when nothing reportable changed**: as today, a scope holding no `.py`
  file, no reportable `.md` file and no `uv.lock` exits 0 without sweeping. The
  reportable set is read from the checker's own constants, not mirrored.
- **Output**: each reported hit as `path:line  rule`, then its variant, then how
  to accept one (`# auditme: accept[<rule>] <reason>`) and how to skip once
  (`SKIP=auditme-changed git commit`).

**Cross-file hits carry `related`.** `_emit()` takes an optional
`related: list[str]` of repository-relative paths, omitted when empty so a hit
without it is byte-identical to today's. Every rule whose predicate compares
locations in two or more files sets it to the other locations' paths:
`literal-duplication`, `paired-sibling-helpers`, `duplicate-call-sequence`,
`recompile-duplication`, `spec-api-signature-drift` (the source file),
`asymmetric-exception-translation` (the callee's file) and
`mutable-module-level-exported` (the reading modules). A test asserts the list,
so a cross-file rule added later without `related` fails it. This changes the
JSONL bytes of those rules' hits; it ships between audit cycles, and each
project's next audit summary notes it.

**A sweep that cannot run fails.** The project-local runner skipped (exit 0) when
the skill was missing, the sweep timed out or crashed; that is the same fail-open
as the empty CI scope. Here a missing checker cannot happen (the hook runs the
checker beside it), and a timeout, crash, non-JSON line or `auditme-check-crash`
hit exits 1 naming the cause. The timeout is 600 seconds.

### The published hooks

`.pre-commit-hooks.yaml` at the repository root:

```yaml
- id: auditme-changed
  name: no unaccepted audit hits in changed files
  entry: claude/skills/auditme/checks/changed.py
  language: script
  pass_filenames: false
  always_run: true
  stages: [pre-commit]
- id: auditme-all
  name: no unaccepted audit hits anywhere
  entry: claude/skills/auditme/checks/changed.py --all
  language: script
  pass_filenames: false
  always_run: true
  stages: [manual]
```

A project adds them by revision, which is what pins the checker:

```yaml
- repo: git@github.com:bnomis/agents.git
  rev: <commit of this repository>
  hooks:
    - id: auditme-changed
    - id: auditme-all
```

`language: script` runs the file with its own `#!/usr/bin/env python3`, so the
interpreter is the one on `PATH`, which must meet this repository's
`requires-python`. Upgrading the checker is `pre-commit autoupdate --repo
git@github.com:bnomis/agents.git` in the project: one commit, whose CI run shows
the new rules' catch-up surface.

#### CI

The CI step, in the project's workflow after its own setup:

```yaml
- name: Audit the whole tree
  run: pre-commit run auditme-all --hook-stage manual --all-files
```

The repository is private, so the runner needs read access to it. Decided with
the operator 2026-10-31: **a deploy key per project**. The project holds an
`AGENTS_DEPLOY_KEY` secret, the private half of an SSH key added read-only to
this repository's deploy keys, and its workflow installs it before pre-commit
runs, with `Host github.com` / `IdentityFile` / `IdentitiesOnly yes` in
`~/.ssh/config`. A project that already uses a deploy key for another private
repository on the same host needs an `ssh` host alias per key, because GitHub
admits one deploy key per repository; the template uses `github-agents` as the
alias and rewrites the hook's URL to it with `git config --global
url."git@github-agents:bnomis/agents.git".insteadOf
"git@github.com:bnomis/agents.git"`.

### The Stop hook

`claude/hooks/auditme-stop.sh`, registered once. Decided with the operator
2026-10-31: **global, opt-in by project**.

- `bin/install-claude.py` adds a `Stop` entry running the hook to
  `~/.claude/settings.json`, merging into what is there: it parses the file,
  adds the entry only if no `Stop` hook already runs this script, writes the
  result atomically, and keeps the original as `settings.json.orig` the first
  time. Running it twice changes nothing.
- The hook exits 0 at once unless the working directory is in a git repository
  whose `.pre-commit-config.yaml` lists `id: auditme-changed`.
- It exits 0 when the payload's `stop_hook_active` is true, so it blocks at most
  once per turn.
- Otherwise it runs `python3 -I ~/.claude/skills/auditme/checks/changed.py`; on
  exit 1 it prints the Claude Code block decision (`{"decision": "block",
  "reason": ...}`, built with `jq -Rs`) carrying the runner's report.

It runs the **installed** checker, not the project's pinned one: it is the
earliest warning, and the binding gates - the commit hook and CI - run the pinned
one. A project's own `.claude/settings.json` Stop hook doing the same job is
removed when the project adopts this one, or every turn runs the sweep twice.

### The `/project-setup` skill

`claude/skills/project-setup/SKILL.md`, invoked as
`/project-setup new [<path>]` or `/project-setup adopt [<path>]`. It confirms
before each outward-facing step (creating a deploy key, setting a secret,
committing) and never pushes.

**`new`**, in an empty or freshly initialised repository:

1. Write `.pre-commit-config.yaml` from `templates/pre-commit-config.yaml`: ruff
   check and format, shellcheck, and the two auditme hooks pinned to this
   repository's `origin/main` commit.
2. Write `.github/workflows/ci.yml` from `templates/ci.yml`: checkout, the deploy
   key step, Python and uv, `uv sync`, `pre-commit run --all-files`, the
   `auditme-all` step and the project's test command (asked).
3. Write `AGENTS.md`, `CLAUDE.md` (`@AGENTS.md`), `TODO.md`, `DONE.md` and
   `claude/rules/README.md` from templates, the title from the project name.
4. Run `pre-commit install`, then the deploy-key steps below.

**`adopt`**, in an existing project:

1. Add the two hooks to `.pre-commit-config.yaml` (create it if absent); remove
   any project-local hook or Stop hook that does the same job, after showing it.
2. Run `pre-commit run auditme-all --hook-stage manual --all-files` and count the
   unaccepted hits by rule.
3. **Zero**: add the CI step and the deploy-key steps. **More than zero**: file
   one `TODO.md` item recording the count by rule and the date, whose Fix
   direction is to fix or accept every hit and then add the CI step - the gate is
   never enabled over a backlog, because a gate that fails every push is switched
   off, and one that is not switched on cannot be.
4. Commit the hook and `TODO.md` changes as `build(audit): adopt the shared audit
   hooks`, when the operator agrees.

**Deploy-key steps** (asked before each): `ssh-keygen -t ed25519 -N '' -f
<scratch>/agents_deploy_key`; `gh repo deploy-key add <scratch>/agents_deploy_key.pub
--repo bnomis/agents --title <project>`; `gh secret set AGENTS_DEPLOY_KEY --repo
<owner>/<project> < <scratch>/agents_deploy_key`; then delete both files. The
private key is never printed.

## Documentation

`docs/setup.md`, the user guide, written for someone who has not seen this
conversation or the project that motivated it, in this order:

1. **What you get** - the guards, what each catches, and why the commit hook is
   scoped to changed files while CI sweeps the whole tree.
2. **A new machine** - prerequisites (`git`, `gh` authenticated, an SSH key on
   GitHub with access to this repository, `uv`, `pre-commit` via `uv tool
   install pre-commit`, Python meeting `requires-python`, `jq`); clone this
   repository; run `bin/install-claude.py`; check it (`ls ~/.claude/skills`,
   the `Stop` entry in `~/.claude/settings.json`).
3. **A new user** - being given read access to this repository; their own SSH
   key; that rules and skills are shared and project specifics go in the
   project's `claude/` directory (`claude/rules/rule-scope.md`).
4. **A new project** - `/project-setup new`, what it writes, and the deploy key.
5. **An existing project** - `/project-setup adopt`, the backlog step, and
   enabling the CI gate.
6. **Upgrading the checker** - `pre-commit autoupdate`, and handling its
   catch-up hits in the same commit.
7. **Troubleshooting** - the hook cannot clone (SSH, the deploy key, the host
   alias); the Stop hook does not fire (not opted in, `jq` missing); hits appear
   only after an upgrade (expected); `SKIP=auditme-changed` for one commit.

Every command in it is runnable as written, with placeholders saying where the
value comes from. `README.md` gains a short section saying what the repository
is and linking to `docs/setup.md`.

## Testing

`uv run --no-project --with pytest pytest claude/skills/auditme/tests`, plus:

- `test_changed.py`, against a temporary git repository: scope from the diff
  base; `--all`; a hit reported through `related` when only its peer changed;
  `--base -x` refused; no base resolves; a sweep crash, timeout and non-JSON line
  each exit 1; nothing reportable changed skips the sweep.
- Each cross-file rule's test asserts its hits' `related`; `test_registry.py`
  asserts the set of rules that emit `related` equals the list above.
- `test_install_claude.py`: the Stop entry is added once, an existing
  `settings.json` keeps every other key, an invalid file is refused.
- The Stop hook: a shell test running it with a stub payload in an opted-in and a
  non-opted-in repository.

## Acceptance criteria

- A project pinning the hooks at this repository's commit fails a commit that
  adds an unaccepted hit, and fails CI on an unaccepted hit in a file the push
  did not touch.
- A cross-file hit whose named file is unchanged is reported when its peer
  changed.
- `audit.py`'s output is byte-identical to the previous commit's for every hit
  without `related`.
- `/project-setup new` in an empty repository and `/project-setup adopt` in an
  existing one each leave a working, committed setup; `adopt` adds no CI gate
  over a non-zero count.
- `docs/setup.md` takes a new machine from nothing to a passing hook run.

## External dependencies

`git`, `pre-commit` (the remote-hook mechanism, `language: script`, the `manual`
stage), `gh` (deploy keys and secrets), `ssh-keygen`, `jq` (the Stop hook), and
GitHub deploy keys (read-only, one per repository). The checker stays
stdlib-only.

## Consumers

Background only; each is its own repository's work. The project whose review
motivated this adopts the hooks in its review task list, replacing its
`bin/audit-changed.*` and its own Stop hook, and that work waits for this spec's
implementation. Every other project adopts with `/project-setup adopt`.

# Command line and hooks

Reference for the scripts in this repository and the hooks it publishes. For
installation see [Setup](../setup.md); for what the checker's rules report
see [The checker](../guide/checker.md).

## `bin/install-claude.py`

```text
install-claude [-h]
```

Links the contents of `claude/` into `~/.claude/` and registers the Stop
hook. It takes no options.

On disk:

- Creates `~/.claude/` if it is missing.
- For each top-level entry of `claude/` (dotfiles skipped):
    - a file (`CLAUDE.md`, `statusline.py`) becomes a symlink in `~/.claude/`;
    - a directory (`hooks/`, `rules/`, `skills/`) becomes a real directory in
      `~/.claude/`, and each entry inside it becomes a symlink, so
      `~/.claude/skills/auditme` links to `claude/skills/auditme/`.
- Symlinks are relative. An existing symlink at the target is replaced; an
  existing file or directory is renamed with a `.orig` suffix (numbered when
  that name is taken).
- Prints any dangling symlinks found in `~/.claude/` and its immediate
  subdirectories, with an `rm` command to remove them. It does not remove
  them.
- Adds a Stop hook entry running `bash "$HOME/.claude/hooks/auditme-stop.sh"`
  to `~/.claude/settings.json`, unless a Stop hook command already names
  `auditme-stop.sh`. Every other key and hook is kept. Before the first change
  to an existing file it copies it to `settings.json.orig`, once; it writes
  through a temporary file and keeps the file's mode. A missing file is
  created.

The settings file is read after the symlinks are made. If it is not valid
JSON, or not a JSON object, the installer leaves it unchanged and exits; the
symlinks are already in place.

`statusline.py` is linked but not registered: nothing writes a `statusLine`
entry to `settings.json`.

| Exit | Meaning |
|---|---|
| `0` | Installed, or `--help` |
| `1` | `settings.json` is not valid JSON or not a JSON object; the message names the file |
| `2` | Unknown argument |

Environment: `HOME` (through `pathlib.Path.home()`).

## `bin/check-foreign-names.sh`

```text
check-foreign-names.sh [--allow=<name>]... [--] <file>...
```

Fails when a file names a project on a list kept outside the repository, so
that the list itself is never committed. It is the entry of the
`no-project-names` hook and changes nothing on disk.

- The list is one name per line; blank lines and lines starting with `#` are
  skipped.
- Matching is whole-word, case-insensitive and literal (`grep -w -i -F`): a
  name inside a longer word does not match.
- `--allow=<name>` removes that name from the list for this run (compared
  case-insensitively against whole lines). Repeatable. A repository used
  across projects passes its own name this way.
- Each match is printed as `file:line:text`, followed by a pointer to
  `claude/rules/rule-scope.md`.

| Exit | Meaning |
|---|---|
| `0` | No match; or no list file (a notice goes to stderr and nothing is checked); or the list is empty after comments and `--allow`; or no files given |
| `1` | At least one match |

Environment: `AGENTS_FOREIGN_NAMES` (path of the list), `HOME` (the default
list is `~/.config/agents/foreign-names`).

## `claude/skills/auditme/checks/audit.py`

```text
audit.py [-h] [--package PACKAGE] [--extra-root DIR] scope
```

The checker driver. Runs every registered check over the project at `scope`
and prints one JSON object per hit on stdout. It reads the tree and writes
nothing.

| Option | Effect |
|---|---|
| `scope` | Project root. |
| `--package PACKAGE` | Audit only `src/PACKAGE`. Drops the extra roots and the loose-module check. For re-checking one package; a normal audit passes neither option. |
| `--extra-root DIR` | Audit `DIR` (relative to `scope`) as its own pass. Repeatable. Replaces the default extra root, `bin/`; each named directory must exist. |

Without options it audits every package under `src/`, each in its own pass,
then `bin/` when it exists and holds `.py` files. A `.py` file directly in
`src/` is reported as `src-loose-module`.

Each output line carries `rule`, `variant`, `path`, `line`, `evidence`,
`accepted` and `accepted_reason`; a hit from a rule that compares several
files also carries `related`, the other files involved. Identical hits are
printed once. A check that raises is reported as an `auditme-check-crash`
hit, and the sweep continues.

| Exit | Meaning |
|---|---|
| `0` | Sweep completed, whatever it found; also when there is nothing to audit (a notice goes to stderr) |
| `2` | `scope`, a named `--extra-root` or the `--package` directory does not exist; or an argument error |

The exit status does not reflect hits: callers read stdout.

Environment: the checks run `ruff` and `uv` as subprocesses with the caller's
environment, finding them through `PATH` (ruff from the project's
`.venv/bin/ruff` first). When `uv lock --check` fails because of a user-level
`exclude-newer` setting, it is rerun with `UV_NO_CONFIG` set.

## `claude/skills/auditme/checks/changed.py`

```text
changed.py [-h] [--all] [--base BASE] [repo_root]
```

The entry of the `auditme-changed` and `auditme-all` hooks. Runs `audit.py`
over the whole tree with the same interpreter (timeout 600 seconds), then
reports every unaccepted hit in scope. It writes nothing.

| Option | Effect |
|---|---|
| `repo_root` | Repository root. Default: `git rev-parse --show-toplevel` of the working directory. |
| `--all` | Report every unaccepted hit, not only those in changed files. |
| `--base BASE` | Diff base. Default: the first of `@{upstream}`, `origin/main`, `main` that resolves. A value starting with `-` is refused. |

Without `--all`, the scope is the files changed in `BASE...HEAD` plus those
changed in the index or working tree against `HEAD`, deletions excluded. A
hit is in scope when its `path` or any of its `related` paths is in scope, so
a cross-file hit on an untouched file fails when its peer changes.

Without `--all`, the sweep is skipped (exit `0`, with a message) when:

- no diff base resolves; or
- no changed file is reportable: a `.py` file, a `uv.lock`, or a `.md` file
  outside hidden directories and outside `.git`, `.venv`, `node_modules`,
  `__pycache__`, `audit-reviews` and `tasks`.

Each reported hit prints as `path:line  rule` with its variant indented
beneath, then how to accept a hit and how to skip the hook once
(`SKIP=auditme-changed git commit`, or `SKIP=auditme-all git push` with
`--all`). All output goes to stdout.

| Exit | Meaning |
|---|---|
| `0` | No unaccepted hit in scope; the sweep was skipped as above; or `--help` |
| `1` | An unaccepted hit in scope; or any failure: argument error, `--base` refused, git failed, the sweep timed out, exited non-zero, printed a line that is not a JSON object, or reported a crashed check (even one outside the scope) |

Environment: none directly; git and `audit.py` inherit the caller's.

## `claude/statusline.py`

```text
statusline.py < status.json
```

A Claude Code status line command. Reads the session's status JSON on stdin
and prints one line of the available parts joined by ` | `:

| Part | Source |
|---|---|
| Model name | `model.display_name` |
| `ctx: N%` | `context_window.used_percentage` |
| `5h: N%` | `rate_limits.five_hour.used_percentage` |
| `cwd: <dir>` | `workspace.current_dir` |
| `git: <branch>+S~M` | `git` in the working directory: `S` files staged (green), `M` modified (yellow); omitted outside a repository |

A missing or zero field is left out. It writes nothing. It exits `0`, or `1`
with a traceback when stdin is not JSON. Environment: none.

The installer links it to `~/.claude/statusline.py` but does not configure it
as the status line.

## Published pre-commit hooks

`.pre-commit-hooks.yaml` publishes these hooks for other projects to pin by
`rev`. This repository runs the same entries from its own tree as `repo:
local` hooks in `.pre-commit-config.yaml`, so a checker change applies in the
commit that makes it.

| Hook id | Stages as published | Entry | Checks | In this repository |
|---|---|---|---|---|
| `auditme-changed` | `[pre-commit]` | `claude/skills/auditme/checks/changed.py` | Unaccepted checker hits in the files the change touches | Same stage |
| `auditme-all` | `[manual]` | `claude/skills/auditme/checks/changed.py --all` | Unaccepted checker hits anywhere | `[manual, pre-push]`: runs on every push |
| `no-project-names` | `[pre-commit, commit-msg]` | `bin/check-foreign-names.sh` | Project names in staged files and the commit message; `uv.lock` excluded | Same stages, no `--allow` |

Both audit hooks set `pass_filenames: false` and `always_run: true`: they
find their own scope and run even when no file is staged. `no-project-names`
receives the staged file names, or the commit message file at `commit-msg`.
Every hook uses `language: script`, so the entry runs from the hook
repository with the interpreter its shebang finds (`python3` for
`changed.py`).

To run the manual hook by hand:

```shell
pre-commit run auditme-all --hook-stage manual --all-files
```

This repository's config also runs `ruff-check`, `ruff-format` and
`shellcheck`; those come from their own repositories and are not published
here.

## The Stop hook

`claude/hooks/auditme-stop.sh` is a Claude Code Stop hook: Claude Code runs it
when Claude is about to end a turn, with the event JSON on stdin.

It does nothing (exit `0`, no output) when:

- the payload's `stop_hook_active` is `true`, meaning the turn is already
  continuing because of an earlier block, so it blocks at most once in a row;
- the working directory is not in a git repository;
- the project is not opted in: its root `.pre-commit-config.yaml` does not
  contain the text `id: auditme-changed`.

Otherwise it runs the installed checker, not the project's pinned one, from
the repository root:

```shell
python3 -I "$HOME/.claude/skills/auditme/checks/changed.py"
```

When that exits `1` it prints `{"decision": "block", "reason": "<report>"}`,
and Claude Code keeps the turn going with the report as the reason. Since
`changed.py` exits `1` on a failed sweep as well as on hits, a sweep that
cannot run also blocks. The hook itself always exits `0` and writes nothing
to disk.

Requires `jq`, `git` and `python3` on `PATH`. Environment: `HOME`.

### Registration

`bin/install-claude.py` adds it once to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$HOME/.claude/hooks/auditme-stop.sh\""
          }
        ]
      }
    ]
  }
}
```

It is global, but acts only in opted-in projects. Check it with
`grep -n 'auditme-stop.sh' ~/.claude/settings.json`.

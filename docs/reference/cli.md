# Command line and hooks

Reference for the scripts in this repository and the hook it publishes. The
auditme checker, its hooks and the Stop hook are documented in the auditor
repository (`bnomis/auditor`, <https://bnomis.github.io/auditor/reference/cli/>).

## `bin/install-claude.py`

```text
install-claude [-h]
```

Links the contents of `claude/` into `~/.claude/`, and registers the status
line. It takes no options.

On disk:

- Creates `~/.claude/` if it is missing.
- For each top-level entry of `claude/` (dotfiles skipped):
    - a file (`CLAUDE.md`, `statusline.py`) becomes a symlink in `~/.claude/`;
    - a directory (`rules/`, `skills/`) becomes a real directory in
      `~/.claude/`, and each entry inside it becomes a symlink, so
      `~/.claude/skills/ship` links to `claude/skills/ship/`.
- Symlinks are relative. An existing symlink at the target is replaced; an
  existing file or directory is renamed with a `.orig` suffix (numbered when
  that name is taken).
- Prints any dangling symlinks found in `~/.claude/` and its immediate
  subdirectories, with an `rm` command to remove them. It does not remove
  them.
- Sets `statusLine` to `{"type": "command", "command": "~/.claude/statusline.py"}`
  in `~/.claude/settings.json`, unless a `statusLine` is already set, in which
  case it is left as it is. Every other key is kept. Before the first change
  to an existing file it copies it to `settings.json.orig`, once; it writes
  through a temporary file and keeps the file's mode. A missing file is
  created.

The settings file is read after the symlinks are made. If it is not valid
JSON, or not a JSON object, the installer leaves it unchanged and exits; the
symlinks are already in place.

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

The installer links it to `~/.claude/statusline.py` and sets it as the status
line, unless one is already set.

## Published pre-commit hooks

`.pre-commit-hooks.yaml` publishes this hook for other repositories to pin by
`rev`. This repository runs the same entry from its own tree as a `repo:
local` hook in `.pre-commit-config.yaml`.

| Hook id | Stages as published | Entry | Checks | In this repository |
|---|---|---|---|---|
| `no-project-names` | `[pre-commit, commit-msg]` | `bin/check-foreign-names.sh` | Project names in staged files and the commit message; `uv.lock` excluded | Same stages, no `--allow` |

`no-project-names` receives the staged file names, or the commit message file
at `commit-msg`. It uses `language: script`, so the entry runs from the hook
repository with the interpreter its shebang finds.

The auditme hooks this repository runs are pinned from the auditor repository
(`bnomis/auditor`, <https://bnomis.github.io/auditor/>). Its config also runs
`ruff-check`, `ruff-format` and `shellcheck`; those come from their own
repositories and are not published here.

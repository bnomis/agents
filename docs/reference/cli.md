# Command line and hooks

Reference for the scripts in this repository and the hooks it runs. The
auditme checker, the `no-project-names` check, their hooks and the Stop hook
are documented in the auditor repository (`bnomis/auditor`, <https://bnomis.github.io/auditor/reference/cli/>).

## `bin/install-claude.sh`

```text
bin/install-claude.sh [--dry-run] [any other install-in-claude option]
```

Links the contents of `claude/` into `~/.claude/`, and sets the status line,
by running the shared installer
[install-in-claude](https://github.com/bnomis/install-in-claude) at the commit
pinned in the script's `INSTALL_IN_CLAUDE_REV`:

```shell
uvx --from "git+ssh://git@github.com/bnomis/install-in-claude.git@$INSTALL_IN_CLAUDE_REV" \
    install-in-claude --source "$REPO/claude" \
    --set-if-absent 'statusLine={"command":"~/.claude/statusline.py","type":"command"}'
```

Its own arguments pass through: `bin/install-claude.sh --dry-run` prints what
would change and changes nothing. It needs `uv`, and SSH access to
`bnomis/install-in-claude` for the first run of a pinned commit; `uvx` caches
it after that.

What the installer does, in short (its README has the detail):

- Checks every option and reads `~/.claude/settings.json` first; a settings
  file that is not a valid JSON object stops it, exit `1`, before anything is
  linked or written.
- For each top-level entry of `claude/` (dotfiles skipped): a file
  (`CLAUDE.md`, `statusline.py`) becomes a symlink in `~/.claude/`; a
  directory (`rules/`, `skills/`) becomes a real directory in `~/.claude/`
  whose entries are symlinks, so `~/.claude/skills/ship` links to
  `claude/skills/ship/`. Links are relative. An existing symlink is replaced;
  an existing file is renamed with a `.orig` suffix (numbered when that name
  is taken).
- Prints any dangling symlinks in `~/.claude/` and its immediate
  subdirectories, with a quoted `rm` command to remove them. It does not
  remove them.
- Sets `statusLine` to `{"type": "command", "command": "~/.claude/statusline.py"}`
  in `~/.claude/settings.json`, unless a `statusLine` is already set, in which
  case it is left as it is. Every other key is kept; the first original is
  copied to `settings.json.orig`; the file is written atomically and keeps its
  mode.

| Exit | Meaning |
|---|---|
| `0` | Installed, or nothing to do |
| `1` | `settings.json` is not valid JSON or not a JSON object; nothing changed |
| `2` | A bad argument; nothing changed |

Environment: `HOME`.

To upgrade the installer, set `INSTALL_IN_CLAUDE_REV` to a newer commit
(`git ls-remote git@github.com:bnomis/install-in-claude.git refs/heads/main`,
first field) and run `bin/install-claude.sh --dry-run` to see what it changes.

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

## Pre-commit hooks

This repository publishes no hooks. Its `.pre-commit-config.yaml` pins
`auditme-changed`, `auditme-all` (at `[manual, pre-push]`) and
`no-project-names` from the auditor repository (`bnomis/auditor`,
<https://bnomis.github.io/auditor/reference/cli/>), which documents each
one. It also runs `ruff-check`, `ruff-format` and `shellcheck` from their own
repositories.

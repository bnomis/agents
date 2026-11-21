# agents

Shared rules and skills for Claude Code, and the status line.

`bin/install-claude.sh` links `claude/` into `~/.claude/`, with the shared
installer `install-in-claude`. The auditme checker, its pre-commit hooks, the
`no-project-names` hook, the Stop hook and `/auditme-project-setup` are in the
auditor repository (`bnomis/auditor`, <https://bnomis.github.io/auditor/>).

## Working on this repository

Install the hooks, including the commit-message one:

```shell
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

Everything here is shared by every project, so no file or commit message names
one (`claude/rules/rule-scope.md`). The `no-project-names` hook, pinned from
the auditor repository, enforces that against a list kept outside the
repository, one name per line, at `~/.config/auditor/foreign-names` (or the
file `$AUDITOR_FOREIGN_NAMES` names).
Without the list the hook checks nothing and says so, which is also what
happens in CI.

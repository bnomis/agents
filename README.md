# agents

Shared rules, skills and hooks for Claude Code, and the audit checker
(`auditme`) that projects pin as pre-commit hooks.

`bin/install-claude.py` links `claude/` into `~/.claude/`. The setup guide,
from a new machine to a project with working guards, is
[docs/setup.md](docs/setup.md).

## Working on this repository

Install the hooks, including the commit-message one:

```shell
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

Everything here is shared by every project, so no file or commit message names
one (`claude/rules/rule-scope.md`). The `no-project-names` hook enforces that
against a list kept outside the repository, one name per line, at
`~/.config/agents/foreign-names` (or the file `$AGENTS_FOREIGN_NAMES` names).
Without the list the hook checks nothing and says so, which is also what
happens in CI.

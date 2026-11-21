# agents

![The agents logo](assets/agents-mark.svg){ align=right width="128" }

Shared [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) rules and skills, and
the status line.

```shell
git clone git@github.com:bnomis/agents.git ~/src/agents
~/src/agents/bin/install-claude.sh
```

The installer links the contents of `claude/` into `~/.claude/`, so the rules load in every Claude
Code session and each skill becomes a slash command in every project. It also sets
`claude/statusline.py` as the status line unless one is already set; see
[Command line and hooks](reference/cli.md).

The auditme checker, its pre-commit hooks, the Stop hook and `/auditme-project-setup` are in the auditor
repository (`bnomis/auditor`, <https://bnomis.github.io/auditor/>).

## What is in the repository

| Path | What it is |
|---|---|
| `claude/rules/` | Rules loaded into every session: git, Python, reviews, security and the rest. See [Rules](reference/rules.md). |
| `claude/skills/` | Slash commands for specs, task lists, the `TODO.md` workflow, shipping and cleanup. See [Skills](reference/skills.md). |
| `claude/statusline.py` | The Claude Code status line. |
| `bin/` | The installer. See [Command line and hooks](reference/cli.md). |

## Where to start

1. Read [How it works](concepts.md) for the moving parts and why each is where it is.
2. Look things up in the reference: [Skills](reference/skills.md), [Rules](reference/rules.md) and
   [Command line and hooks](reference/cli.md).

## Why

- **A rule a script can check is a hook.** A rule that lives only in prose drifts; the checks that
  enforce the mechanical rules are run by the auditor repository's hooks (`bnomis/auditor`,
  <https://bnomis.github.io/auditor/>).
- **Nothing here is about one project.** Rules, skills, fixtures and commit messages stay generic; a
  hook rejects any file or commit message that names a project from a list kept outside the
  repository.

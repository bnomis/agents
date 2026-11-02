# agents

![The agents logo](assets/agents-mark.svg){ align=right width="128" }

Shared [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) rules, skills and hooks,
and `auditme`, a static checker that projects pin as pre-commit hooks so the rules a script can check
are enforced on every commit, push and CI run.

```shell
git clone git@github.com:bnomis/agents.git ~/src/agents
~/src/agents/bin/install-claude.py
```

The installer links the contents of `claude/` into `~/.claude/`, so the rules load in every Claude
Code session and each skill becomes a slash command in every project. A project then opts in to the
checker with `/project-setup new` or `/project-setup adopt`, which pins the hooks in its
`.pre-commit-config.yaml`:

```yaml
- repo: git@github.com:bnomis/agents.git
  rev: <commit>
  hooks:
    - id: auditme-changed
    - id: auditme-all
      stages: [manual, pre-push]
```

## What is in the repository

| Path | What it is |
|---|---|
| `claude/rules/` | Rules loaded into every session: git, Python, reviews, security and the rest. See [Rules](reference/rules.md). |
| `claude/skills/` | Slash commands for specs, task lists, the `TODO.md` workflow, shipping, cleanup, audits and project setup. See [Skills](reference/skills.md). |
| `claude/skills/auditme/checks/` | The checker: a standard-library-only sweep over `src/` and `bin/`. See [The audit checker](guide/checker.md). |
| `claude/hooks/` | The Claude Code Stop hook that runs the checker before a turn ends. |
| `bin/` | The installer and the `no-project-names` check. See [Command line and hooks](reference/cli.md). |
| `.pre-commit-hooks.yaml` | The hooks other projects pin. |

## Where to start

1. Read [How it works](concepts.md) for the moving parts and why each is where it is.
2. Follow [Setting up](setup.md) for a new machine, a new project or an existing one.
3. Read [The audit checker](guide/checker.md) before the first hit appears: what it sweeps, how to
   read a hit and how to accept one.
4. Look things up in the reference: [Skills](reference/skills.md), [Rules](reference/rules.md) and
   [Command line and hooks](reference/cli.md).

## Why

- **A rule a script can check is a hook.** A rule that lives only in prose drifts; the checker turns
  each mechanical rule into a failing commit, so the drift never reaches an audit.
- **The commit sees your changes; the push sees everything.** The commit hook reports hits only in the
  files a commit changes, so nobody is blocked by someone else's old hit; the push gate and CI sweep the
  whole tree.
- **Projects choose when to upgrade.** Each project pins the checker to a commit of this repository, so
  a new rule fails a build only after `pre-commit autoupdate`.
- **Nothing here is about one project.** Rules, skills, fixtures and commit messages stay generic; a
  hook rejects any file or commit message that names a project from a list kept outside the
  repository.

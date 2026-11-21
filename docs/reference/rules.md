# Rules

A rule is a Markdown file of instructions that Claude Code loads into a
session's context. The shared rules live in `claude/rules/` and
`claude/rules/python/`.

## How rules reach a session

`bin/install-claude.sh` links `claude/rules/` into `~/.claude/rules/`: each
entry of `claude/rules/` becomes a symlink there, so `~/.claude/rules/python`
is a link to `claude/rules/python/`. See [Command line and hooks](cli.md#bininstall-claudesh)
for the installer.

Claude Code reads `~/.claude/rules/` as user-level rules for every project.
Nothing in `claude/CLAUDE.md` links to them; the rules directory alone is what
loads them. Rules cross-reference each other with relative links (for
example `[security.md](security.md)`).

- **Unscoped rules** (no frontmatter) load at the start of every session.
- **Path-scoped rules** start with `paths:` frontmatter listing file globs,
  and load only when Claude works with a matching file:

    ```markdown
    ---
    paths:
      - "**/*.md"
    ---
    ```

    `markdown.md` and every rule under `python/` are scoped this way. The
    Python rules match `**/*.py`; some add `**/pyproject.toml`, `**/uv.lock`,
    `**/requirements.txt` or `**/bin/*`.

A project's own rules do not go here. Per `rule-scope.md`, everything in
`claude/rules/` holds for any project; a rule for one project goes in that
project's `claude/rules/` (and its skills in `claude/skills/`), at the root of
its workspace, loaded from the workspace's `CLAUDE.md`.

## General rules

| File | Requires |
|---|---|
| `asking-questions.md` | Questions to the user go through the structured question tool, one decision per question, with clickable options and the recommendation first. |
| `bash-guidelines.md` | Non-interactive shell use: no pagers or editors, limit output with flags, judge multi-check commands by exit status, match processes by name, never `pkill -f`. |
| `counts-in-prose.md` | A number in prose is dropped, replaced by the command that produces it, or generated; dated measurements are exempt. |
| `design.md` | Per-input details (paths, column names, mappings) are required runtime config, never defaults; an inferred value needs positive evidence. |
| `environment.md` | Load environment variables with direnv from `.envrc`; do not edit `.envrc` unless told to. |
| `git-conventions.md` | Install pre-commit and pre-push hooks, make every script-checkable rule a hook, Conventional Commits, feature branches, no generated data in git, leave the user's own changes out of commits. |
| `identifiers-in-prose.md` | Decode every spec, review or task label (decision IDs, task numbers, hashes) in plain words wherever it appears in a message. |
| `locale.md` | British English spelling and grammar. |
| `markdown.md` | Plain ASCII punctuation in `.md` files, chat and commit messages: `-`, straight quotes, `...`. Scoped to `**/*.md`. |
| `reviews.md` | Anything the user must review is a review document in the repository plus an interactive page whose answers save as they are made. |
| `rule-scope.md` | Shared rules, skills and every other file in this repository (and any repository used across projects) name no project; project-specific rules go in the project's `claude/` directory. |
| `security.md` | No secrets in the repository or in output; never list environment variables; no raw PII in shipped logs; repeat the secrets rule in every subagent brief. |
| `tools-and-libraries.md` | Prefer dependencies already in the project or the stdlib; check a library's maintenance status before recommending it, and give alternatives when flagging one. |
| `user-guides.md` | User guides cover install, configure, run, examples and trade-offs, and are updated in the same commit as user-visible behaviour. |
| `verify-claims.md` | A statement about current state comes from a check run for it, timed with `date -u`; absence is claimed only after a search by likely name. |
| `versions.md` | Record every version that shapes an output, check it wherever saved work is reused, refuse a mismatch, pin what is checked. |

## Python rules

Every file here is path-scoped (see above).

| File | Requires |
|---|---|
| `python/argparse.md` | argparse only in unconverted code and standard-library-only scripts (every new CLI uses cappa), with a trailing comma in its calls so arguments format one per line. |
| `python/asserts.md` | No `assert` in product code; raise an exception. Tests may assert. |
| `python/environment.md` | Source `bin/activate.sh`, then run `bin/` scripts and `pytest` directly, without `uv run`. |
| `python/logging.md` | `ETA: ` log lines at `info` level, a format downstream tooling parses. |
| `python/testing.md` | Tests in `src/tests/` mirroring the source; never the full suite routinely; scope runs to changed modules and their importers; mark slow tests; bound hypothesis examples. |
| `python/tools-and-libraries.md` | The standard toolset: uv, loguru, cappa, ruff, pytest, hypothesis, aiohttp, mypy, Docker. |
| `python/utilities.md` | Utility scripts in `bin/`, dash-separated names, each with a bash wrapper that sources `bin/activate.sh`. |

## Rules from the auditor repository

The Python rules the auditme checker enforces - `coding-standards.md`,
`imports.md` and `dependencies.md` - live beside the checker in the auditor
repository (`bnomis/auditor`), whose installer links them into
`~/.claude/rules/auditme/`. Its
[Rules](https://bnomis.github.io/auditor/reference/rules/) page lists them,
and maps each shared rule a hook or checker rule enforces to that check,
including `rule-scope.md`, `git-conventions.md` and `python/asserts.md` from
here. No hook or checker rule checks any rule it does not list.

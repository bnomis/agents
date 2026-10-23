# Git conventions

## pre-commit

Install hooks after cloning so linting/formatting runs on each commit:

```shell
pre-commit install
```

If a hook fails, fix the underlying issue. Do not use `--no-verify`.

## Branching

Use feature branches (`feat/short-description`) unless told to use worktrees.
Rebase onto main before opening a PR.

## Commits

### Format

```text
<type>(<scope>)?: <description>

[optional body]

[optional footer(s)]
```

Scope is optional. Use `!` after the type (or a `BREAKING CHANGE:` footer)
for breaking changes: `feat(api)!: drop /v1 endpoints`.

### Types

- `feat` - new feature
- `fix` - bug fix
- `docs` - documentation only
- `refactor` - neither fixes a bug nor adds a feature
- `perf` - performance improvement
- `test` - adding or correcting tests
- `build` - build system or dependencies
- `ci` - CI/CD changes
- `chore` - tooling that doesn't fit above
- `revert` - reverts a prior commit

### Subject line

- 50 characters or fewer (including the `type(scope):` prefix).
- Lowercase first word, no trailing period.
- Imperative mood: "If applied, this commit will __."
- Be specific. Avoid "fix bug", "update code", "this commit...".

Good:

```text
add user authentication
fix null pointer in cart service
remove deprecated API endpoint
```

Bad:

```text
added user authentication          # past tense
fix bug                            # vague
user authentication added          # descriptive, not imperative
```

### Body

Use when the change isn't self-evident from the diff: non-obvious
rationale, breaking changes, issue references. Wrap at 72 characters.
Explain *why*, not *what*.

A consequence someone must act on later (refit, migrate, re-run, a missing
guard) does not live only in a commit body, which is read once. If the code
does not already guard it, file it in the project's `TODO.md` (`/todo-add`)
before committing, and ask whether the same hazard applies beyond this
change.

### Granularity

One logical change per commit. Don't bundle refactors with feature work.
Avoid `WIP` commits on branches that will be reviewed.

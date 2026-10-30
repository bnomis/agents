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

## Data files stay out of git

Never commit generated data: result JSON, model outputs, samples, datasets.
They live in a data directory outside the repository; only small
human-readable records made from them (a report, a review) are committed.

- A spec or task list that writes output names where it goes. Point that
  output outside the repository, and ignore the data's extension in the
  directory where its records live, so a slip fails at `git add`.
- Before a commit, `git diff --cached --stat` and check any file over 1 MB:
  if it is data, move it out. Git hosts refuse files over their size limit
  at push, after the file is already in history, and removing it then means
  rewriting every unpushed commit that holds it.

## The user's own changes

Leave uncommitted changes you did not make out of your commits. Mention one
once, when you first notice it, and never again: not in status summaries,
commit reports or "next step" messages. The user knows about their own working
tree, and repeating it is noise.

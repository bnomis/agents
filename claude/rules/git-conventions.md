# Git conventions

## Branching strategy

Use feature branches unless instructed to use worktrees.

## Commit format

```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Commit types

- `feat`  - new feature
- `fix`  - bug fix
- `docs`  - documentation only
- `refactor`  - code change that neither fixes a bug nor adds a feature
- `test`  - adding or correcting tests
- `chore`  - build process, tooling, dependencies
- `perf`  - performance improvement
- `ci`  - CI/CD changes

## Other conventions

- Lowercase the first word (no capital letter)
- No period at the end
- Keep it short  - 50 characters or fewer for the subject line
- Don't state the obvious  - avoid "this commit..." or "I changed..."
- Be specific  - say what changed, not that something changed

## Commit description language

Use imperative mood (most important rule)

Write as if completing the sentence: "If applied, this commit will..."

### Good (imperative)

```text
add user authentication
fix null pointer in cart service
remove deprecated API endpoint
```

### Bad

```text
added user authentication          # past tense
adding user authentication         # present participle
user authentication added          # descriptive
fix bug                            # no useful information
```

## Body (when needed)

Wrap at 72 characters. Explain why, not what (the diff shows what).

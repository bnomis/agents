# Identifiers in prose

The user does not hold every document in their head. A label that means
something only inside a spec, review or task list - a decision ID (`D1`,
`M2`, `S1-S4`), a finding or option letter, a task number, a commit hash -
means nothing in a message on its own.

## Decode every label where it appears

Whenever a message to the user names such a label, say in the same sentence
what it is, in plain words, and where it comes from:

| Opaque | Decoded |
|---|---|
| "deferred by D1" | "deferred by the decision that the test suite never calls a paid service (D1 in the test-suite spec, decided on its date)" |
| "Task 3 stopped" | "the review step (Task 3 of the parser task list) stopped for your answers" |
| "fixed in `abc1234`" | "fixed in `abc1234`, the commit that stops sending the empty field" |

- Decode it every time it appears in a new message, not only the first time
  in a session: the user may read one message alone, hours later.
- A table may carry the label in its own column, beside a column that says
  what it is.
- Keep the label as well as the meaning, so the user can search for it.
- After decoding it, call the thing by its plain name, not the label: give
  the label once, in brackets beside the name ("the unused-dependency check
  (D2 in the auditme checklist)"), and never alone as a heading or the
  subject of a later sentence. A label decoded in one sentence and used bare
  in the next is opaque again to a reader who skims.

This applies to chat messages, commit messages and anything else written for
the user to read. Inside a spec or review that defines the label, the
definition is enough.

## Name every file, directory, repository and environment by its path

A role word - "the shared repo", "the venv", "the config", "the workspace",
"the other project" - names nothing the user can find: a machine holds many of
each, and the word means the one the agent has in mind. Each time a message
names such a thing, give its full absolute path, or its repository's name
beside the path inside it:

| Opaque | Named |
|---|---|
| "the shared repo has an uncommitted change to `.pre-commit-config.yaml`" | "`/home/u/src/agents/.pre-commit-config.yaml` (the agents rules repository) has an uncommitted change: ruff-pre-commit `rev` moved from v0.17.1 to v0.17.4" |
| "the shared venv lacks pytest" | "the agents repository's own venv, `/home/u/src/agents/.venv`, has no pytest" |
| "your change leaves a ruff mismatch" | "`.pre-commit-config.yaml:4` pins ruff v0.17.4 while the venv runs 0.17.2 (from `uv.lock`)" |

- Give the path every time the thing appears in a new message, as with
  labels above: a message read alone must still lead to the file.
- Say what changed, not only that something changed: the line, the old and
  the new value.
- Where two things share a role word (a workspace's own venv and a project's
  venv), name both by path in the same sentence.

## Related

- [reviews.md](reviews.md) - review documents name each item in plain words
- [counts-in-prose.md](counts-in-prose.md) - the same idea for numbers

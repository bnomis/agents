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

This applies to chat messages, commit messages and anything else written for
the user to read. Inside a spec or review that defines the label, the
definition is enough.

## Related

- [reviews.md](reviews.md) - review documents name each item in plain words
- [counts-in-prose.md](counts-in-prose.md) - the same idea for numbers

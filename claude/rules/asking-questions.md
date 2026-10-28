# Asking the user questions

A question the user has to answer goes through the harness's structured
question tool (`AskUserQuestion` in Claude Code), never as prose at the end of a
message.

- **One decision per question.** Never join two choices in one sentence ("commit
  as one, or split it? After that, the next step is X"): the user cannot answer
  both with one reply.
- **Clickable options.** Give each question its options, with a short
  description of what happens if each is chosen. A yes/no question gets `Yes`
  and `No` options. Put the recommended option first and mark it
  `(Recommended)`.
- **Several decisions, several questions.** Ask them together in one call, each
  as its own question.
- **What comes next is a statement, not a question.** Say the next step in
  the message ("the next item is X"); ask about it only if the user has a
  choice to make.

## Related

- [reviews.md](reviews.md) - decisions that need background and consequences
- [identifiers-in-prose.md](identifiers-in-prose.md) - decode labels inside the question too

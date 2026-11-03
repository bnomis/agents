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
- **One request at a time.** A message asks the user for one thing: a question,
  or a task such as reviewing a page or answering decisions on it. Never add a
  second ("answer the page; and shall I commit?"). Wait for the reply, then
  ask the next. Two requests in one message make the user hold one open while
  answering the other.
- **Several decisions, several questions.** Decisions on the same step can be
  asked together in one call, each as its own question.
- **What comes next is a statement, not a question.** Say the next step in
  the message ("the next item is X"); ask about it only if the user has a
  choice to make.
- **Never say you will do something and then do nothing.** A message that
  says "next, I'll do X" is followed by doing X in the same turn, then
  reporting it. If X waits on the user, ask for it instead of announcing it.
  Ending a turn on "I'll do X" leaves the user to notice that X never ran and
  ask for it.
- **Say why a prerequisite is needed.** When work needs something from the
  user - a credential, a login, a network connection, an installed tool, a
  file - say in the same sentence what the work uses it for, and why nothing
  they already have would do: "the sync needs a token because GitHub's
  GraphQL API refuses requests without one, even for public data", not "it
  needs a token". Check the reason in the code or the service's documentation
  first, not from memory. A bare "needs X" reads as an arbitrary demand, and
  the user has to ask why before they can judge whether to provide it.

## Related

- [reviews.md](reviews.md) - decisions that need background and consequences
- [identifiers-in-prose.md](identifiers-in-prose.md) - decode labels inside the question too

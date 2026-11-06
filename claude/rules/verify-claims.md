# Check a claim before stating it

A statement to the user about the present - a repository's status, whether a
file exists, what a commit holds, whether a feature is missing, what a change
breaks downstream - comes from a check made for it, not from memory. Each
rule below was broken more than once, and each time the user acted on, or had
to correct, a claim that a command would have disproved in seconds.

## State someone else can change

The user and other sessions work alongside the agent: they commit, push,
merge, edit and delete while a session runs.

- Just before stating the state of a repository, file, branch or running
  process, run the command that shows it (`git status -sb`, `git log`,
  `ls`), and report what it printed.
- Note the time of every such check: run `date -u +%H:%M:%S` in the same
  command. If more than a minute has passed since the last check, check
  again before stating the state, and give the time with the claim: "as of
  14:05 UTC, `main` matches `origin/main`". A state without a time cannot be
  told apart from one remembered from hours earlier.
- A recap is a statement. The closing report of a ship, merge or queue run
  re-checks every repository it mentions (`git fetch`, then
  `git branch -a --contains <hash>` or `git status -sb`) in the same turn.
- An offer or question is a statement too: "X is still stopped; shall I
  restart it?" claims X's state. Check the process or repository in the same
  turn before offering to act on it, however recently it was last seen.
- A status from earlier in the session, a context summary or another session
  is a lead, not a fact. Check it in the repository that actually holds the
  file (`git rev-parse --show-toplevel`); if it cannot be checked, say when it
  was observed, and never base a design choice on it.
- That includes your own pending work. "X is still uncommitted" or "X waits
  for Y" about something you left open turns ago claims the present state of
  both X and Y; the user may have done X or fixed Y since. Check both before
  saying either, in the same turn.
- A queue or agent log records what was tried, not what was committed.
  Confirm a defect seen in a log in the committed state (`git show <commit>`
  or the file) before reporting it.

## Absence

- Before saying a capability does not exist, search by the likely function
  name, not a substring (`link_latest`, not `latest`), and search the
  project's sibling libraries as well as the project itself.
- Unless the search was exhaustive, say "I did not find X" and how you
  looked, not "X does not exist".

## Impact on another project

- When a finding's impact depends on a consumer in a sibling project, read
  the consumer's code and, where cheap, run it on the case in question before
  describing the impact.
- Never present "could matter, unchecked" as a conclusion: check it, or say
  it is the next step and do it.
- That holds for a finding a subagent reports outside its brief: check it
  before relaying it, then file it or drop it. Passing it on marked "not
  checked" leaves the check to the user.
- Before filing a gap in another project, find out how that project is
  actually used. A file for local development (a compose file, a dev
  script) is not its deployment, and a one-line remark in another
  project's document is a lead, not evidence. If the repository does not
  say how it is used, ask before filing; never file the gap with a
  "suspected" cause instead.

## Related

- [reviews.md](reviews.md) - how findings reach the user

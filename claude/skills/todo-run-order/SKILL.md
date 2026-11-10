---
name: todo-run-order
description: Turn chosen TODO.md items into a run order - re-check each item, write the specs it needs (one review for all of them), a task list per spec, and the order file that /rro runs
when_to_use: |
    Use this skill whenever the user mentions:
        - make a run order from the todo items
        - make an order from the todo items
        - specs and task lists for todo items 1-3
        - plan these todo items as a run order
        - todo run order

allowed_tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, Skill, Artifact, ArtifactData]
---

# TODO run order

Invoke as:
    /todo-run-order <items> [run order name]

Where:

- `<items>` picks `TODO.md` items by their position in the file, counting
  `##` headings from 1: a comma-separated list of numbers and ranges, such
  as `1-3,5,8`. The positions are the `#` column of the table the
  [todo-review](../todo-review/SKILL.md) skill shows.
- `[run order name]` names the run order; without one, name it from the items'
  subjects in three or four words. Its slug (the
  [specdev](../specdev/SKILL.md) slugification) names the files below.

Takes the chosen items from `TODO.md` to an order file that `/rro` (the
run-order command) can run unattended: the specs the items need, one review
of those specs, a task list per spec, and the order file itself. It runs
nothing: starting the order is the operator's call. Follow
[conventions.md](../todo-review/conventions.md) for `TODO.md`, and the
project's own rules on specs, task lists, tests and commits.

Every step stays in the current repository. `/rro` runs one repository's
lists, so work an item needs in another repository is a prerequisite,
named in the order file, never a row in it.

## 1. Start

1. Check, from the main checkout (not a worktree): on the default branch,
   a clean tree, level with its remote (`git status -sb`), since `/rro`
   refuses anything else and the order's commits go on that branch. If not,
   say which and stop.
2. Read the project's `AGENTS.md` (and its `TODO.md` section if any),
   `TODO.md` in full, `agents/specs/index.md`, `agents/tasks/index.md`, and
   the newest existing order file (`agents/tasks/order-*.md`), if any.
3. Parse `<items>`. A position outside the file, or a malformed list, is an
   error: say which and stop. Save the starting text,
   `git show HEAD:TODO.md > <scratchpad>/todo-before.md`.
4. Show the chosen items as the todo-review table
   ([Showing the list](../todo-review/SKILL.md#showing-the-list)), headed
   with the order's name.

## 2. Re-check each item

For each item, as [todo-do](../todo-do/SKILL.md) step 1 does: is it still
open and still true, is it one symptom of a cause another item shares, and
does a spec or task list for it already exist (its `Spec: ...; tasks: ...`
line, the indexes, a task list whose `**Status:**` headers are not all
`done`). For more than a couple of items, hand the checks to one Explore
agent per item, in parallel, and keep their conclusions.

- A done or stale item, or one that shares a cause with an item left out
  of the selection: report it with the evidence, propose the move, the
  correction or the wider selection, and stop.
- An item with an unfinished task list: that list is its row; write no new
  spec or list for it.

## 3. Plan the specs and lists

Size each item as todo-do step 2 does, then decide what it becomes:

- **Small:** one task list with the item as its source (taskdev's non-spec
  input, `**Source:** TODO.md, "<item heading>"`), no spec.
- **Large:** a spec, new or an amendment of the spec the item names, then
  its task list. One item may need several specs, one per cohesive feature
  (for example one per language or per component, where each can be built
  and merged alone); several items may share one spec where the work is one
  change. Each spec covers this repository only.

For each list, note:

- what it waits for: a list whose merged code or data it needs (a
  dependency between items, or a shared file two lists would both edit);
- each stop that waits for the operator whatever `/rro` decides: those the
  project's rules reserve (the `always wait for` files of the newest order,
  or the project's queue-stop rule), and work only a person can do
  (placing data the project may not download itself, labelling, spending
  money);
- each prerequisite outside this repository, with how to check it is in
  place.

Show the plan as a table (item, spec or list, new or amended, waits for,
stops for the operator) before writing anything, as a statement, not a
question: the specs' review in step 4 is where the operator answers.

## 4. Write the specs, then one review

1. Write each spec with `/specdev` through the Skill tool, carrying each
   item's dated findings into the spec's motivation. Independent specs may
   be written by parallel subagents, one spec each; every brief names the
   item, the spec path, this skill's planning notes for it, and repeats the
   shared security rule on environment variables word for word. Read every
   spec a subagent returns before going on.
2. Write one review document for all of them,
   `agents/reviews/order-<slug>-specs.md`, in the shape the shared
   `reviews.md` rule gives: each spec as an item to approve or flag, with
   what it changes and why, and each decision the specs leave open. Filter
   the decisions as that rule says, so only real choices reach the
   operator. Name every prerequisite the operator must provide before the
   order runs (data to place, accounts, another repository's change), each
   with what the work uses it for and why nothing already present will do.
3. Publish its page, put its URL in the header, hand it over, and stop
   until every item and decision has an answer.
4. When the operator says it is answered, read the answers from the page's
   database, copy them into the Answers section with the date, apply them
   to the specs (amend their version and record the decision), and commit
   the specs and the review together after asking.

## 5. Write the task lists

Write each list with `/taskdev` through the Skill tool, in the order the
lists will run. On top of what taskdev requires, every list in an order
has:

- **a last task that saves its final test output** at the order's
  `test log` path, relative to the main checkout, since `/rro`'s merge gate
  reads that file and does not rerun the tests. From a worktree, the main
  checkout is the first entry of `git worktree list --porcelain`; pipe the
  last task's full test run through
  `tee "<main checkout>/<test log path>"`, with `{spec}` and `{index}`
  filled in, and create its directory first;
- **its operator stops named** as the task that stops and what it waits
  for, so the order's `Stops for you` cell can quote it;
- **a version bump, if any, made against the default branch at its last
  task**, not at its first, so lists that each bump the version can merge
  in any order the table allows.

Add the `Spec: <spec path>; tasks: <task list path>.` line to each item in
`TODO.md` in the same commit as its task list (taskdev's rule on the
baseline for `verify_bodies.py`). Put it at the end of the item's body,
after any notes and `###` findings: `verify_bodies.py` accepts text added
after a body but reports one changed in its middle as altered.

## 6. Write the order file

Write `agents/tasks/order-<slug>.md` in the format `/rro` documents (its
`docs/run-order.md`):

1. **An introduction:** the date, the items it covers by heading, the
   command that runs it (`/rro agents/tasks/order-<slug>.md`), the specs'
   review it follows, and every prerequisite with where it goes. Say which
   rows stop for the operator, and that providing their data before the
   start lets those rows run straight through.
2. **The settings table.** Take each setting from the newest order file in
   the repository, then from the project's rules (its test and queue-stop
   rules name the checkpoint command, the pass line and the files that
   always wait). Ask the operator only for a required setting none of them
   gives (`checkpoint command`, `test pass line`), one question each.
   Leave `progress page` empty: `/rro` fills it in.
3. **The rows**, in run order: a list's `Waits for` rows before it, then
   the `TODO.md` order. A list that waits for the operator goes after lists
   that do not, unless something waits for it. `Stops for you` names each
   reserved stop with its task number, `-` for none; `Status` is `todo`.
   Add checkpoint rows only where the project's rules ask for them at a
   fixed place; `/rro` otherwise inserts one every `checkpoint every` lists
   and at the end, skipping one that would leave fewer than `checkpoint
   every` lists before the end.

Check it with `/rro`'s own parser (its `next` subcommand on the order
file), through the parser's wrapper script where it has one, since the bare
script may need that tool's own environment: it must print a step that runs
row 1, not an error. Where the parser is not installed, say the file was
not checked.

## 7. Finish

1. Run `python3 ~/.claude/skills/todo-review/verify_bodies.py
   <scratchpad>/todo-before.md TODO.md DONE.md`; it must exit 0 (the
   `Spec: ...; tasks: ...` lines are the only change to item bodies).
2. Run the project's commit checks, then ask whether to commit the task
   lists, the indexes, `TODO.md` and the order file
   (`docs(tasks): add the <run order name> run order`). Do not push unless asked.
3. Report: the table of rows (list, what it waits for, its operator stops),
   the prerequisites still to provide, and the command that starts the
   order. Starting it is the operator's request, not a question here.

## Do not

- Write a row, task or spec for work in another repository.
- Start the order, or any queue, from this skill.
- Write a task list before the specs' review is answered: the answers
  change the specs the lists are built from.
- Move an item to `DONE.md`: its list's last task does that when the work
  has shipped.

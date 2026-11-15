---
name: todo-review
description: Review a project's TODO.md - check each item is still open and still true, file outstanding work that specs, task lists or code promise but no item records, consolidate items that share a root cause, and put the file in implementation order
when_to_use: |
    Use this skill whenever the user mentions:
        - review the todo list
        - todo review
        - reorder TODO.md
        - consolidate the todo items
        - what should we do next (when TODO.md looks disordered or long)

allowed_tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent]
---

# TODO review

Invoke as:
    /todo-review

Reviews `TODO.md` in the current repository as a whole: drops nothing,
moves what is finished, files outstanding work that no item records,
consolidates what shares a cause, and orders the rest. Follow
[conventions.md](conventions.md); a project's own `TODO.md` section in
`AGENTS.md` or `CLAUDE.md` wins where it differs.

## Gather context

1. Read the project's `AGENTS.md` / `CLAUDE.md` section on `TODO.md`, if any.
2. Read `TODO.md` in full, and the last few entries of `DONE.md`.
3. Save the starting text: `git show HEAD:TODO.md > <scratchpad>/todo-before.md`.
   If `TODO.md` has uncommitted changes, ask whether to commit them first.

## Workflow

1. **Check each item is still open and still true.** For each item, look for
   the work having landed - the code it names, a `Done:` line in `DONE.md`,
   a task list whose `**Status:**` headers say done (checkboxes are records,
   not status). Look also for a premise gone stale: a discrepancy a later
   repair cleared, a file since renamed. For more than a handful of items,
   hand the checks to an Explore agent and keep its conclusions only.
   Classify each item: **open**, **done**, **partly done**, or **stale**.
2. **Look for outstanding work that no item records.** `TODO.md` is meant to
   hold all open work, but plans made elsewhere often promise later work that
   never reaches it. Search the project's own records for such promises:
   - specs: a spec still `proposed` with no task list; work a spec calls
     planned, deferred, a follow-up or a later spec (a planned-specs table,
     an "out of scope, filed later"), checked against what exists;
   - task lists: a closing step deferred to a later list ("the list that
     completes X sets ..."), and tasks left `blocked`;
   - reviews: decisions or answers whose follow-up nothing has started;
   - code and tests: known-bug and expected-failure markers, and `TODO` or
     `FIXME` comments, that name no `TODO.md` heading;
   - commit bodies since the last review that name a consequence to act on
     later (refit, migrate, rerun, a missing guard).
   A promise counts as recorded only if an open `TODO.md` item, or an
   unfinished task in an existing task list, covers it. Before calling it
   missing, check the work has not already been done (the file it would
   create exists, the status has moved). Unless the search was exhaustive,
   report "I did not find an item for X" and say where you looked. For more
   than a few records, hand the search to an Explore agent and keep its
   conclusions only.
3. **Group by root cause**, using the tests in
   [conventions.md: Consolidation](conventions.md#consolidation). Read the
   items against each other, not one at a time: the question is whether two
   items are one piece of work, and whether one item's fix removes the
   reason another rejected an alternative.
4. **Order** the open items and groups by
   [conventions.md: Order](conventions.md#order).
5. **Propose before rewriting.** Present to the operator, briefly:
   - items to move to `DONE.md`, each with the evidence it is done;
   - stale items, with what is stale and the proposed correction;
   - missing items, each with the record that promises the work and a
     proposed title and place in the order;
   - each proposed group, with the shared cause in one sentence and the
     findings it absorbs;
   - the proposed order, as the table in
     [Showing the list](#showing-the-list).
   Ask the operator to confirm or adjust. Do not rewrite until they do.
6. **Rewrite**, as confirmed:
   - move done items to the end of `DONE.md`, body unchanged, each followed
     by a `Done:` line naming the spec, task list or commit that closed it;
   - build each consolidated item: cause, Fix direction, then each original
     finding verbatim under `###`;
   - write each confirmed missing item in the shape conventions.md gives,
     its finding dated today and naming the record that promised the work;
   - correct stale premises by adding a dated note, never by rewriting the
     dated finding;
   - fix only cross-references that now point at the wrong place, and any
     bare count in prose you wrote.
   Build the new file from slices of the old one rather than retyping
   bodies.
7. **Verify nothing was lost:**

   ```shell
   python3 ~/.claude/skills/todo-review/verify_bodies.py <scratchpad>/todo-before.md TODO.md DONE.md
   ```

   It must exit 0. If a body is reported lost or altered, restore it - an
   intended change (a fixed cross-reference) is the only exception, and say
   which one it was.
8. **Run the project's checks** on `TODO.md` and `DONE.md` (pre-commit hooks,
   any count checker).
9. **Report**: the closing message always carries the table, read from the
   file as it now stands, even when the operator chose to leave the file
   unchanged; a table shown only in the step 5 proposal does not count. Give
   the new order as the table in
   [Showing the list](#showing-the-list), what moved to `DONE.md`, what was
   merged into what, which missing items were added, and anything stale. Ask
   whether to commit (`docs(todo): ...`). If a group's fix will change a
   spec or an artefact shape, say that the next step is `/todo-do`, which
   starts a spec for it. Whenever the review changes `TODO.md` again, or
   commits it in a later turn, show the list again
   ([conventions.md: Show the list after every change](conventions.md#show-the-list-after-every-change)).

## Showing the list

Whenever this skill shows the operator the list - the proposed order in step
5, the new order in step 9, or the list on its own when asked - show it as a
laid-out table, never as the raw `TODO.md` text. The operator reads the
table to decide what to do next; the file is there for the detail.

Head it with the file's full absolute path and the commit it reflects (or
"uncommitted"). Then one row per item, in the file's order:

| # | Item | Kind | Found | Next step | Size |
|---|---|---|---|---|---|
| 1 | <the item's title, shortened only if very long> | <defect, blocker, waste, feature, audit, deferred> | <date found; and the date of any later note> | <the command or action that moves it on: `/todo-do`, a spec, a task list, a run> | <small, or large and why> |

In step 5, add a **Change** column saying what the review does to each row
(kept, moved up or down, merged, corrected, new), and list the items leaving
for `DONE.md` beneath the table.

Where an item carries a list of its own - the findings of a consolidated
item, the packages or files it covers, the measurements it records - show
that list as a second, smaller table under the main one, headed with the
item's number and title. Keep each dated figure with its date, as the item
records it.

Follow the tables with a sentence or two on anything the table cannot say:
what the first item needs before it can start, or that the list is short
because nothing else is open.

## Do not

- Delete an item, or shorten a dated finding to make a group read better.
- Reorder by precedence alone without first looking for shared causes.
- Mark an item done because a spec or task list exists for it.
- File a missing item from memory of the session: name the record that promises
  the work, and check it is still outstanding.
- Touch the operator's own notes files.

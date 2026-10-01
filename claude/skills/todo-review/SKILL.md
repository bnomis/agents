---
name: todo-review
description: Review a project's TODO.md - check each item is still open and still true, consolidate items that share a root cause, and put the file in implementation order
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
moves what is finished, consolidates what shares a cause, and orders the
rest. Follow [conventions.md](conventions.md); a project's own `TODO.md`
section in `AGENTS.md` or `CLAUDE.md` wins where it differs.

## Gather context

1. Read the project's `AGENTS.md` / `CLAUDE.md` section on `TODO.md`, if any.
2. Read `TODO.md` in full, and the last few entries of `DONE.md`.
3. Read `agents/lessons.md` (or the project's equivalent), if present.
4. Save the starting text: `git show HEAD:TODO.md > <scratchpad>/todo-before.md`.
   If `TODO.md` has uncommitted changes, ask whether to commit them first.

## Workflow

1. **Check each item is still open and still true.** For each item, look for
   the work having landed - the code it names, a `Done:` line in `DONE.md`,
   a task list whose `**Status:**` headers say done (checkboxes are records,
   not status). Look also for a premise gone stale: a discrepancy a later
   repair cleared, a file since renamed. For more than a handful of items,
   hand the checks to an Explore agent and keep its conclusions only.
   Classify each item: **open**, **done**, **partly done**, or **stale**.
2. **Group by root cause**, using the tests in
   [conventions.md: Consolidation](conventions.md#consolidation). Read the
   items against each other, not one at a time: the question is whether two
   items are one piece of work, and whether one item's fix removes the
   reason another rejected an alternative.
3. **Order** the open items and groups by
   [conventions.md: Order](conventions.md#order).
4. **Propose before rewriting.** Present to the operator, briefly:
   - items to move to `DONE.md`, each with the evidence it is done;
   - stale items, with what is stale and the proposed correction;
   - each proposed group, with the shared cause in one sentence and the
     findings it absorbs;
   - the proposed order, as a table.
   Ask the operator to confirm or adjust. Do not rewrite until they do.
5. **Rewrite**, as confirmed:
   - move done items to the end of `DONE.md`, body unchanged, each followed
     by a `Done:` line naming the spec, task list or commit that closed it;
   - build each consolidated item: cause, Fix direction, then each original
     finding verbatim under `###`;
   - correct stale premises by adding a dated note, never by rewriting the
     dated finding;
   - fix only cross-references that now point at the wrong place, and any
     bare count in prose you wrote.
   Build the new file from slices of the old one rather than retyping
   bodies.
6. **Verify nothing was lost:**

   ```shell
   python3 ~/.claude/skills/todo-review/verify_bodies.py <scratchpad>/todo-before.md TODO.md DONE.md
   ```

   It must exit 0. If a body is reported lost or altered, restore it - an
   intended change (a fixed cross-reference) is the only exception, and say
   which one it was.
7. **Run the project's checks** on `TODO.md` and `DONE.md` (pre-commit hooks,
   any count checker).
8. **Report**: the new order as a table, what moved to `DONE.md`, what was
   merged into what, and anything stale. Ask whether to commit
   (`docs(todo): ...`). If a group's fix will change a spec or an artefact
   shape, say that the next step is `/todo-do`, which starts a spec for it.

## Do not

- Delete an item, or shorten a dated finding to make a group read better.
- Reorder by precedence alone without first looking for shared causes.
- Mark an item done because a spec or task list exists for it.
- Touch the operator's own notes files.

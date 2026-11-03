---
name: todo-add
description: Add a finding to a project's TODO.md - verified, dated, merged into an existing item when it shares a root cause, and inserted where it belongs in implementation order
when_to_use: |
    Use this skill whenever the user mentions:
        - add this to the todo list
        - add a todo
        - file this in TODO.md
        - record this bug for later

allowed_tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# TODO add

Invoke as:
    /todo-add <description>

With no description, file the finding the conversation has just
established, and say which one.

Adds one finding to `TODO.md` the way an item is meant to read: what was
observed, when, the cause, and a fix direction - placed by the whole file,
not appended. Follow
[conventions.md](../todo-review/conventions.md); a project's own `TODO.md`
section in `AGENTS.md` or `CLAUDE.md` wins where it differs.

## Workflow

1. **Read** the project's `TODO.md` convention section, `TODO.md` in full,
   and the last few entries of `DONE.md`. If `TODO.md` has uncommitted
   changes, ask whether to commit them first.
2. **Establish the finding.** An item is a record, so it needs evidence, not
   a paraphrase:
   - what was observed, where, and on what date;
   - the identifiers a reader can chase (a file, a row, a DOI, a run, a
     commit);
   - the cause, with `path:line` or function names, confirmed by reading the
     code - mark it "suspected" if it is not confirmed;
   - a fix direction, and whether it must go through a spec first.
   If the description is a one-liner and the cause is not known, find it,
   or say plainly in the item that it is unconfirmed. Do not invent a
   measurement.
3. **Check it is not already filed or done.** Search `TODO.md` and
   `DONE.md` for the same symptom, file and function. If it is done, say so
   and stop. If it is filed, add only what is new to that item.
4. **Look for a shared root cause** with every open item, using
   [conventions.md: Consolidation](../todo-review/conventions.md#consolidation).
   Then decide:
   - **New item**: no shared cause.
   - **Join an item**: it shares a cause with one item. Add it as a `###`
     finding under that item, and widen that item's Fix direction to cover
     it.
   - **Consolidate**: it shares a cause with two or more items, or changes
     how existing items should be grouped. Propose the consolidation to the
     operator and, once they agree, apply it as
     [`/todo-review`](../todo-review/SKILL.md) would, including its
     mechanical check that every original body survives.
   - **Reverses a reason**: it removes the reason another item, or a spec,
     rejected an alternative. Say so in both places.
5. **Place it** by [conventions.md: Order](../todo-review/conventions.md#order),
   re-reading its neighbours. A new bug that loses work goes at the top.
   If placing it changes why the items around it are in their order, say so.
6. **Write it** in the shape conventions.md gives: a specific `##` title,
   the dated finding inside the project's accept markers, the cause, the
   Fix direction. One blank line after every heading.
7. **Run the project's checks** on `TODO.md`.
8. **Report** where it went and why there: new, joined, or consolidated,
   and the neighbours it sits between, then show the updated list
   ([conventions.md: Show the list after every change](../todo-review/conventions.md#show-the-list-after-every-change)).
   Ask whether to commit (`docs(todo): ...`).

## Do not

- Append to the end of the file because it is easiest.
- Add a second item for a cause an existing item already names.
- Write an undated number, or a cause stated as fact that was not checked.
- File anything in `DONE.md`.
- File a fix that lies in another repository only in the repository that
  found it. File it where the fix is made, creating that repository's
  `TODO.md` if it has none, and point the finding repository's item at it.
  "It has no `TODO.md`" is never a reason to scatter one fix across its
  consumers.

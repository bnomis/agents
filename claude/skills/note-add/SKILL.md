---
name: note-add
description: Add a dated, free-form note to a project's NOTES.md - clarified with the user until it stands on its own, previewed, then appended
when_to_use: |
    Use this skill whenever the user mentions:
        - add a note
        - note this down
        - put this in NOTES.md
        - remember this idea for later (in the project, not in Claude's memory)

allowed_tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Note add

Invoke as:
    /note-add <the note>

With no argument, ask what the note should say.

Adds one note to the project's `NOTES.md`: an idea, a reminder, a decision
deferred, a link worth keeping. It is the loose sibling of
[`/todo-add`](../todo-add/SKILL.md). A note needs no evidence, cause or fix
direction, and its place in the file does not matter. It does need to make
sense to someone reading it months later with none of today's context, and
that is the one thing this skill insists on.

## Workflow

1. **Read** `NOTES.md` in the repository root, in full. If it does not exist,
   say so and offer to create it with a `# <Project> notes` title. If it has
   uncommitted changes, ask whether to commit them first.
2. **Check for an existing note** on the same subject. If one exists, offer
   to add to it (a dated line at its end) rather than starting a second.
3. **Find what a later reader would be missing.** Read the note as someone
   who was not in this conversation would. Typical gaps:
   - **What** it is about: a project-only label, an abbreviation, a
     decision ID, a task number or a commit hash with no plain-words meaning;
   - **Why** it matters, when the note does not say;
   - **Where**: the file, URL, paper, dataset or command it refers to;
   - **When**: a relative date ("next week", "after the run") that needs an
     absolute one;
   - **Who**: a person named only by pronoun or first name, when it matters.
   Fill what you can from the conversation and the repository yourself.
   Search for a referenced file, spec or commit rather than asking where it
   is. Never invent a fact.
4. **Ask only about the rest**, with `AskUserQuestion`, plainly and briefly:
   one question per gap, each with concrete options where there are any
   ("the 2026-10-29 big-five run", "the next audit cycle") so the user can
   click rather than type. Skip this step entirely when the note already
   stands on its own. Do not turn a note into an interview: two or three
   questions at most, and accept "leave it as is".
5. **Draft** the note in the file's existing style:

   ```markdown
   ## <short title saying what the note is about>

   Added YYYY-MM-DD. <the note, in the user's words where possible, with the
   clarifications worked in>
   ```

   - Keep the user's wording and voice. Clarify, do not rewrite.
   - Exactly one blank line after the heading.
   - Follow the project's markdown and spelling rules (plain ASCII
     punctuation, the project's locale).
   - A number in the note follows the project's counts-in-prose rule. Date
     a measurement, or wrap it in the project's accept markers if a count
     checker reads `NOTES.md`.
6. **Preview** the exact markdown in a code block, then ask with
   `AskUserQuestion`: `Add it (Recommended)`, `Change it` (then ask what to
   change and preview again), or `Cancel`.
7. **Append** the note at the end of `NOTES.md`, separated from the previous
   note by one blank line. Insert it elsewhere only if the file says it is
   ordered or grouped.
8. **Run the project's checks** on `NOTES.md` (its pre-commit hooks, any
   count checker) and fix anything they flag in the new note.
9. **Report** where the note went, and ask whether to commit it
   (`docs(notes): <subject>`).

## Do not

- File open work here. A bug or a task with a cause belongs in `TODO.md`:
  if the note describes one, say so and offer `/todo-add` instead.
- Edit, reorder or tidy the other notes in the file. They are the user's.
- Save the note to Claude's own memory instead of, or as well as, the file.
- Ask a question the repository or the conversation already answers.

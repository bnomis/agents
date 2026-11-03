---
name: todo-do
description: Do the first item in a project's TODO.md - re-check it is still open and not part of a larger cause, fix it directly if small, start a spec with /specdev if not, and move it to DONE.md when the work has shipped
when_to_use: |
    Use this skill whenever the user mentions:
        - do the next todo
        - do the top item in TODO.md
        - work on the next item
        - todo do

allowed_tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, Skill]
---

# TODO do

Invoke as:
    /todo-do
    /todo-do <item title>

Takes the first item in `TODO.md`, or the named one, and moves it forward:
done outright when it is small, into a spec when it is not, and across to
`DONE.md` when the work has shipped. Follow
[conventions.md](../todo-review/conventions.md); a project's own `TODO.md`
section in `AGENTS.md` or `CLAUDE.md` wins where it differs. The project's
own rules on branches, tests, docs and commits apply throughout.

## 1. Re-check the item before touching code

1. Read the project's `TODO.md` convention section and `TODO.md` in full.
2. **Is it still open and still true?** Check the code it names, `DONE.md`,
   and any task list's `**Status:**` headers. If it is done, propose moving
   it; if its premise is stale, say what changed and propose a correction.
   Either way, stop for the operator.
3. **Is it really one item?** Read it against the rest of the file with
   [conventions.md: Consolidation](../todo-review/conventions.md#consolidation).
   If it shares a root cause with other items, do not fix it alone: propose
   [`/todo-review`](../todo-review/SKILL.md) or a consolidation, and stop.
   Fixing one symptom of a shared cause is how a fix ends up needing a fix.
4. **Is anything ahead of it in progress?** If the item says a spec or task
   list exists for it, the next step is that task list, not a new start.

## 2. Size it

**Small** - do it now - when every one of these holds:

- one logical change, in one package or a few closely related files;
- no change to an artefact's shape, a manifest field, a stage's contract or
  a public API another package uses;
- no section of a spec has to change for the code to match it, beyond a
  sentence or a pointer;
- no run that spends money (an LLM stage) and no change to a real project's
  data is needed to finish it.

**Large** - start a spec - otherwise, and always when the item's Fix
direction says it "goes through the spec first".

Say which it is and why, in a sentence, before going on.

## 3a. Small: do it

1. Follow the project's branch rule (a feature branch, or the worktree the
   operator named).
2. Write the failing test first where the item describes a defect, then the
   fix. Follow the project's code, test and documentation rules - a
   user-visible change updates the user guide in the same change.
3. Run the project's Definition of Done checks, as its task lists name them
   (pre-commit, the scoped tests, any audit or count checker). A checker
   that reads committed history only runs meaningfully after a commit.
4. **Move the item to `DONE.md`**: append its heading and body unchanged at
   the end, then a line
   `Done: YYYY-MM-DD - <what fixed it: commit, test, spec section>.`
   and remove it from `TODO.md`.
5. **Keep the other items' references current.** Grep the remaining
   `TODO.md` items for `path:line` references into every file the fix
   changed and check each against the code. For each one that moved, add a
   line after the item's Fix direction:
   `Note YYYY-MM-DD: since <commit>, ... is at <line>.`
   Never rewrite the dated finding.
6. Report, listing those notes, then show the updated list
   ([conventions.md: Show the list after every change](../todo-review/conventions.md#show-the-list-after-every-change)),
   and ask whether to commit. The item move and the notes go in the same
   commit as the fix.

## 3b. Large: start a spec

1. Invoke `/specdev` through the Skill tool, passing the change the item
   needs and the spec it belongs in: an existing spec the item names, or a
   new one. Carry the item's dated findings into the spec's motivation, and
   any decision that is the operator's to make into a question for them.
2. Stop for the operator to review the spec. Then offer `/taskdev` to break
   it into tasks.
3. **The item stays in `TODO.md`.** Add one line to its body, after its
   Fix direction:
   `Spec: <path to spec>; tasks: <path to task list>.`
   so the next reader sees it is in progress and where. Show the updated
   list ([conventions.md: Show the list after every change](../todo-review/conventions.md#show-the-list-after-every-change)).
4. When the task list's last task is done, move the item to `DONE.md` with
   a `Done:` line naming the spec and the task list. The task list's own
   documentation task is the usual place this happens.

## Real data and real money

- **Back up before a run that rewrites a real project's artefacts**, and
  name the backup by its full path.
- **Simulate a whole stage or none of it.** A dry run of one step predicts
  that step and nothing before it.
- **A run that calls a paid LLM**: ask which provider, with a cost estimate
  sized from a previous run's recorded tokens, before starting. An
  unattended run stops there.
- **When a run surfaces a new defect**, restore what it damaged, file the
  defect with [`/todo-add`](../todo-add/SKILL.md), and stop - do not fix it
  inside this item.

## Stop and re-plan when

- the fix needs a second rule to undo its own side effect;
- the item turns out larger than sized;
- the operator's data was changed in a way nobody predicted.

Say what happened, restore anything damaged, and propose the next step
rather than pushing on.

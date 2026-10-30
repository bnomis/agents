---
name: taskdev
description: Guide the user in the production of a task list from a specification file
when_to_use: |
    Use this skill whenever the user mentions:
        - write a task list
        - task lists
        - plan the implementation
        - break a spec into tasks
        - implement a spec
        - build tasks from a spec

allowed_tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill]
---

# Task development

Invoke as:
    /taskdev <SPEC-NAME>
    /taskdev <SPEC-PATH>

Where:

- <SPEC-NAME> is the title of the spec
- <SPEC-PATH> is the path to a spec or a review, it can be distinguished because it will have slashes "/" in it

If no argument is provided, list existing specs from agents/specs/index.md and ask the user to pick one.

## Spec location

If you are given a <SPEC-NAME> you can find the spec with the following rules.

The spec file is at `agents/specs/<SLUG>/spec.md`, where `<SLUG>` is the slugified version of <SPEC-NAME> (lowercase, spaces to hyphens, non-alphanumeric characters removed). See the [specdev skill](../specdev/SKILL.md) for full slugification rules.

If you are given a <SPEC-PATH> read the spec at that path. The <SLUG> in this case will be the name of the directory containing the spec. For example, for a spec at path `agents/audit-reviews/review-1.md` the <SLUG> is `audit-reviews`.

## Non-spec input

A document is a spec if its path is under agents/specs/ and the filename is spec.md. All other paths are treated as non-spec input.

When the input document is not a spec (e.g., an audit review file):

- Step 3: skip the specdev invocation — mark ambiguous items with **Caveat:** instead
- Step 6: skip API signature comparison — check only whether implementation code exists for the described changes
- Step 9: verify every actionable finding/recommendation has a corresponding task (instead of verifying spec section coverage)
- File header: use **Source:** `<input path>` instead of **Spec:**
- Task template: use **Source Reference:** `<finding number>` instead of **Spec Reference:**

## Gather context

1. Read `AGENTS.md` and `README.md`
2. Read `agents/tasks/index.md` (if it exists)
3. Read existing task files in `agents/tasks/<SLUG>/tasks-*.md` (if they exists)

## Follow existing rules and standards

All tasks should following the standards in AGENTS.md established for source code, testing and file system layout.

## Workflow

1. Read the spec at the resolved path
2. Read related `.md` documents in the same directory
3. If the spec is ambiguous or incomplete or will lead to a "decide with the user" task or subtask, tell the user what the issue is and ask the user whether to invoke the specdev skill (via the Skill tool) to improve it before proceeding. If the user declines, continue but add a warning to the task file header noting which spec sections were ambiguous, and mark affected tasks with `**Caveat:** spec unclear` in their Notes
4. Read any existing `tasks-*.md` files in `agents/tasks/<SLUG>/` to understand prior work
5. Analyse the spec and produce an implementation plan
6. Check if implementation code already exists:
   1. Search `src/` for modules matching task descriptions using Glob and Grep
   2. Compare public API signatures against the spec (function names, parameters, return types)
   3. Check for tests that cover the implemented functionality
   4. Mark tasks as done only if the API matches the spec and tests verify correctness
   5. For partial implementations, mark the task as in-progress and note what remains in the subtasks
7. Write the task list file
8. Update `agents/tasks/index.md` with the new task file entry (create the index if it doesn't exist)
9. Verify coverage: confirm every spec section is addressed by at least one task
10. If there are any tasks or subtasks in the new task list file which require a user decision (i.e. human intervention or decisions) such as "decide with the user" tasks or subtasks, flags these tasks to the user and suggest they update the spec to make the tasks unambiguous so a new task list can be written which does not require human intervention.
11. If the list was written against a review that settles the spec's gaps (choices made and decisions, as a `review-N.md` beside the spec), hand that review over as the shared `reviews.md` rule says before presenting: publish its interactive page, add `**Review page:** <URL>` to its header, and lead step 12's summary with the URL
12. Present the task list summary to the user for review

A decision carried into a task list covers only what it names. When a task
will meet work outside it, the task stops for the user; never write a
"decide X" subtask for the agent running the list to close, and never let a
task extend a decision to cases it did not name.

A closing subtask that moves an item from `TODO.md` to `DONE.md` says to
append its heading and body unchanged, then the `Done:` line, and the last
task's Definition of Done runs the todo-review skill's `verify_bodies.py`
against the `TODO.md` from before the list started. Take that baseline from
the commit that adds the task list
(`git log --diff-filter=A --format=%H -- <task list path>`), and point the
`TODO.md` items at the list (their `tasks:` line) in that same commit. A
baseline from an earlier commit lacks that line, so it checks an older body
and passes a stale one unnoticed.

## Task sizing

The plan should consist of small, self-contained tasks. A self-contained task:

- Is a logical unit that can be implemented, tested, and integrated without breaking the system
- Typically corresponds to a single Python module or a focused change across a few files
- Should be completable in a single working session

Aim for less than 15 tasks per spec. If more are needed, suggest splitting the spec.

## One repository per task list

Every task edits and commits only the repository its task list lives in. A task
list is often run unattended, one task at a time in a worktree of that
repository, where nothing outside it can be changed - a task that reaches into
another repository stops at once and waits for the operator.

When the spec needs work in another repository (a shared library, a checker, a
tool the project calls), do not write a task for it here:

- tell the user, and have that work done before the list runs - by hand, or
  through a task list in that repository;
- give the task that depends on it a Notes line naming the change it waits
  for, and an acceptance criterion this repository can check once the change
  is in.

## Human review stops

When a task stops the list for the operator to review something on an
interactive page (see the shared `reviews.md` rule), the unattended session
that resumes the list may have no tool to read the page's stored answers. It
then sees an empty Answers section and stops again, waiting for answers that
were already given.

So the hand-back from the operator happens outside the unattended run:

- The stopping task's last subtask says: once every item has an answer, an
  operator session reads the page's answers, copies each into the review
  document's Answers section with the date, commits that, and only then
  restarts the list.
- The task that applies the answers reads them from the review document's
  Answers section, never from the page. Its first subtask stops the task as
  `blocked`, naming what is missing, if that section is empty or incomplete.

## Task format

Use user stories for user-facing tasks. For infrastructure or technical tasks where "As a user" doesn't fit naturally, use the technical goal format instead.

Each task should include:

- **Status**: todo / in-progress / done
- **Priority**: high / medium / low
- **Complexity**: small / medium / large
- **Spec Reference**: which section(s) of the spec this task fulfils
- **Subtasks**: atomic actions that are not further decomposable
- **Acceptance Criteria**: testable conditions
- **Definition of Done**: the project's own checks, named literally
- **Notes**: dependencies, relevant file paths, implementation hints

## Task ordering

Tasks should be in implementation order. Take into account:

- Dependencies between tasks (explicit: "Task 3 depends on Task 1")
- Priority (high-priority tasks first when dependencies allow)
- Complexity (consider front-loading simpler tasks to build momentum)

## Cross referencing

If the spec references other specs, check whether tasks from those specs have already been created and note dependencies.

## Definition of done

Every task carries a **Definition of Done** listing the checks that must pass
before it is marked complete. Acceptance criteria say what the task must
achieve; the definition of done says what must be *run* to believe it.

Discover the commands from the repository - never copy them from another
project's task list. A gate naming a command the project does not have reads
as satisfied while silently never running, which is worse than no gate. Look
at `.pre-commit-config.yaml` (noting any hook with `stages: [pre-push]`, which
does not run on a commit), `Makefile` targets, `package.json` scripts,
`pyproject.toml`, and any verification script under `bin/`, `scripts/` or
`tools/` - a whole-tree audit or duplication check especially, since that is
the kind of check that gets run once and ignored when it is not part of "done".

Name each command literally, so the task can be verified without inferring
anything:

```markdown
**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `bin/affected-tests.sh --run` exits 0
- [ ] `bin/audit-changed.sh` exits 0
```

Put the same list on every task. Repetition is the point: a check listed once
in the file header is a check that stops binding by task three.

For the lint and hook check, in two tiers:

- **Every task but the last:** the hooks on the files the task changed. A
  commit already runs every pre-commit hook on its staged files, and every
  `always_run` hook as well, so "the task's commit passes its hooks" is the
  check; name no separate run. Where the project has no pre-commit hooks,
  name the linter on the changed files (`ruff check <files>`).
- **The task list's last task:** `pre-commit run --all-files` (or the
  project's whole-tree lint), once, before the branch merges. It catches what
  a per-file hook cannot see: a change in one file that breaks a check on
  another.

A whole-tree run on every task repeats the slow hooks (a type checker over
the whole tree, an audit sweep) on code the task never touched, and a task
re-runs it after every fix, so most of a task's time goes on checks rather
than on the work.

For the test check, use the project's affected-tests tool where it has one
(the project's own rules or `AGENTS.md` name its commands) rather than naming
test directories, in three tiers:

- **Every task:** only the test files the task writes or edits, and the own
  tests of each source module it changes, named literally in the task.
- **A task that stops for a human review:** the quick form as well - tests
  whose own code imports a changed module, `slow` tests skipped - so the
  reviewer never reviews work on a broken branch.
- **The task list's last task:** the full form, which follows imports
  transitively and catches tests far from a change to shared code. It runs
  once per task list, before the branch merges.

The tool compares the branch with its base, so the last task's run covers
every task's changes; nothing has to remember which files changed. Running
the quick form on every task only moves detection earlier, and where it
selects tests that load large models it can cost a long run on every task,
however small the task. A breakage a task causes
then surfaces in the last task's run instead, still before the merge.

Where a project has no such tool, name the touched test files and the changed
modules' own test files on every task; add every test file that imports a
changed module directly on a task that stops for review; and on the last task
run, for every module the list changed, its importers and the directories
whose tests reach it through other modules.
Never make "run every test directory" a done-check; a full run is the user's
call.

## Components modelled on an existing sibling

When the spec describes a component that parallels one already built - a second
stage in the same pipeline, another provider behind the same interface, a new
package that reads the same artefacts - say so in the task list, and give the
component's last task an explicit deduplication subtask:

```markdown
- [ ] Hoist anything this component duplicates from <sibling> to a single
      owner: grep the tree for each literal collection, constant and one-line
      helper the new modules define, and import rather than copy. Choose the
      owner from the existing import graph; prefer a package the consumer
      already imports over adding a new edge
```

Adapting a sibling is usually the right design - it is how conventions stay
consistent - but it reliably leaves duplicated constants and helpers behind, and
those are invisible from inside the file that creates them. The second copy is
what creates the problem, and by the time it is written the first is an earlier
task nobody is still holding in their head. A whole-tree duplication check will
find them eventually; a subtask finds them while the author still knows why both
copies exist.

Make it the component's last task, not its first: the duplicates do not exist
until the modules that carry them are written.

## Closing the spec

When the input is a spec, give the task list's last task a subtask that marks
the spec finished once the work it describes has shipped:

```markdown
- [ ] Set the spec's `**Status:**` to `implemented`
```

A spec starts as `proposed` (see the [specdev skill](../specdev/SKILL.md)), and
nothing else moves it on. Without this subtask a finished spec keeps saying
`proposed`, and the next reader cannot tell built work from planned work
without reading the task lists. When a task list covers only part of a spec -
a reconciliation after the spec changed, say - set the status only on the list
that completes it. Skip the subtask for non-spec input.

## File output

Write the implementation plan to `agents/tasks/<SLUG>/tasks-N.md`, where N is an index starting from 1.

If the file already exists DO NOT overwrite it. Instead increment N to create a unique filename (e.g., tasks-2.md, tasks-3.md).

Tasks numbering always starts at 1 per file, and dependencies reference file + task number ("tasks-1.md Task 3")

### File header

Every task list file must start with a metadata header:

```markdown
# Tasks: <SPEC-NAME>

**Spec:** `agents/specs/<SLUG>/spec.md`
**Created:** <YYYY-MM-DD>
**Version:** N
```

## Task index

Maintain an index file at `agents/tasks/index.md` listing all task files across all specs. When creating a new task file, add an entry to this index. If the index does not exist, create it.

Format:

```markdown
# Task Index

| Spec | Task File | Version | Created |
|------|-----------|---------|---------|
| [Searcher](../specs/searcher/spec.md) | [tasks-1.md](searcher/tasks-1.md) | 1 | 2026-03-08 |
```

## Reconciling with spec changes

If prior task files exist and the spec has changed since they were written:

1. Check previous task files and flag tasks that no longer align with the spec (removed requirements, changed API, etc.)
2. Check the implementation against the current spec and make a new task file to implement changes to bring the implementation in line with the spec.
3. If there are tasks left over from previous sessions, check against the spec, flag if no longer relevant, if any are still relevant add to the task file created in step 2.

## Task template

Use User Story for user-facing tasks or Technical Goal for infrastructure tasks. Include only one.

```markdown
---

## Task <N>: <description>

**Status:** todo
**Priority:** high/medium/low
**Complexity:** small/medium/large
**Spec Reference:** <section name or "Section X.Y">

**User Story:** As a [user], I want [feature], so that [benefit].
**Technical Goal:** <what needs to happen and why>

**Subtasks:**

- [ ] <atomic action>
...

**Acceptance Criteria:**

- [ ] <testable condition>
...

**Definition of Done:**

- [ ] <the project's lint/format command> passes
- [ ] <the project's typecheck command> passes
- [ ] <the project's test command, scoped to the touched module> passes
- [ ] <each repo-local verification script> exits 0

**Notes:**

- Depends on Task <M>
- Depends on tasks-1.md Task <M> *(use this format for cross-file references)*
- Key files: `path/to/relevant/module.py`
- <any implementation hints or context>

---
```

## Completion checklist

Before finalising the task list, verify:

- [ ] Every section of the spec is covered by at least one task
- [ ] No task is so large it should be split further
- [ ] Dependencies between tasks are explicitly stated
- [ ] Existing completed work is marked as done
- [ ] Task order respects dependency chains
- [ ] No task edits or commits outside this repository
- [ ] A task that applies review answers reads them from the review document, and the stopping task says an operator session copies them there first
- [ ] Prior task files were reviewed to avoid duplicating already-planned work
- [ ] For spec input, the last task sets the spec's status to `implemented`
- [ ] A review written for this list has its interactive page published, and its header names the page's URL

## Version control

Before making any changes to a task file:

1. Check if the task file has uncommitted changes with `git status`
2. If uncommitted changes exist, ask the user if they want to commit them first
3. After editing, stage the task file and index: `git add agents/tasks/<SLUG>/tasks-N.md agents/tasks/index.md`
4. Ask the user if they'd like to commit the changes
5. Commit with a message describing what changed, e.g.: `"taskdev: add error handling tasks"`
6. Do not push unless the user asks

---
name: survey
description: Survey every repository in a workspace for unfinished specs and task lists, fixable expected failures, known bugs, doable TODO items and stale branches or worktrees - then, on request, file each finding in the TODO.md where its fix belongs and propose an implementation order
when_to_use: |
    Use this skill whenever the user mentions:
        - survey all the projects
        - what is left to do across the projects
        - are any specs or task lists not implemented
        - are any xfail tests fixable
        - are there stale branches or worktrees (across several repositories)
        - file todo items for everything the survey found

allowed_tools: [Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion]
---

# Survey

Invoke as:
    /survey [root]

Root defaults to the current directory: a workspace holding several
repositories (the root itself and the repositories below it), or a single
repository. The survey answers five questions for every repository:

1. Which specs and task lists are not implemented?
2. Which tests marked as expected failures (xfail, known bugs, pending
   cases) could be fixed?
3. Which known bugs can be fixed?
4. Which `TODO.md` items can be done now?
5. Which branches and worktrees are stale?

It reads until the report is given. Filing the findings (Phase 4) changes
`TODO.md` files, and runs only when the user asks for it.

A project's own rules win where they differ from this skill. That includes
rules about when tests may run, which matters are never raised (for example a
project that defers a class of decision), and how its `TODO.md` is shaped.

## Ground rules

- **Read only until Phase 4.** No edits, commits, pushes or deletions.
  Deleting stale branches is `/cleanup`'s job, once the user asks for it.
- **No test runs.** The survey reads markers and code; it does not run
  suites. Another session may be using the machine, and a project's rule
  may limit runs to one at a time.
- **Secrets.** Never print environment variables or env files. Test that a
  variable is set with `[ -n "${VAR:-}" ]`, and a directory with `[ -d ... ]`,
  printing yes or no only. Repeat this in every subagent brief.
- **State with a time.** Every claim about repository state comes from a
  check made for it, with `date -u +%H:%M:%S` in the same command (the shared
  `verify-claims.md` rule). Fetch first when the remote matters.
- **Verify before recommending.** A subagent's finding is a lead. Before the
  report recommends acting on one, read the code line it cites yourself.

## Phase 1: Inventory (scripted)

```shell
python3 ~/.claude/skills/survey/inventory.py <root> [--depth N]
```

It prints, per repository: status and changed paths; each worktree (merged
or not, locked, changed paths); each branch (ahead and behind the default
branch, merged by ancestry or patch); task lists with tasks not done; specs
not marked implemented. Keep the output in the scratchpad.

Then judge what the script cannot:

- **Unmerged worktrees and branches.** For each, list the files it changes
  and check whether the default branch already holds them, edited later or
  finished. A draft whose work landed by another route is superseded, so it
  is safe to delete; say how you know.
- **Parked work is not stale.** A branch whose task list says it stops for
  people, data or a decision stays, with the reason.
- **Locked worktrees** may belong to a running session: name them, and leave
  them out of any deletion advice until the user confirms.
- **Unpushed commits** on the default branch: name each one.
- **Specs with no task list** marked implemented are fine. A spec that is
  approved but has no task list is a finding: read why (a deferral recorded
  in the spec, a review answer).

## Phase 2: Per-repository survey (subagents)

Hand the reading to read-only subagents, in parallel. Give one agent to each
large repository (a long `TODO.md`, many specs), and group small ones,
keeping to the session's agent-count guideline. Each brief is the template
below, with the repository paths and anything Phase 1 found for them (a task
list to explain, an approved spec with no tasks):

```text
Read-only survey of <repositories> under <root> (each its own git repo).
Do NOT edit files, commit, or run tests (another session may be using the
machine). Never print environment variables or env files; to test a
variable use `[ -n "${VAR:-}" ] && echo yes`.

For each repository answer, with path:line references:
1. TODO.md (DONE.md for context): each open item in one plain-words line,
   classified (a) doable now without the user, small; (b) needs a spec;
   (c) blocked - on what (an upstream release, people such as annotators or
   native readers, data, a decision the user deferred). Check against the
   code that each item is still true before calling it doable. Flag items
   already fixed but not moved to DONE.md.
2. Tests marked xfail or skip, or registered as known bugs or pending cases
   in a correctness harness. Leave out a harness's self-tests, which xfail
   on purpose, and skips that depend on the environment (a GPU, credentials,
   an optional file), naming those in one line. For each real one: what it
   covers, why it fails, and whether it is fixable now (with the likely fix)
   or blocked.
3. Open findings in reviews, audit reviews, upstream-defect notes and test
   plans that no TODO.md item records.
4. Specs and task lists not implemented: <the Phase 1 leads>. What remains,
   and whether it can start.
Report under <600-700> words, ranked by what is most worth doing now.
```

Tell the user what is running, and relay each agent's findings as it
returns, in plain words. Do not wait for all of them before reporting.

## Phase 3: Report

Re-check the findings you will recommend acting on (Ground rules), then
report under the five questions:

1. **Not implemented:** a table of repository, what, and why it is open.
   Mention status lines that lag finished work in one line.
2. **Expected failures:** what each one waits on. Say plainly when none can
   be fixed now.
3. **Known bugs that can be fixed:** each with its cause (`path:line`),
   size, and whether it needs a spec. Name bugs blocked upstream in one
   line.
4. **TODO items doable now**, then the blocked ones in one line per kind of
   blocker.
5. **Stale branches and worktrees:** safe to delete (merged and clean),
   superseded (with the evidence), parked (with the reason), locked, and
   unpushed commits.

End with the work that needs nothing from the user, and the matters that are
the user's to decide. More than one decision for the user goes on a review
page (the shared `reviews.md` rule), not as a list of questions.

## Phase 4: File the findings (on request)

When the user asks to file the findings, file each one through the
`todo-add` skill's conventions
(`~/.claude/skills/todo-add/SKILL.md`,
`~/.claude/skills/todo-review/conventions.md`):

- **Fixable now, or after a spec:** an item with its cause and a fix
  direction that says whether a spec comes first.
- **Blocked on something outside the work:** an upstream release, human
  labour (labelling, annotators, native readers), data that does not exist
  yet, or a decision the user deferred. File it as deferred, saying what it
  waits on, unless an open item already records it.
- **Already fixed, still in TODO.md:** move it to DONE.md unchanged, with a
  `Done:` line naming the fix.
- **Filed where the fix is made.** A fix in a shared library, a tool or a
  sibling repository is filed in that repository's `TODO.md`. The finding
  repository's item points at it rather than working around it (an accept
  marker hides the fault). This includes repositories no subagent's brief
  covered: the session files those itself before reporting.
- **One cause, one item.** A finding that shares a cause with an open item
  joins it as a dated note or a `###` finding.

Hand the filing to subagents, one per repository or group, each with the
findings for its repositories (paths, causes, fix directions) and these
instructions: follow the `todo-add` skill and conventions; re-verify each
finding in the code; place items by the conventions' order, never just
append; change no existing heading (a known-bug register may read them);
run the repository's checks on the changed files (`pre-commit run --files
TODO.md DONE.md`); do not commit; report where each item went and the
headings table. When an agent corrects a finding, carry the correction into
the report, and into any other repository's item that cites it.

## Phase 5: Hand over

1. Check each repository's state again (`git status --porcelain`, with the
   time). List every changed file as a full absolute path, one per line.
2. Give a table of what was filed: repository, item, and status (doable now,
   needs a spec, deferred and on what, moved to DONE.md).
3. Give the implementation order. Work in different repositories can run in
   parallel, except where one depends on another:
   - a fix in a shared library or tool goes before its consumers' work
     that relies on it;
   - a pin or a checker fix goes before a sweep that is meant to end at
     zero;
   - a spec goes before its code; specs in different repositories can be
     written at the same time;
   - documentation-only items can go at any time;
   - items in the same repository run in sequence;
   - a machine-wide limit on test runs serialises the test runs, not the
     editing.
4. Ask whether to commit with `AskUserQuestion`, as one yes-or-no question:
   one `docs(todo): ...` commit per repository, no push.

## Do not

- Run `/cleanup`, delete a branch, or push during the survey.
- Report a subagent's finding as fact without checking the cited code, or
  state repository state without a fresh, timed check.
- Leave a finding unfiled because it lies outside every subagent's brief.
- File a deferred item for a blocker an open item already records.
- File a matter a project's own rules say is never raised.

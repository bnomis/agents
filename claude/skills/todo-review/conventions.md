# TODO.md and DONE.md conventions

The shared rules for `todo-review`, `todo-add` and `todo-do`. **A project's
own statement of these rules wins**: read `AGENTS.md` (or `CLAUDE.md`) for a
section on `TODO.md` first, and follow it where it differs from this file.

## The two files

- **`TODO.md` holds open work only.** Everything in it is outstanding, so its
  length is a real measure of the backlog.
- **`DONE.md` holds finished work**, chronological, newest last. It is a
  record, not a plan.
- **An item moves, it is never deleted.** Its heading and body go to the end
  of `DONE.md` unchanged, followed by a `Done:` line (see below). The body
  records what was wrong, what was measured and why the fix took its shape -
  the reasoning a later reader wants when asking "was this considered?".
- **An item earns its move when the work is done, not when it is decided.** A
  spec written for it is not done; the code shipping is.
- **Never file a new item in `DONE.md`**, and never add a `## Done` section to
  `TODO.md`: a heading inside a file is easy to append under by accident.
- Leave the operator's own notes alone. Loose, undated jottings the operator
  keeps elsewhere (for example `NOTES.md`) are not items to manage.

## Shape of an item

```markdown
## <specific symptom, not a vague topic>

<!-- doc-counts: accept-start found on YYYY-MM-DD - a dated record, not a claim about the present -->
Found <how and where, with the date>. <What was observed, with the
measurement and the identifiers a reader can chase.>
<!-- doc-counts: accept-end -->

<Cause, with `path/to/file.py` and function names.>

Fix direction: <what to change, and anything that must go through a spec
first>.
```

- **One `##` heading per item**, directly under the file's `#` title. No
  grouping level above items: the file an item is in says whether it is done,
  and a group heading would be a second, drifting claim.
- **Exactly one blank line after every heading.**
- **`###` is allowed inside an item**, for the findings a consolidated item
  carries (see [Consolidation](#consolidation)).
- **Date every finding and measurement.** A number in prose is either dated,
  generated or dropped. Wrap a dated record in the project's accept markers
  when it has a count checker (`doc-counts: accept-start` / `accept-end` in
  repositories using `bin/doc-counts.sh`); otherwise write the date into the
  sentence. Never regenerate or "update" a dated figure: it is a record.
- Plain ASCII punctuation, British spelling.

## Order

**`TODO.md` is in implementation order, nearest first.** The order is the
argument for what to do next. In descending precedence:

1. What **loses work** - destroys or corrupts an artefact, or overwrites a
   decision a person made.
2. What **blocks** a normal workflow - a stage that hard-fails.
3. What is **slow or wasteful** - correct, but paying for nothing.
4. **Features**, each before the one it makes cheaper, safer or more
   meaningful. A cost control goes before what multiplies the calls it
   controls; a validation study after the accuracy work it measures; a
   change that removes a hazard before a change the hazard would break.
5. What is **deferred by decision**.

A new item is **inserted where it belongs**, never appended. A new bug usually
goes at the top.

## Consolidation

**Group by root cause before ordering by precedence.** Precedence ranks
symptoms; it can spread one piece of work across the list - an urgent defect
at the top and the same cause's other findings far below - and then each is
fixed alone, each fix surfacing the next.

Items share a root cause when any of these holds:

- one stored fact, missing, is what each of them re-derives or guesses;
- one fix closes both, or each fix needs the other's;
- one item's fix would make another unsafe, or remove the reason another
  rejected an alternative;
- they change the same artefact shape, contract or spec section.

A consolidated item:

- opens with a title naming the **cause**, a paragraph stating it, and one
  **Fix direction** covering every finding;
- never moves a heading that code or tests read to another level or text:
  before consolidating, grep the repository (source and tests) for each
  heading that would change. A known-bug register whose constants must
  equal a `##` or `###` heading fails when a finding becomes `####`; group
  such items with plain bold lines, not deeper headings. On one project, a
  consolidation that nested findings under `###` group headings stopped the
  correctness suite's known-bug check from starting (2026-10-30);
- carries each original finding **verbatim** under its own `###` heading -
  the old `##` title becomes the `###` title, and the body moves unchanged;
- says which decision it reverses, if any, and why that decision's reason no
  longer holds;
- may be split by stage when only part of a finding shares the cause, the
  remainder staying an item of its own that points at the consolidated one.

**Keep every dated finding.** After rewriting, check mechanically that every
original item body still appears in the new file, character for character.
Change only cross-references that now point at the wrong place ("the next
item"), and bare counts in prose you wrote yourself.

## Warning signs

Stop and consolidate, rather than patch, when:

- a fix needs a second rule to undo its own side effect;
- an acceptance run of one item surfaces a defect in another;
- the same cause is being described a third time in different words.

Name the fact every derivation is compensating for, and propose storing it.

## Checks and commits

- Run the project's checks on the file after editing it - `pre-commit run
  --files TODO.md DONE.md` and any count checker. A checker that reads
  committed history only (`doc-counts`, `audit-changed`) sees the change at
  the next commit; run it again after committing.
- **Commit only when the operator asks.** One logical change per commit;
  `docs(todo): ...` for a `TODO.md`/`DONE.md` change on its own.
- Give every file the operator is asked to open as a full absolute path.

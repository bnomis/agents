# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## `phaseb.py check` rejects the result of every listed question but A4

Found on 2026-11-21 in the Doc batch-size pilot (two runs of 13 batches each
on one project, results kept in the session's scratchpad):
`python3 claude/skills/auditme/checks/phaseb.py check <run dir>` exits 1 on
every Doc1, Doc2, Doc4 and Doc5 run. It reports each result line as
`unparseable ... extra must be a list of strings` and each id as missing,
and lists every batch for retry, though every reviewer returned a
well-formed line per candidate in the brief's own shape. So no Doc run can
pass `check` or be merged into a ledger. Reading the code the same day: the
T1, T2, A1, A11, A17 and A19 briefs ask for a `findings` object, which the
same check rejects, so every listed question but A4 is affected.

Cause: `parse_result` in `claude/skills/auditme/checks/auditme/phaseb/batches.py`
requires A4's `missing` and `extra` lists on every line, and `read_run_verdicts`
in the same file builds each `Verdict.findings` from those two keys alone,
while each brief defines its own output: `drift` (Doc4, Doc5), `stale` and
`missing` (Doc1, Doc2), a `findings` object (T1, T2 and the A questions).
The listers shipped in `c10a5cc`, the T listers in `9da7cc3` and the A
listers in `73df3f4`; their tests ran `check` on A4-shaped output only.

Fix direction: give each registered question its result shape (the keys
its brief names), have `parse_result` and `read_run_verdicts` validate and
store those keys, and add a test per registered question that runs `check`
and `merge` on a line in its brief's shape. It changes the verdict contract
of the repeatable-phase-b spec, which names A4's keys, so it goes through
that spec, or the three listed-question specs, first.

Spec: `agents/specs/repeatable-phase-b/spec.md`, amendment 1.2 (one `findings` object for every question, chosen by the operator on 2026-11-21); tasks: `agents/tasks/repeatable-phase-b/tasks-2.md`.

## Pilot the documentation listers' batch sizes on a real audit

Found on 2026-11-20 in a review of this file:
`agents/specs/listed-phase-b-documentation-questions/spec.md` (Briefs)
registers batch sizes that were never measured - 24 for Doc4 and Doc5, 12
for Doc1 and Doc2 - and says the operator's first run on a real project is
the pilot, run twice as A4's was, with any threshold it exposes landing as a
brief version bump. No item or task records it, and no run has happened:
the listers shipped the same day in `c10a5cc`.

Cause: the batch sizes were set by estimate when the spec was written,
because no Doc question had been run on the listed path yet.

Fix direction: in the next audit, which waits for the item above, run each
Doc question's batches twice with the same brief and compare the verdicts,
as the A4 pilot did. Change a registered batch size in
`claude/skills/auditme/checks/auditme/phaseb/candidates.py`, or a brief
threshold with a version bump under `claude/skills/auditme/phaseb/briefs/`,
only where the two runs disagree or a batch fails to return. Small here; the
run itself is in another project.

Note, 2026-11-21: the item above cleared on 2026-11-21, and the pilot ran the
same day on one project, outside an audit, with both runs kept out of its
ledger. Two runs of 13 batches each at the registered sizes, same briefs:
every batch returned a line for every candidate. Same flag decision per
candidate: Doc4 132 of 133, Doc5 78 of 80, Doc1 9 of 9 (identical path lists
8 of 9), Doc2 17 of 17; 236 of 239 overall. So the batch sizes need no
change. Every disagreement traces to a threshold the reviewers themselves
named as unsettled, which lands as a brief version bump:

- Doc4: whether a fix table dated in the spec ("as classified on
  <date>") is a dated record when the names in it have since changed;
- Doc5: whether an example of printed output that leaves out a line is
  drift or an omission, and whether an `(unresolved)` candidate's other
  statements are judged, not only its tokens;
- Doc5: whether a list of values written out in prose (an `exit_reason`
  list) presents itself as complete;
- Doc1: whether a path the section itself calls ignored, and so absent from
  the tracked tree, is stale.

Merging the pilot's verdicts waits for the `phaseb.py check` item above.

## A project with no audit root skips the project-level checks

Found on 2026-10-31 in `agents/specs/project-setup/spec.md`, amendment 1.2,
which records it as a known limit not fixed there. When a project has no
package under `src/` and no extra root, `audit.py` runs no pass, so the
per-root project-level checks (the lockfile, `AGENTS.md`, spec drift) never
run, and a project with no Python passes them without being checked.

Cause: the project-level checks run inside the per-root loop in `main()` of
`claude/skills/auditme/checks/audit.py`, once per root with duplicates
suppressed. With no root, they never run.

Fix direction: deferred until a project without Python adopts the guards.
Then run the project-level checks once when no root exists, which changes the
driver's contract, so it goes through the spec first.

# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

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

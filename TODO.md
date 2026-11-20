# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## Put the Phase B questions that find most onto the listed path

Found on 2026-11-20 while writing `agents/specs/repeatable-phase-b/spec.md`
(version 1.1), which puts only A4 on the listed path: a program lists every
candidate, reviewers judge each against a versioned brief, and a ledger
reuses each verdict while its code is unchanged. Every other question is
still sampled, so it still turns up sites earlier audits missed in code
nobody changed. Measured the same day on one project's last three full
audits, counting the Phase B question each finding names (a finding may name
more than one): the documentation questions (Doc1, Doc2, Doc4, Doc5) 13;
the test questions T1 and T2 7; A1, A11, A17 and A19 9; A13 and A15 5; A4 3;
the rest 5. Listing A4 alone covers the smallest of these groups.

Cause: version 1 of the listed path covers one question, and nothing yet
says which come next or what happens to a question that cannot be listed.

Fix direction: an amendment of the repeatable-phase-b spec per group, in
this order, each with its lister, brief and tests, shipped between audits:

1. Doc4 and Doc5, then Doc1 and Doc2: a candidate is each backticked name
   in a spec or user document that resolves to a function, setting, class
   or file, with the code it names in the hash.
2. T1 and T2: branchy functions and the functions a property test would
   suit, from the AST, with their test files in the hash.
3. A11, A19, A1 and A17: the match statements, broad handlers, external
   calls and public surfaces the AST already finds.

The same spec settles a rule for the questions that stay sampled (A13, A15
and any whose candidates cannot be listed): run them on changed files only,
or every few audits, and report their new sites as coverage, not drift.

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

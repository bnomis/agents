# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## spec-api-signature-drift compares a spec's method with a module-level function of the same name

Found on 2026-11-06 in a sweep of another project: two of its
`spec-api-signature-drift` hits were false. Each was a `@classmethod`
`load(cls, ...)` written inside a `class` block in a spec's API section,
reported as drifting from that project's one module-level `def load(path)`,
an unrelated function in another module. The real classmethods matched the
spec.

Cause: `_DEF_LINE_RE` in
`claude/skills/auditme/checks/auditme/rules/project_hygiene.py` allows
leading whitespace, so `check_spec_api_signature_drift` reads a method
indented inside a spec's `class` block as a `def`, and looks its bare name up
in `_source_definitions`, which holds module-level definitions only. The
rule's "a name with no module-level definition does not fire" refinement
then does not apply, because a module-level function happens to share the
name.

Fix direction: skip a spec `def` that sits inside a `class` block (indented
under a `class` line in the same fence), as the rule already skips methods on
the source side; or, more ambitiously, compare it with the method of that
class in the source. Add a test beside the existing refinements in
`claude/skills/auditme/tests/test_nested_underscore_and_spec_signatures.py`:
a spec class with a `load` classmethod and an unrelated module-level `load`
in the source does not fire. Small; no spec needed.

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

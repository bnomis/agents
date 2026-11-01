# TODO

Open work only, in implementation order, nearest first. Finished items move to
`DONE.md` unchanged. See the shared `todo-add` and `todo-review` skills for
the shape of an item.

## auditme rules report hits the code does not have

Found on 2026-11-01 while clearing every unaccepted hit in another project,
which accepted each site with a marker and listed it in its own records. The
patterns, by rule:

- `raises-section-drift` attributes a callee's `Raises:` entry to a caller
  that cannot take the raising path: the caller passes an argument value
  that rules the error out (a fixed name, an optional argument left unset, a
  value every caller has already checked against the supported list), or
  passes only types the callee's dispatch error does not apply to, or calls
  the callee only inside a guard (`if is_model(x):`) that rules the error out.
- `raises-section-drift` reports an error caught in a nested function and
  re-raised on one branch with a bare `raise` as never reaching the caller.
- `missing-raises-section` counts a `raise` inside a nested function as
  reaching the caller when the enclosing function catches it, either by the
  exception's base class or because the nested function's only call sits in
  a `try`.
- `passthrough-shim` flags a wrapper whose single `return target(...)`
  computes its arguments, or reuses a parameter as a default
  (`table.get(name, name)`), and flags functions decorated `@pytest.fixture`,
  which tests request by name.
- `non-alphabetical-literal` flags an `__all__` in the order ruff RUF022
  requires (constants, classes, functions), which its ASCII order contradicts.

Cause: the rules decide from the shape of a call or a `raise` alone. The
`Raises:` rules do not follow argument values, guards or handlers within the
enclosing function; `passthrough-shim` does not check that the arguments are
the wrapper's parameters passed on unchanged; and the ordering rule has no
case for `__all__`.

Fix direction: one rule at a time, in `claude/skills/auditme/checks/`, each
with a test fixture for the false positive: skip a `raise` caught within the
same enclosing function, count a bare `raise` as raising the caught types,
flag a shim only when its arguments are its own parameters unchanged, skip
pytest fixtures, and accept the RUF022 order for `__all__`. Following
argument values and guards for `raises-section-drift` is the largest, and
may be better done as skipping callees whose raise depends on an argument;
decide that in a spec first. Each change frees the accept markers the other
project added, which it removes once it pins the change.

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

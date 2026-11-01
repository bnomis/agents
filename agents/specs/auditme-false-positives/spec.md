# Auditme false positives

**Version:** 1.0
**Status:** proposed
**Date:** 2026-11-01

Narrows five predicates of the auditme checker that report hits the code does
not have. Each change is a refinement in the sense of `SKILL.md`, "Refining a
predicate": it removes a sub-pattern from what a rule reports, never adds one.
Each gets a test asserting that the carve-out does not fire, a
`Refinement (2026-11-01): ...` paragraph in its check's docstring, and a dated
entry under "Documented refinements" in `claude/skills/auditme/SKILL.md`.

Motivation: the `TODO.md` item "auditme rules report hits the code does not
have", found on 2026-11-01 while clearing every unaccepted hit in another
project, which accepted each site with a marker. Its findings, restated:

1. `raises-section-drift` attributes a callee's `Raises:` entry to a caller
   that cannot take the raising path: the caller passes an argument value
   that rules the error out, passes only types the callee's dispatch error
   does not apply to, or calls the callee only inside a guard that rules the
   error out.
2. `raises-section-drift` reports an error caught in a nested function and
   re-raised on one branch with a bare `raise` as never reaching the caller.
3. `missing-raises-section` counts a `raise` inside a nested function as
   reaching the caller when the enclosing function catches it, by the
   exception's base class or because the nested function's only call sits in
   a `try`.
4. `passthrough-shim` flags a wrapper whose single `return target(...)`
   computes its arguments or reuses a parameter (`table.get(name, name)`),
   and flags functions decorated `@pytest.fixture`.
5. `non-alphabetical-literal` flags an `__all__` in the order ruff's RUF022
   requires.

Decision (operator, 2026-11-01): for finding 1, skip callee errors whose
every raise depends on the callee's arguments, rather than evaluating the
caller's values and guards. A caller that really can pass a bad value is then
left to the Phase B review (checklist item A4).

## Module location

The checker is not under `src/`; this repository keeps it with its skill.

- `claude/skills/auditme/checks/auditme/rules/error_handling.py`:
  `check_raises_section_drift`, `check_missing_raises_section`,
  `_handler_passes_on`
- `claude/skills/auditme/checks/auditme/rules/imports_and_surfaces.py`:
  `check_passthrough_shim`
- `claude/skills/auditme/checks/auditme/rules/style_and_naming.py`:
  `check_nonalphabetical_literals`
- tests: `claude/skills/auditme/tests/test_error_handling.py`,
  `test_imports_and_surfaces.py`, `test_style_and_naming.py`
- docs: `claude/skills/auditme/SKILL.md`, `docs/guide/checker.md`

No check is added or removed, so `CHECKS` in `registry.py` and
`tests/registry-order.txt` do not change.

## API

The check signatures do not change. New module-level helpers in
`error_handling.py`, replacing the class-tree closure inside
`check_raises_section_drift` so both `Raises:` rules share it:

```python
def package_class_parents(trees: Iterable[ast.Module]) -> dict[str, set[str]]:
    """Map each top-level class's short name to the tails of its written bases.

    Pooled across every module of the package, as the drift rule's closure
    does today: a base written `mod.Base` contributes `Base`.
    """


def class_lineage(name: str, parents: Mapping[str, set[str]]) -> set[str]:
    """Return `name` and every ancestor reachable through `parents`.

    Cycles terminate; an unknown name returns `{name}`.
    """


def argument_dependent(func: ast.FunctionDef | ast.AsyncFunctionDef, error: str, parents: Mapping[str, set[str]]) -> bool:
    """Whether every raise of `error` in `func` depends on its arguments.

    True when `func`'s own scope (nested defs, lambdas and classes excluded)
    holds at least one `raise X(...)` or `raise mod.X(...)` whose lineage
    contains `error`, and each such raise has an enclosing `If` (in its body
    or `orelse`) or `Match` inside `func` whose test or subject reads a Name
    that is one of `func`'s parameters (any kind). False otherwise, including
    when `func` raises `error` only through its own callees.
    """


def nested_call_sites(func: ast.FunctionDef | ast.AsyncFunctionDef) -> list[tuple[ast.AST, tuple[HandlerLevel, ...]]]:
    """`_reach_sites(func.body)` plus, for each call by bare name to a def
    nested directly in `func`'s body, that def's own reach sites with the
    call's handler levels prepended. One level deep; a nested def that is
    never called contributes nothing.
    """
```

In `style_and_naming.py`:

```python
def ruff_dunder_all_key(name: str) -> tuple[int, list[int | str]]:
    """Sort key for ruff's RUF022 order of `__all__`.

    Group 0: more than one character and `name.isupper()` (SCREAMING_SNAKE);
    group 1: first character upper case (CamelCase); group 2: the rest.
    Within a group, natural order: digit runs compare as integers.
    """
```

## Error handling

The checks raise nothing new. A crash inside a check is still reported by the
driver as `auditme-check-crash`. Where the new analysis cannot decide, it
keeps today's hit: a callee whose node cannot be found (a re-export of
something other than a function) is not argument-dependent, and a call whose
target is not a bare-named nested def adds no nested sites.

## Implementation

**1. `raises-section-drift`: argument-dependent callee errors.** When a
callee's documented name would reach the caller, look up the callee's
`FunctionDef` in the parsed modules (by the qualname `resolve` already
returns). If `argument_dependent(callee, name, parents)`, the name does not
reach this caller through that call. Omissions only: the extra-declaration
branch is unchanged. Test shapes: a callee raising `ParseError` under
`if strict:` with `strict` a parameter, and under the `else` of an
`isinstance(value, ...)` chain on a parameter, gives no omission hit for its
caller; the same raise outside any `if`, or under an `if` testing a
module-level name, still does; a callee that raises the name both inside and
outside a parameter guard still does.

**2. `raises-section-drift`: nested functions.** Replace
`_reach_sites(node.body)` with `nested_call_sites(node)`, so a raise or call
in a nested def the subject calls reaches the subject under the call's
levels. Change `_handler_passes_on` to look for a bare `raise` or
`raise <bound>` only within the handler's own scope (`_walk_within_scope`),
not inside a def or lambda defined in the handler. A bare `raise` under an
`if` in the handler still passes the caught types on. The task starts with a
failing test reproducing finding 2 as stated (outer declares `ParseError`;
a nested def catches it from `parse()` and re-raises it on one branch; the
outer calls the nested def). If the reproduction needs a different shape
from the one this section fixes, the task stops for the operator.

**3. `missing-raises-section`: caught raises.** For each subject (still every
function at any depth), build its lineage table with `package_class_parents`
over the package, and take its sites from `nested_call_sites`. A raise counts
when its name passes today's test (`raise X(...)`/`raise mod.X(...)`, ends in
`Error`, not in `STDLIB_ERRORS`) and no handler level at its site catches its
`class_lineage` without passing it on (`_level_catches`, which also treats a
bare `except:`, `Exception` and `BaseException` as catching). A raise inside
a nested def counts only through a call site, so a def that is returned and
never called contributes nothing; it is still its own subject. The
`__init__.py`/`errors.py` skip and the `Raises:` marker regex are unchanged.

**4. `passthrough-shim`: real forwarding only.** Keep today's shape, and add:
every keyword value is also a Name of one of the wrapper's parameters (a
`**` keyword is not); no parameter is passed twice across positional and
keyword arguments; and a function with any decorator is skipped, since a
decorator registers it for something else (a fixture, a command, a route).

**5. `non-alphabetical-literal`: `__all__`.** For an `Assign` or `AnnAssign`
whose single target is the Name `__all__`, the members pass when they equal
`sorted(members)` or `sorted(members, key=ruff_dunder_all_key)`. Other
literals keep the plain `sorted()` test. Test fixture, checked against ruff
0.17.3 `--select RUF022 --fix` on 2026-11-01:
`['X_Y', 'Thing', '_private', 'helper', 'item2', 'item10']` passes for
`__all__` and is a hit for any other name.

**Docs.** Each check's docstring gains its `Refinement (2026-11-01): ...`
paragraph (`check_nonalphabetical_literals` gains a docstring stating its
predicate). `SKILL.md` "Documented refinements" gains one entry per rule in
the existing format, and the A4 line describing `raises-section-drift` adds
that argument-dependent callee errors are skipped and left to review.
`docs/guide/checker.md` updates the rows for the four rules.

**Closing.** Move the `TODO.md` item to `DONE.md` with a `Done:` line naming
this spec and its task list, and set this spec's status to `implemented`.

## Testing

New tests beside each rule's existing ones, using the `project` and
`run_check` fixtures (`tests/conftest.py`) and, for the drift rule, the
`drift` helper with `ERRORS` and `CALLEE`. Each carve-out has a test that it
does not fire and a neighbouring test that the unrefined shape still fires.
Every existing test in the three test files passes unchanged.

## Acceptance criteria

- Each of the five findings, written as a fixture, gives no hit.
- Each shape listed above as "still" a hit gives one.
- `uv run --no-project --with pytest pytest claude/skills/auditme/tests -q -p no:cacheprovider` passes.
- `uv run --no-project python claude/skills/auditme/checks/audit.py .` in this
  repository reports no new unaccepted hit.

## External dependencies

None: the checker stays standard-library only. Ruff is used once, by hand,
to confirm the RUF022 fixture; the tests do not run it.

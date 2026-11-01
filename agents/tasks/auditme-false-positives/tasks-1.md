# Tasks: Auditme false positives

**Spec:** `agents/specs/auditme-false-positives/spec.md`
**Created:** 2026-11-01
**Version:** 1

Implements the whole spec: five narrowings of the auditme checker, the two
shared helpers they need, the documentation, and the closing move of the
`TODO.md` item "auditme rules report hits the code does not have", which
points at this list.

Every change only narrows what a rule reports. Each narrowing task writes its
tests first and sees them fail: a test that the carve-out does not fire, and
a neighbouring test that the unrefined shape still fires. Every existing test
in the touched test files must pass unchanged; a task that needs to change an
existing test stops as `blocked` and names it.

No check is added or removed, so `CHECKS` in
`claude/skills/auditme/checks/auditme/registry.py` and
`claude/skills/auditme/tests/registry-order.txt` stay as they are.

The repository has no affected-tests tool. Each task names its own test
files; the last task runs every test tree the checker's change can reach.
Test commands run from the repository root.

---

## Task 1: Hoist the package class tree into shared helpers

**Status:** done
**Priority:** high
**Complexity:** small
**Spec Reference:** API (`package_class_parents`, `class_lineage`)

**Technical Goal:** Move the class-tree logic out of the closure inside
`check_raises_section_drift` into module-level helpers, so Task 4 can use the
same lineage for `missing-raises-section`. Behaviour does not change.

**Subtasks:**

- [x] Tests first in `claude/skills/auditme/tests/test_error_handling.py`, under a new `# package_class_parents and class_lineage` heading: a base written `Base` and one written `mod.Base` both give `Base`; classes from two modules are pooled; `class_lineage` returns the name and every ancestor transitively; a cycle (`A(B)`, `B(A)`) terminates; an unknown name gives `{name}`. Run them and see them fail
- [x] In `claude/skills/auditme/checks/auditme/rules/error_handling.py`, add `package_class_parents(trees: Iterable[ast.Module]) -> dict[str, set[str]]` and `class_lineage(name: str, parents: Mapping[str, set[str]]) -> set[str]` with the spec's signatures and docstrings, beside `module_tuple_constants`
- [x] Replace the `package_classes`/`parents` construction and the `ancestors` closure in `check_raises_section_drift` with calls to the helpers; keep `is_domain` reading the same set of top-level class names

**Acceptance Criteria:**

- [x] The new tests pass
- [x] Every existing `raises-section-drift` test passes unchanged

**Definition of Done:**

- [x] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [x] `uv run --no-project --with pytest pytest claude/skills/auditme/tests/test_error_handling.py -q -p no:cacheprovider` passes

**Notes:**

- Key code: `check_raises_section_drift` (the class tree is built near its top, `ancestors` and `is_domain` are inner functions)
- Tests use the `project` and `run_check` fixtures in `claude/skills/auditme/tests/conftest.py`; the helpers can be tested directly on `ast.parse` trees

---

## Task 2: `raises-section-drift` skips argument-dependent callee errors

**Status:** todo
**Priority:** high
**Complexity:** medium
**Spec Reference:** Implementation 1; API (`argument_dependent`); Error handling

**Technical Goal:** A callee error whose every raise sits under a test of the
callee's own parameters no longer reaches the callee's callers, as the
operator decided on 2026-11-01.

**Subtasks:**

- [ ] Tests first, beside the existing drift tests, using the `drift` helper with `ERRORS` and a callee of its own: no omission hit for the caller when the callee raises `ParseError` only under `if strict:` (`strict` a parameter), or only in the `else` of an `if isinstance(value, ...)` / `elif` chain on a parameter, or only in a `match` on a parameter; still one omission hit when the raise is outside any `if`, under an `if` that tests a module-level name, or both inside and outside a parameter guard; still one hit when the callee only documents `ParseError` and raises it through its own callee. Run them and see the "no hit" cases fail
- [ ] Add `argument_dependent(func, error, parents) -> bool` with the spec's signature and docstring. Walk `func`'s own scope only (`_walk_within_scope`); a raise counts when `_raised_name` gives a name whose `class_lineage` contains `error`; it depends on arguments when an enclosing `If` (body or `orelse`) or `Match` inside `func` has a test or subject reading a `Name` in `func`'s parameters (positional-only, positional, `*args`, keyword-only, `**kwargs`)
- [ ] In `check_raises_section_drift`, keep a map from qualname to `FunctionDef` while collecting subjects; where a resolved callee's documented name would reach the caller, skip it when `argument_dependent(callee_node, name, parents)`. A qualname with no `FunctionDef` is not argument-dependent. Omissions only: leave the extra-declaration branch alone
- [ ] Add a `Refinement (2026-11-01): ...` paragraph to `check_raises_section_drift`'s docstring stating the carve-out, and that a caller that can pass a bad value is left to the Phase B review (A4)

**Acceptance Criteria:**

- [ ] Every case above passes
- [ ] Every existing `raises-section-drift` test passes unchanged

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --no-project --with pytest pytest claude/skills/auditme/tests/test_error_handling.py -q -p no:cacheprovider` passes

**Notes:**

- Depends on Task 1
- The drift rule never reads a callee's body today; it uses only the callee's documented `Raises:` (`raises_section_names`). This task adds the one body read the decision needs
- The decision covers only callee errors that depend on the callee's arguments. It does not cover evaluating the caller's values or guards; a case that needs that stays a hit

---

## Task 3: `raises-section-drift` follows called nested functions

**Status:** todo
**Priority:** high
**Complexity:** medium
**Spec Reference:** Implementation 2; API (`nested_call_sites`)

**Technical Goal:** An error a nested function catches and re-raises on one
branch, called by the subject, reaches the subject's callers; a bare `raise`
inside a def defined in a handler no longer makes that handler re-raise.

**Subtasks:**

- [ ] First, reproduce finding 2 as the spec states it: a test where the subject declares `ParseError` in `Raises:`, defines a nested def that calls `parse()` inside `try:` with `except ParseError:` re-raising it with a bare `raise` on one branch of an `if`, and calls the nested def. Run it and record the hit it gives. If it gives no hit, or the hit is not the one this task fixes (an "extra" `declares ParseError, which never reaches the caller`), stop the task as `blocked` with the test and its output: the fix below covers only that shape
- [ ] Further tests: a nested def that is defined but never called adds nothing (an omission hit for the subject does not appear because of it); a call to the nested def inside the subject's own `try`/`except ParseError` that does not re-raise means `ParseError` does not reach; a handler in the subject that defines a nested def containing a bare `raise`, and itself does not re-raise, catches. Run them and see the new-behaviour cases fail
- [ ] Add `nested_call_sites(func)` with the spec's signature and docstring: `_reach_sites(func.body)`, plus, for each call by bare `Name` to a def nested directly in `func.body`, that def's `_reach_sites(def.body)` with the call's levels prepended; one level deep
- [ ] In `check_raises_section_drift`, use `nested_call_sites(node)` in place of `_reach_sites(node.body)`
- [ ] Change `_handler_passes_on` to search the handler with `_walk_within_scope` rather than `ast.walk`, so a raise inside a def, lambda or class defined in the handler does not count; a bare `raise` under an `if` in the handler still does
- [ ] Extend the `Refinement (2026-11-01)` paragraph in `check_raises_section_drift`'s docstring with the nested-function case

**Acceptance Criteria:**

- [ ] The reproduction test no longer gives the hit, and every case above passes
- [ ] Every existing `raises-section-drift` and translator-envelope test passes unchanged (both use handler helpers)

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --no-project --with pytest pytest claude/skills/auditme/tests/test_error_handling.py -q -p no:cacheprovider` passes

**Notes:**

- Depends on Task 1
- `_reach_sites` skips nested defs, lambdas and classes today, and `_handler_passes_on` uses `ast.walk`, which enters them; `_walk_within_scope` is the existing scope-bounded walk in the same module
- Check every caller of `_handler_passes_on` (grep it) before changing it

---

## Task 4: `missing-raises-section` ignores caught raises

**Status:** todo
**Priority:** high
**Complexity:** medium
**Spec Reference:** Implementation 3

**Technical Goal:** A raise that a handler around it catches, by its own
class or a base class, no longer counts as reaching the caller, and a nested
def's raise counts only where the nested def is called.

**Subtasks:**

- [ ] Tests first, beside the existing `missing-raises-section` tests (an `errors.py` with `ProbeError` and `ParseError(ProbeError)`, and a module using them): no hit when `raise ParseError(...)` sits in a `try` whose handler catches `ParseError`, `ProbeError`, `Exception` or a bare `except:` without re-raising; no hit when a nested def raises it and the nested def's only call sits in such a `try`; no hit when a nested def raises it and is returned but never called in the subject (the nested def is still reported as its own subject when it has a docstring without `Raises:`); still a hit when the handler re-raises, catches an unrelated class, or there is no handler; still a hit for a nested def called outside any `try`. Run them and see the "no hit" cases fail
- [ ] In `check_missing_raises_section`, build the parents table once per package with `package_class_parents`; for each subject (still every function at any depth), take sites from `nested_call_sites(node)`; a `Raise` site counts when its name passes today's test and no handler level at the site catches `class_lineage(name, parents)` (`_level_catches`, which treats a bare `except:`, `Exception` and `BaseException` as catching)
- [ ] Keep the `__init__.py`/`errors.py` skip and the `Raises:` marker regex as they are
- [ ] Add a docstring paragraph `Refinement (2026-11-01): ...` stating the carve-out

**Acceptance Criteria:**

- [ ] Every case above passes
- [ ] The existing `missing-raises-section` tests pass unchanged

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --no-project --with pytest pytest claude/skills/auditme/tests/test_error_handling.py -q -p no:cacheprovider` passes

**Notes:**

- Depends on Tasks 1 and 3
- The rule reads one file at a time today; the parents table needs every module of the package, as `check_raises_section_drift` builds it

---

## Task 5: `passthrough-shim` flags only real forwarding

**Status:** todo
**Priority:** medium
**Complexity:** small
**Spec Reference:** Implementation 4

**Technical Goal:** A wrapper that computes or repeats an argument, or is
decorated, is no longer reported as a pass-through shim.

**Subtasks:**

- [ ] Tests first in `claude/skills/auditme/tests/test_imports_and_surfaces.py`, beside the existing shim tests: no hit for `return table.get(name, name)`; no hit for a keyword argument with a computed value (`f(x, size=len(x))`) or a `**kwargs` keyword; no hit for a function decorated `@pytest.fixture`, `@pytest.fixture(scope='module')`, or any other decorator; still a hit for `return f(a, b)` and for `return f(a, key=key)` with `a` and `key` parameters. Run them and see the "no hit" cases fail
- [ ] In `check_passthrough_shim`: skip a function with any decorator; require every keyword to have a name (`kw.arg is not None`) and a value that is a `Name` of one of the wrapper's parameters; require that no parameter appears twice across positional and keyword arguments
- [ ] Add a docstring paragraph `Refinement (2026-11-01): ...` stating the carve-out and why a decorator excludes a function (it registers the function for something else)

**Acceptance Criteria:**

- [ ] Every case above passes
- [ ] The existing `passthrough-shim` tests pass unchanged

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --no-project --with pytest pytest claude/skills/auditme/tests/test_imports_and_surfaces.py -q -p no:cacheprovider` passes

**Notes:**

- Key file: `claude/skills/auditme/checks/auditme/rules/imports_and_surfaces.py`, `check_passthrough_shim`
- Skipping every decorator, not only `@pytest.fixture`, is the spec's choice

---

## Task 6: `non-alphabetical-literal` accepts ruff's `__all__` order

**Status:** todo
**Priority:** medium
**Complexity:** small
**Spec Reference:** Implementation 5; API (`ruff_dunder_all_key`)

**Technical Goal:** An `__all__` sorted the way ruff's RUF022 sorts it is no
longer reported.

**Subtasks:**

- [ ] Tests first in `claude/skills/auditme/tests/test_style_and_naming.py`, beside the existing literal tests: `__all__ = ['X_Y', 'Thing', '_private', 'helper', 'item2', 'item10']` gives no hit; the same list assigned to any other name gives one; a plainly sorted `__all__` gives no hit; an `__all__` in neither order gives one; an annotated `__all__: list[str] = [...]` in RUF022 order gives no hit. Direct tests of `ruff_dunder_all_key` on the same names. Run them and see the RUF022 cases fail
- [ ] In `claude/skills/auditme/checks/auditme/rules/style_and_naming.py`, add `ruff_dunder_all_key(name)` with the spec's signature and docstring: group 0 when `len(name) > 1 and name.isupper()`, group 1 when `name[:1].isupper()`, group 2 otherwise; then a natural key splitting digit runs into integers
- [ ] In `check_nonalphabetical_literals`, for an `Assign` or `AnnAssign` whose single target is the `Name` `__all__`, pass when the members equal `sorted(members)` or `sorted(members, key=ruff_dunder_all_key)`
- [ ] Give `check_nonalphabetical_literals` a docstring stating its predicate (top-level assignments of string tuples, lists, sets and `frozenset(...)` literals; the fixed-length tuple exemption) and the `Refinement (2026-11-01): ...` paragraph

**Acceptance Criteria:**

- [ ] Every case above passes
- [ ] The existing `non-alphabetical-literal` tests pass unchanged

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --no-project --with pytest pytest claude/skills/auditme/tests/test_style_and_naming.py -q -p no:cacheprovider` passes

**Notes:**

- The fixture list was checked against ruff 0.17.3 `ruff check --isolated --select RUF022 --fix` on 2026-11-01; the tests do not run ruff

---

## Task 7: Document the refinements

**Status:** todo
**Priority:** medium
**Complexity:** small
**Spec Reference:** Implementation, "Docs"

**User Story:** As someone reading an audit hit or the checker's guide, I
want each narrowed rule to say what it no longer reports, so that I can tell
a missing hit from a carve-out.

**Subtasks:**

- [ ] `claude/skills/auditme/SKILL.md`, "Documented refinements": one entry per rule, `raises-section-drift`, `missing-raises-section`, `passthrough-shim` and `non-alphabetical-literal`, each dated 2026-11-01, in the existing format (the carve-out with an example, what keeps the old behaviour, and the helper and module to see)
- [ ] `claude/skills/auditme/SKILL.md`, checklist item A4: add that `raises-section-drift` skips a callee error every raise of which depends on the callee's arguments, and that Phase B reviews whether a caller can pass a value that takes that path
- [ ] `docs/guide/checker.md`: update the rows for `missing-raises-section`, `raises-section-drift`, `passthrough-shim` and `non-alphabetical-literal` to match the narrowed predicates
- [ ] Check each description against the code the earlier tasks wrote

**Acceptance Criteria:**

- [ ] Each entry names a helper that exists (`grep -n 'def <helper>'` finds it)
- [ ] `uv run --group docs mkdocs build --strict` passes

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --group docs mkdocs build --strict` passes

**Notes:**

- Depends on Tasks 2-6
- No file in this repository may name an external project (`claude/rules/rule-scope.md`; the `no-project-names` hook checks it): the finding came from "another project"

---

## Task 8: Close the spec

**Status:** todo
**Priority:** medium
**Complexity:** small
**Spec Reference:** Acceptance criteria; Implementation, "Closing"

**Technical Goal:** Check the whole change before the branch merges, move the
`TODO.md` item to `DONE.md`, and mark the spec implemented.

**Subtasks:**

- [ ] Run `uv run --no-project python claude/skills/auditme/checks/audit.py .` on this branch, and the same command in a temporary worktree of `main` (`git worktree add --detach <scratch> main`, removed afterwards), and compare their unaccepted hits. A hit on the branch that `main` does not have stops the task as `blocked` with both outputs
- [ ] Move the `TODO.md` item "auditme rules report hits the code does not have" to the end of `DONE.md`: append its heading and body unchanged, then `Done: <date> - agents/specs/auditme-false-positives/spec.md, agents/tasks/auditme-false-positives/tasks-1.md: the five refinements, documented in SKILL.md.`, and remove it from `TODO.md`
- [ ] Set the spec's `**Status:**` to `implemented`

**Acceptance Criteria:**

- [ ] The spec's acceptance criteria hold: each finding's fixture gives no hit, each "still" shape gives one, and this repository's audit has no new unaccepted hit

**Definition of Done:**

- [ ] `pre-commit run --all-files` exits 0
- [ ] `pre-commit run auditme-all --hook-stage manual --all-files` exits 0
- [ ] `uv run --no-project --with pytest --with pyyaml pytest claude/skills/auditme/tests claude/skills/project-setup/tests tests -q -p no:cacheprovider` passes
- [ ] `uv run --group docs mkdocs build --strict` passes
- [ ] `git show $(git log --diff-filter=A --format=%H -- agents/tasks/auditme-false-positives/tasks-1.md):TODO.md > <scratch>/todo-before.md`, then `python3 claude/skills/todo-review/verify_bodies.py <scratch>/todo-before.md TODO.md DONE.md` exits 0

**Notes:**

- Depends on Tasks 1-7
- After the merge and push, the operator checks that the CI and docs runs on `main` passed; a task in the list cannot see GitHub
- The other project removes its accept markers once it pins this change; that is its own work, not a task here

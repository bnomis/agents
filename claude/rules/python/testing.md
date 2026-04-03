---
paths:
  - "**/*.py"
---

# Python Testing

Below `<project>` is the current project's top level module name.

## Test layout

- Test files live in `src/tests/` and mirror the source layout:
  - `src/<project>/<name>.py` -> `src/tests/test_<name>.py`
  - `src/<project>/<pkg>/<file>.py` -> `src/tests/<pkg>/test_<file>.py`
- Test functions are prefixed with `test_`
- Make and use re-usable pytest fixtures
- Place fixtures files in `src/tests/fixtures/` with names that mirror the source module names
- Load fixtures in the `src/tests/conftest.py` file
- Use hypothesis for functions with well-defined input domains
- Use `pytest.raises` for expected exceptions

## Test data and fixtures

- Place reusable sample texts and expected outputs in `src/tests/fixtures/`
- Name fixture files to mirror the source module they test (e.g., `fixtures/lexical.py` for `extractors/lexical.py`)
- For feature extraction tests, include at least one known-good input/output pair per language so regressions are caught
- Keep fixture texts short but representative  - avoid large corpora in the test suite

## Test coverage

- All new public functions must have tests
- Bug fixes must include a regression test

## Running tests

```bash
source bin/activate.sh
pytest path/to/test_file.py
```

## Testing scope

- NEVER run the full test suite at once. Always run tests scoped to the files/modules you changed.
- Before running tests, preview what will run with `pytest --co -q <path>` to make sure the scope looks right. Then run them.
- Use `pytest path/to/test_file.py` for individual files.
- Use `pytest path/to/test_file.py::TestClassName::test_method` to run a single test.
- After fixing a failing test, re-run only that test first before broadening scope.
- If you need broader validation, run one directory at a time, e.g. `pytest src/tests/data/` then `pytest src/tests/integration/` separately.

## Finding tests

You can list all available tests with the command:

```shell
pytest --co -q
```

To run only tests for files you changed:

```shell
pytest $(git diff --name-only --diff-filter=d origin/main...HEAD | grep 'test_.*\.py$')
```

To also find tests related to changed source files:

```shell
pytest $(git diff --name-only --diff-filter=d origin/main...HEAD | sed -n \
  -e 's|^src/<project>/\([^/]*\)\.py$|src/tests/test_\1.py|p' \
  -e 's|^src/<project>/\([^/]*\)/\([^/]*\)\.py$|src/tests/\1/test_\2.py|p' \
  -e 's|^src/<project>/\([^/]*\)/\([^/]*\)/\([^/]*\)\.py$|src/tests/\1/\2/test_\3.py|p')
```

## Performance guardrails

- Mark tests that load large models or process real datasets with `@pytest.mark.slow`
- Skip slow tests during development with `pytest -m "not slow"`
- The `slow` marker is registered in `pyproject.toml`  - no warning will be raised
- Hypothesis tests must always use `@settings(max_examples=20, deadline=10000)` to keep run times predictable
- Do not increase `max_examples` without good reason  - the default of 20 balances coverage and speed
- If a single test takes more than 10 seconds, it should be marked `@pytest.mark.slow`

# Audit Review 1

**Date:** 2026-11-21
**Scope:** full
**Commit:** 5b51aa3
**Script output:** /tmp/audit-agents.jsonl (7 hits, 0 accepted, 7 unaccepted)
**Convergence note:** first review of this repository; no earlier review to compare. The sweep ran with `--extra-root claude --extra-root tests`, since the repository has no `src/` and `bin/` holds no Python: without them the sweep reads no Python at all. The code listers of the listed questions (A1, A4, A11, A17, A19, T1, T2) read only `src/`, found no candidates, and those questions were judged by hand over the same files, so none of them has ledger verdicts. Doc4 and Doc5 were judged through `phaseb.py`, every candidate as new.

## Summary

The sweep reports 7 unaccepted hits: four `bare-parametric-annotation` and one
`silent-broad-except` in `claude/statusline.py`, and two `literal-duplication` in
the survey skill's tests. Phase B finds 38 sites across A1, A9, A19, A24, D1,
P2, Sec2, Sec4, T1, T2, T3 and Doc5, nearly all low severity, in four small
standard-library scripts and the skill reference page.

## Mechanical findings (from checks/audit.py)

### Rule: silent-broad-except - no logger and no raise in body

- **Severity:** medium
- **Instance count:** 1
- **Locations:**
  - `claude/statusline.py:24` - `except:` around the git subprocess calls, setting `git_status = ''`
- **Recommendation:** catch only what the git calls raise when the directory is not a repository or git is missing (`subprocess.CalledProcessError`, `FileNotFoundError`), so an unexpected failure is not hidden. Same handler as Phase B A19.

### Rule: bare-parametric-annotation - bare `dict` without element type

- **Severity:** low
- **Instance count:** 4
- **Locations:**
  - `claude/statusline.py:31` - `def get_model(data: dict) -> str:`
  - `claude/statusline.py:37` - `def get_directory(data: dict) -> str:`
  - `claude/statusline.py:45` - `def get_context_window(data: dict) -> str:`
  - `claude/statusline.py:53` - `def get_rate_percentage(data: dict) -> str:`
- **Recommendation:** annotate as `dict[str, object]` (the parsed session JSON), or a `TypedDict` of the fields read.

### Rule: literal-duplication - identical ordered literal across 2 locations

- **Severity:** low
- **Instance count:** 2
- **Locations:**
  - `claude/skills/survey/tests/test_inventory.py:74` - `['agents/tasks/probe/tasks-1.md: 1/2 done; open: todo']`
  - `claude/skills/survey/tests/test_inventory.py:104` - the same expected list
- **Recommendation:** the two tests check one output for two status formats (heading lines and table rows); hoist the expected list to a module constant, or accept with a scoped marker saying each test states its own expectation.

## Phase B per-question results

Files: `claude/statusline.py`, `claude/skills/survey/inventory.py`,
`claude/skills/test-log-review/scan.py`, `claude/skills/todo-review/verify_bodies.py`,
and the tests `claude/skills/survey/tests/test_inventory.py`,
`claude/skills/test-log-review/tests/test_scan.py`, `tests/test_install_claude.py`.
No previous review, so every sampled question ran on the whole tree (mode: full).

### A1: External call envelope (listed; lister found no candidates, judged by hand)

- **Hits:**
  - `claude/statusline.py:61` - `json.load(sys.stdin)` outside any `try`
  - `claude/skills/survey/inventory.py:57` - `subprocess.run(['git', ...])` in `git()` with no envelope
  - `claude/skills/survey/inventory.py:70` - `directory.iterdir()` in `find_repositories`
  - `claude/skills/survey/inventory.py:124` - `path.read_text` in `open_task_lists`
  - `claude/skills/survey/inventory.py:149` - `path.read_text` in `open_specs`
  - `claude/skills/test-log-review/scan.py:61` - `path.stat()` in `newest_per_kind`
  - `claude/skills/test-log-review/scan.py:67` - `path.read_text` in `parse_log`
  - `claude/skills/todo-review/verify_bodies.py:40` - `read_text` of the old file
  - `claude/skills/todo-review/verify_bodies.py:41` - `read_text` of each new file
- None of the scripts defines a domain `*Error`; each failure reaches the user as a traceback.

### A2 (sampled): Except tuple coverage

- **Mode:** full
- **Hits:** none (the only `try`, `claude/statusline.py:11`, wraps subprocess calls, not disk or parsers)

### A3 (sampled): Domain-error layering

- **Mode:** full
- **Hits:** none (no `raise` statement, no `*Error` class)

### A4: Docstring `Raises` accuracy (listed; no candidates, judged by hand)

- **Hits:** none (no docstring has a `Raises:` section)

### A5-A8 (sampled)

- **Mode:** full
- **Hits:** none for each: A5 no config object; A6 no pipeline-stage class; A7 no hand-written `__init__`; A8 the one dataclass instance (`scan.py:91`) is not mutated

### A9 (sampled): Pure-named function side effects

- **Mode:** full
- **Hits:**
  - `claude/skills/survey/inventory.py:61` - `find_repositories` tests the file system (`.exists()`, `iterdir`, `is_dir`, `is_symlink`)
  - `claude/skills/survey/inventory.py:89` - `is_merged` runs git three times
  - `claude/skills/test-log-review/scan.py:51` - `find_repositories` globs and calls `is_dir()` / `.exists()`
  - `claude/skills/test-log-review/scan.py:66` - `parse_log` reads the file; the `load_` exemption does not cover `parse_`

### A10 (sampled), A11 (listed, judged by hand), A12-A16 (sampled), A17 (listed, judged by hand)

- **Mode:** full
- **Hits:** none for each: A10 `is_merged` and `needs_investigation` answer exactly their names; A11 no `Literal` or enum; A12 no `assert` outside tests; A13 `LogReport(...)` gets a distinct value per slot; A14 each project-state helper runs once per repository; A15 `LogReport` built at one site; A16 no `cli/`; A17 no `__init__.py`

### A18 (sampled)

- **Mode:** full
- **Hits:** none (no callback methods)

### A19: Wrong logger level for broad-except (listed; judged by hand)

- **Hits:**
  - `claude/statusline.py:24` - bare `except:` degrades to `git_status = ''`; per [Conflicts with no winner], narrow or remove it rather than adding a logger

### A20-A23 (sampled)

- **Mode:** full
- **Hits:** none for each: A20 the only module-level container read elsewhere would be `inventory.SKIP_DIRS`, already a `frozenset` and read by no other module; A21 no lazy init; A22 no raise/return fall-through; A23 no undocumented component discarded

### A24 (sampled): Identity of subprocess calls

- **Mode:** full
- **Hits:**
  - `claude/skills/survey/inventory.py:165` - `is_merged` runs for each worktree's branch, then again at `:173` for the same branch from `git branch`, unmemoised

### A25 (sampled)

- **Mode:** full
- **Hits:** none (`SKIP_DIRS` holds only `str` and is read by no other module)

### S1 (sampled): Type annotations

- **Mode:** full
- **Hits:** none in non-test source beyond the sweep's four `bare-parametric-annotation` hits
- **Test tree count:** 12 missing parameter annotations, 11 missing return annotations, 2 modules affected (`claude/skills/test-log-review/tests/test_scan.py`: 9 and 8; `tests/test_install_claude.py`: 3 and 3), 1 module fully annotated (`claude/skills/survey/tests/test_inventory.py`). `pyproject.toml` enables `ANN` for every file, and the test tree is not exempt.

### S2-S4 (sampled)

- **Mode:** full
- **Hits:** none: S2 names follow convention; S3 no `TYPE_CHECKING`; S4 `AGENTS.md` references no rule file

### P1, P3 (sampled)

- **Mode:** full
- **Hits:** none

### P2 (sampled): Blocking I/O in hot paths

- **Mode:** full
- **Hits:**
  - `claude/statusline.py:12` - four git subprocesses in sequence (lines 12-15) on every status refresh; one `git status --porcelain=v2 --branch` returns the branch and both counts

### Sec1, Sec3, Sec5 (sampled)

- **Mode:** full
- **Hits:** none (every tracked file scanned for secrets; every subprocess call takes an argument list without a shell; nothing is logged)

### Sec2 (sampled): Input validation at system boundaries

- **Mode:** full
- **Hits:**
  - `claude/statusline.py:32` - session JSON shape unchecked: `{"model": null}` raises `TypeError`; likewise lines 38, 46 and 54
  - `claude/statusline.py:49` - `int(ctx)` on an unchecked value raises `ValueError` for a non-number; likewise line 57
  - `claude/statusline.py:61` - empty stdin raises `json.JSONDecodeError`

### Sec4 (sampled): Path traversal

- **Mode:** full
- **Hits:**
  - `claude/skills/test-log-review/scan.py:59` - `repository.glob(pattern)` takes `--glob` as given; a `..` in it reaches files outside the repository (read and summarised only)

### T1: Test coverage of branchy logic (listed; lister found no candidates, judged by hand)

- **Hits:**
  - `claude/statusline.py:9` - `git_status`: no test (no test file for `statusline.py`)
  - `claude/statusline.py:31` - `get_model`: no test
  - `claude/statusline.py:37` - `get_directory`: no test
  - `claude/statusline.py:45` - `get_context_window`: no test
  - `claude/statusline.py:53` - `get_rate_percentage`: no test
  - `claude/skills/survey/inventory.py:182` - `main` (including its `if not repos` exit 1): no test
  - `claude/skills/todo-review/verify_bodies.py:18` - `item_bodies`: no test (no test file for `verify_bodies.py`)
  - `claude/skills/todo-review/verify_bodies.py:35` - `main` (exit 2, 1 and 0 branches): no test

### T2: Property-based tests (listed; lister found no candidates, judged by hand)

- **Hits:**
  - `claude/skills/survey/inventory.py:46` - `statuses(list[str]) -> list[str]`, a pure parser, has no hypothesis test
  - `claude/skills/test-log-review/scan.py:46` - `log_kind(str) -> str` (idempotent stamp stripper) has two example asserts only
  - `claude/skills/todo-review/verify_bodies.py:18` - `item_bodies(str) -> dict[str, str]` has a round-trip property and no test

### T3 (sampled): Integration vs unit balance

- **Mode:** full
- **Hits:**
  - `claude/skills/survey/inventory.py:182` - `main` (find, report, print) has no end-to-end test
  - `claude/statusline.py:61` - the script body (stdin to printed line) has no end-to-end test
  - `claude/skills/todo-review/verify_bodies.py:35` - `main` has no end-to-end test

### D1 (sampled): Declared in pyproject

- **Mode:** full
- **Hits:**
  - `claude/skills/survey/tests/test_inventory.py:7` - imports `pytest`, which no dependency group declares (CI supplies it with `uv run --no-project --with pytest`)

### D2, D3 (sampled)

- **Mode:** full
- **Hits:** none (`ruff` and `mkdocs` are run, `mkdocs-material` is the named theme; no `lockfile-drift` hit)

### Doc1, Doc2: AGENTS.md structure and tools (listed; no candidates)

- **Hits:** none. `AGENTS.md` is the single line `# agents`, with no structure or tools section for the predicates to compare.

### Doc3 (sampled)

- **Mode:** full
- **Hits:** none

### Doc4: Specs match implementation (listed)

- **Candidates judged:** 8 of 8 (all from `agents/specs/cleanup/spec.md`), brief version 3
- **Hits:** none

### Doc5: User docs match implementation (listed)

- **Candidates judged:** 75 of 75, in 4 batches, brief version 3
- **Hits:**
  - `docs/reference/skills.md:9` - says each skill's frontmatter has a `when_to_use` list; `claude/skills/paper-pdf-hunter/SKILL.md` has none
  - `docs/reference/skills.md:85` - `/specdev`'s commit message given as `specdev: add error handling section to <slug> spec`; the skill commits `docs(specs): add error handling to <SLUG> spec`
  - `docs/reference/skills.md:131` - `/testplan` stops to commit `testplan: add plan-N`; the skill commits `docs(tests): add plan-N`

### Coverage (sampled)

First review: every sampled hit above is coverage, none is drift.

## Phase B findings (consolidated)

### Finding: Scripts let I/O errors escape as tracebacks

- **Category:** A
- **Question:** A1
- **Severity:** low
- **Location:** `claude/statusline.py:61`; `claude/skills/survey/inventory.py:57`, `:70`, `:124`, `:149`; `claude/skills/test-log-review/scan.py:61`, `:67`; `claude/skills/todo-review/verify_bodies.py:40`, `:41`
- **Description:** each script is a standalone standard-library tool with no domain error, so a missing file, an unreadable directory or a missing git surfaces as a Python traceback.
- **Recommendation:** in each `main`, catch `OSError`, `UnicodeDecodeError` and `subprocess` failures and print one line naming the path, with a non-zero exit; for the status line, print nothing rather than fail.

### Finding: Pure-prefixed names that do I/O

- **Category:** A
- **Question:** A9
- **Severity:** low
- **Location:** `claude/skills/survey/inventory.py:61`, `:89`; `claude/skills/test-log-review/scan.py:51`, `:66`
- **Description:** `find_repositories`, `is_merged` and `parse_log` read the file system or run git.
- **Recommendation:** rename (`scan_repositories`, `branch_is_merged`, `read_log`), or accept each with a scoped marker if the name is judged to say it.

### Finding: Status line hides every failure and runs git four times per refresh

- **Category:** A, P
- **Question:** A19, P2
- **Severity:** medium
- **Location:** `claude/statusline.py:24`, `:12`
- **Description:** the bare `except:` swallows any error, including a bug; the four sequential git calls run on every refresh.
- **Recommendation:** catch `subprocess.CalledProcessError` and `FileNotFoundError` only, and take branch and counts from one `git status --porcelain=v2 --branch` call.

### Finding: Status line trusts the session JSON's shape

- **Category:** Sec
- **Question:** Sec2
- **Severity:** low
- **Location:** `claude/statusline.py:32`, `:38`, `:46`, `:49`, `:54`, `:57`, `:61`
- **Description:** a `null` object, a non-numeric percentage or empty stdin crashes the script, and the status line shows nothing.
- **Recommendation:** read each field through `isinstance` checks and drop the part when the value is not the expected type.

### Finding: Unmemoised merge check per branch

- **Category:** A
- **Question:** A24
- **Severity:** low
- **Location:** `claude/skills/survey/inventory.py:165`, `:173`
- **Description:** a branch checked out in a worktree has `is_merged` (three git calls) run twice per report.
- **Recommendation:** compute it once per branch in `report`, in a dict both loops read.

### Finding: `--glob` can leave the repository

- **Category:** Sec
- **Question:** Sec4
- **Severity:** low
- **Location:** `claude/skills/test-log-review/scan.py:59`
- **Description:** a pattern with `..` reads logs outside the repository; the input is the operator's own option and files are only summarised.
- **Recommendation:** skip matches whose resolved path is not inside the repository, or reject a pattern containing `..`.

### Finding: Untested scripts and branches

- **Category:** T
- **Question:** T1, T2, T3
- **Severity:** medium
- **Location:** `claude/statusline.py` (every function and the script body); `claude/skills/todo-review/verify_bodies.py:18`, `:35`; `claude/skills/survey/inventory.py:46`, `:182`; `claude/skills/test-log-review/scan.py:46`
- **Description:** `statusline.py` and `verify_bodies.py` have no tests at all; `inventory.main` is never run; the pure parsers `statuses`, `log_kind` and `item_bodies` have no property tests.
- **Recommendation:** add `tests/test_statusline.py` (each getter and the stdin-to-line path, with a stub git) and `claude/skills/todo-review/tests/test_verify_bodies.py` (exit 0, 1 and 2); an end-to-end test of `inventory.main` on a temporary repository; hypothesis tests for the three parsers, with bounded examples.

### Finding: pytest undeclared

- **Category:** D
- **Question:** D1
- **Severity:** low
- **Location:** `claude/skills/survey/tests/test_inventory.py:7`
- **Description:** the tests import `pytest`, which `pyproject.toml` does not declare; CI adds it with `--with pytest`.
- **Recommendation:** `uv add --dev pytest`, and let CI use the locked one.

### Finding: Skill reference drifts from three skills

- **Category:** Doc
- **Question:** Doc5
- **Severity:** low
- **Location:** `docs/reference/skills.md:9`, `:85`, `:131`
- **Description:** the page says every skill has `when_to_use` (paper-pdf-hunter has none), and gives `/specdev`'s and `/testplan`'s commit messages in a form neither skill uses.
- **Recommendation:** give paper-pdf-hunter a `when_to_use` list (or say on the page that it has none), and copy the two commit messages from the skills.

## Files reviewed (Phase B)

- `claude/statusline.py` - A1-A25, S1-S4, P1-P3, Sec1-Sec5, T1-T3
- `claude/skills/survey/inventory.py` - A1-A25, S1-S4, P1-P3, Sec1-Sec5, T1-T3
- `claude/skills/test-log-review/scan.py` - A1-A25, S1-S4, P1-P3, Sec1-Sec5, T1-T3
- `claude/skills/todo-review/verify_bodies.py` - A1-A25, S1-S4, P1-P3, Sec1-Sec5, T1-T3
- `claude/skills/survey/tests/test_inventory.py`, `claude/skills/test-log-review/tests/test_scan.py`, `tests/test_install_claude.py` - A1-A25, S1 (count), T1-T3
- `bin/install-claude.sh` - Sec1-Sec5, T1
- `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, `.github/workflows/*.yml`, `mkdocs.yml` - D1-D3, Doc2
- `AGENTS.md`, `CLAUDE.md`, `README.md` - Doc1-Doc3, S4
- `agents/specs/cleanup/spec.md` - Doc4 (8 candidates), spec review
- `README.md`, `docs/` - Doc5 (75 candidates)

## Spec review

`agents/specs/cleanup/spec.md` (version 1.1, `implemented`) has every template
section. Its Module location names `claude/skills/cleanup/SKILL.md` rather than
a path under `src/`, which the repository does not have; no gap.

## Prior findings re-verified

None: this is the first review, and there is no `summary.md` or audit-review task list.

## Recommendations

1. Medium: narrow the status line's bare `except:` and add tests for `statusline.py` and `verify_bodies.py`.
2. Low: fix the three lines of `docs/reference/skills.md`; declare `pytest`; type the `data` parameters.
3. Low: the remaining A1, A9, A24, Sec2, Sec4, T2, T3 items, and the duplicated test literal.

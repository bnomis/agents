# Tasks: Audit review 1

**Source:** `agents/audit-reviews/review-1.md`
**Created:** 2026-11-21
**Version:** 1

Every finding of review-1, grouped by the script it is in. The four scripts
(`claude/statusline.py`, `claude/skills/survey/inventory.py`,
`claude/skills/test-log-review/scan.py`,
`claude/skills/todo-review/verify_bodies.py`) are run with a bare `python3`
by the skills and the status line, so they stay standard-library only: no
task adds an import outside the standard library to them. `pytest` and
`hypothesis` are for their tests only.

The audit hooks run the sweep with its default roots, which read no Python in
this repository (review-1's convergence note), so each task runs the sweep
itself with this repository's roots:

```shell
python3 ~/.claude/skills/auditme/checks/audit.py . --extra-root claude --extra-root tests > /tmp/audit-agents.jsonl
python3 -c "import json; [print(r['rule'], r['path'], r['line']) for r in map(json.loads, open('/tmp/audit-agents.jsonl')) if not r['accepted']]"
```

The second command lists each unaccepted hit as `rule path line`.

Choices made in writing this list, where the review offered two ways:

- the pure-prefixed names that do I/O (A9) are renamed, not accepted;
- the duplicated expected list (`literal-duplication`) becomes a module constant;
- paper-pdf-hunter gets a `when_to_use` list, so the skill reference stays true;
- the status line prints nothing and exits `0` on input it cannot read, since
  Claude Code shows its output as the status line; the other scripts print one
  line naming the path and exit non-zero.

---

## Task 1: Declare the test dependencies and run every test directory in CI

**Status:** done
**Priority:** high
**Complexity:** small
**Source Reference:** Finding "pytest undeclared" (D1)

**Technical Goal:** The tests import `pytest`, and Tasks 3-5 add `hypothesis`
tests, but neither is declared: CI adds pytest with `--with pytest`, and the
CI step runs `claude/skills/survey/tests` and `tests` but not
`claude/skills/test-log-review/tests`. Declare both, and run every test
directory from the locked environment.

**Subtasks:**

- [x] `uv add --dev pytest hypothesis` (the resolver's 14-day `exclude-newer` applies; a probe on 2026-11-21 resolved `pytest>=9.2.0` and `hypothesis>=6.170.15`)
- [x] In `.github/workflows/ci.yml`, replace `uv run --no-project --with pytest pytest claude/skills/survey/tests tests -q -p no:cacheprovider` with `uv run pytest claude/skills/survey/tests claude/skills/test-log-review/tests tests -q -p no:cacheprovider`
- [x] Update any doc that gives the old test command (`git grep -n 'with pytest'` outside `agents/audit-reviews/`)

**Acceptance Criteria:**

- [x] `pyproject.toml`'s `dev` group lists `pytest` and `hypothesis`, and `uv lock --check` exits 0
- [x] `git grep -n -- '--with pytest'` finds nothing outside `agents/audit-reviews/`

**Definition of Done:**

- [x] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [x] `uv run pytest claude/skills/survey/tests claude/skills/test-log-review/tests tests -q -p no:cacheprovider` exits 0
- [x] The sweep (header) lists no unaccepted hit in a file this task changed

**Notes:**

- Key files: `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`

---

## Task 2: Make the status line robust, cheaper and tested

**Status:** done
**Priority:** high
**Complexity:** medium
**Source Reference:** `silent-broad-except` (`claude/statusline.py:24`); `bare-parametric-annotation` (`:31`, `:37`, `:45`, `:53`); findings "Status line hides every failure and runs git four times per refresh" (A19, P2), "Status line trusts the session JSON's shape" (Sec2), "Scripts let I/O errors escape as tracebacks" (A1, `:61`), "Untested scripts and branches" (T1, T3, status line part)

**User Story:** As a Claude Code user, I want the status line to show what it
can and never crash or hide a bug, so that a malformed session field or a
missing git does not blank the line or a real error go unseen.

**Subtasks:**

- [x] Write `tests/test_statusline.py` first, loading the script with `importlib` from `claude/statusline.py`: each getter with the field present, missing, `null`, zero and a non-number; `git_status` with a stub `git` on `PATH` (a repository with staged and modified files, not a repository, git missing); and the whole script run as a subprocess with JSON on stdin, with empty stdin and with non-JSON
- [x] Move the module-level script body into `main() -> int` behind `if __name__ == '__main__':`, so the tests can import the module without reading stdin
- [x] Annotate the getters' parameter as `dict[str, object]` and read each nested field through `isinstance` checks, dropping the part when a value is not the expected type (a `dict`, a non-empty `str`, an `int` or `float`)
- [x] In `main`, treat empty or non-JSON stdin, or a top level that is not an object, as no fields: print an empty line and return `0`
- [x] Replace the four git calls with one `git status --porcelain=v2 --branch`, taking the branch from `# branch.head` and counting staged and modified entries from the `1`/`2` lines' `XY` field, with the same output as now
- [x] Replace the bare `except:` with `except (subprocess.CalledProcessError, FileNotFoundError):`, so any other error propagates
- [x] Update `docs/reference/cli.md`'s `claude/statusline.py` section: it now says it exits `1` with a traceback when stdin is not JSON; say it prints an empty line and exits `0`

**Acceptance Criteria:**

- [x] `{"model": null}`, `{"context_window": {"used_percentage": "n/a"}}`, empty stdin and `not json` each print a line without a traceback and exit `0`
- [x] Inside a repository the output's `git:` part is the same as before for a clean tree, staged files and modified files
- [x] `git` runs once per refresh (the stub records its calls)
- [x] No bare `except:` remains in `claude/statusline.py`

**Definition of Done:**

- [x] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [x] `uv run pytest tests/test_statusline.py -q -p no:cacheprovider` exits 0
- [x] The sweep (header) lists no unaccepted hit in `claude/statusline.py` or `tests/test_statusline.py`

**Notes:**

- Depends on Task 1 (pytest declared)
- Key files: `claude/statusline.py`, `docs/reference/cli.md`
- The script must stay standard-library only
- A stub `git` is a small executable script in a temporary directory prepended to `PATH`, as `tests/test_install_claude.py` stubs `uvx`

---

## Task 3: Survey inventory: errors, names, one merge check per branch, tests

**Status:** todo
**Priority:** medium
**Complexity:** medium
**Source Reference:** `literal-duplication` (`claude/skills/survey/tests/test_inventory.py:74`, `:104`); findings A1 (`inventory.py:57`, `:70`, `:124`, `:149`), A9 (`:61`, `:89`), A24 (`:165`, `:173`), T1 (`:182`), T2 (`:46`), T3 (`:182`)

**Technical Goal:** The inventory script lets I/O and git failures escape as
tracebacks, has two pure-prefixed names that do I/O, runs its three-call
merge check twice for a branch checked out in a worktree, and has no test of
`main` or property test of its status parser.

**Subtasks:**

- [ ] Rename `find_repositories` to `scan_repositories` and `is_merged` to `branch_is_merged`, with their callers and tests
- [ ] In `report`, compute `branch_is_merged` once per branch and reuse it in the worktree and branch loops
- [ ] In `main`, catch `OSError`, `UnicodeDecodeError` and `subprocess.CalledProcessError`, print one line to stderr naming the path or the git command, and return `1`
- [ ] In `test_inventory.py`, hoist the expected list at lines 74 and 104 into one module constant both tests use
- [ ] Add a test of `main` on a temporary workspace (the output's heading and one repository section), one for a root with no repository (exit `1`, the stderr line), and one for an unreadable task list (exit `1`, the path named)
- [ ] Add a hypothesis test of `statuses` (each `**Status:**` heading line or table row it is given yields exactly its status word, in order), with `max_examples` bounded

**Acceptance Criteria:**

- [ ] `git grep -nwE 'find_repositories|is_merged' -- claude/skills/survey` finds nothing
- [ ] A test counts `git` calls for a branch checked out in a worktree and sees one merge check
- [ ] The new `main` tests and the hypothesis test pass

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run pytest claude/skills/survey/tests -q -p no:cacheprovider` exits 0
- [ ] The sweep (header) lists no unaccepted hit in `claude/skills/survey/inventory.py` or its tests

**Notes:**

- Depends on Task 1 (hypothesis declared)
- Key files: `claude/skills/survey/inventory.py`, `claude/skills/survey/tests/test_inventory.py`
- `claude/skills/survey/SKILL.md` names no function of the script (checked 2026-11-21); check again before renaming

---

## Task 4: verify_bodies: errors and tests

**Status:** todo
**Priority:** medium
**Complexity:** small
**Source Reference:** findings A1 (`claude/skills/todo-review/verify_bodies.py:40`, `:41`), T1 (`:18`, `:35`), T2 (`:18`), T3 (`:35`)

**Technical Goal:** `verify_bodies.py` has no tests, and an unreadable file
ends it with a traceback. Give it a one-line error and a test directory, and
run that directory in CI.

**Subtasks:**

- [ ] Write `claude/skills/todo-review/tests/test_verify_bodies.py`, importing the script as the other skills' tests do (`sys.path` insert): `item_bodies` on text before the first heading, consecutive headings, a trailing item and blank-line stripping; `main` exiting `0` when every body survives, `1` naming each lost one, and `2` with fewer than two paths
- [ ] Add a hypothesis round-trip test: build a file from generated titles and bodies (no line starting `## ` inside a body), parse it with `item_bodies` and get the same mapping back, with `max_examples` bounded
- [ ] In `main`, catch `OSError` and `UnicodeDecodeError`, print `cannot read <path>: <reason>` to stderr and return `2`; add the case to the module docstring and to its test
- [ ] Add `claude/skills/todo-review/tests` to the test step of `.github/workflows/ci.yml`

**Acceptance Criteria:**

- [ ] A missing new file gives exit `2` and the path on stderr, with no traceback
- [ ] Every branch of `item_bodies` and `main` has a test

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run pytest claude/skills/todo-review/tests -q -p no:cacheprovider` exits 0
- [ ] The sweep (header) lists no unaccepted hit in `claude/skills/todo-review/verify_bodies.py` or its tests

**Notes:**

- Depends on Task 1
- The todo-review, todo-run-order and taskdev skills run this script and require exit `0`; exit `2` stays a failure for them

---

## Task 5: Test-log scan: errors, names, containment, property test

**Status:** todo
**Priority:** medium
**Complexity:** small
**Source Reference:** findings A1 (`claude/skills/test-log-review/scan.py:61`, `:67`), A9 (`:51`, `:66`), Sec4 (`:59`), T2 (`:46`)

**Technical Goal:** The scan lets `stat` and read failures escape, has two
pure-prefixed names that do I/O, follows a `..` in `--glob` out of the
repository, and tests `log_kind` with two examples only.

**Subtasks:**

- [ ] Rename `find_repositories` to `scan_repositories` and `parse_log` to `read_log`, with their callers and tests
- [ ] In `newest_per_kind`, skip a match whose resolved path is not inside the resolved repository
- [ ] In `main`, catch `OSError`, print one line to stderr naming the path, and return `1`
- [ ] Add tests: a `--glob` with `..` reaches no file outside the repository; an unreadable log gives exit `1` and its path
- [ ] Add a hypothesis test of `log_kind`: it is idempotent, and a name with a timestamp added in the form the module strips maps to the name without it; `max_examples` bounded

**Acceptance Criteria:**

- [ ] `git grep -nwE 'find_repositories|parse_log' -- claude/skills/test-log-review` finds nothing
- [ ] `claude/skills/test-log-review/SKILL.md` still describes the script's options and output correctly

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run pytest claude/skills/test-log-review/tests -q -p no:cacheprovider` exits 0
- [ ] The sweep (header) lists no unaccepted hit in `claude/skills/test-log-review/scan.py` or its tests

**Notes:**

- Depends on Task 1
- Key files: `claude/skills/test-log-review/scan.py`, `claude/skills/test-log-review/tests/test_scan.py`

---

## Task 6: Bring the skill reference in line with the skills

**Status:** todo
**Priority:** low
**Complexity:** small
**Source Reference:** finding "Skill reference drifts from three skills" (Doc5: `docs/reference/skills.md:9`, `:85`, `:131`)

**User Story:** As a reader of the skill reference, I want what it says about
each skill to match the skill, so that I can rely on it without opening the
skill file.

**Subtasks:**

- [ ] Add a `when_to_use` list to `claude/skills/paper-pdf-hunter/SKILL.md`'s frontmatter, in the shape the other skills use, with trigger phrases taken from its description
- [ ] `docs/reference/skills.md:85`: give `/specdev`'s commit message as the skill does, `docs(specs): add error handling to <SLUG> spec`
- [ ] `docs/reference/skills.md:131`: give `/testplan`'s as `docs(tests): add plan-N`
- [ ] Search the page for any other commit message it quotes and compare each with its skill

**Acceptance Criteria:**

- [ ] Every `claude/skills/*/SKILL.md` frontmatter has `when_to_use`
- [ ] Each commit message `docs/reference/skills.md` quotes matches its skill's

**Definition of Done:**

- [ ] The task's commit passes its pre-commit hooks (never `--no-verify`)
- [ ] `uv run --group docs mkdocs build --strict` exits 0

**Notes:**

- Key files: `docs/reference/skills.md`, `claude/skills/paper-pdf-hunter/SKILL.md`, `claude/skills/specdev/SKILL.md`, `claude/skills/testplan/SKILL.md`

---

## Task 7: Whole-tree checks and the audit summary

**Status:** todo
**Priority:** high
**Complexity:** small
**Source Reference:** all findings; the auditme skill's step 8b (refresh the summary after the task list ships)

**Technical Goal:** Check the whole tree once before the branch merges, and
record in the audit summary which findings this list resolved.

**Subtasks:**

- [ ] Run the sweep (header) over the whole tree and fix or accept, with a scoped marker giving the reason, any unaccepted hit left
- [ ] Move each finding resolved by Tasks 1-6 from `agents/audit-reviews/summary.md`'s Unresolved findings to Recently resolved, as `review-1` raised, resolved by this task list; leave any not resolved where it is, with a dated note saying why
- [ ] Update the summary's `**Last script run hit count:**` from this run

**Acceptance Criteria:**

- [ ] The sweep lists no unaccepted hit
- [ ] `agents/audit-reviews/summary.md` lists no finding as unresolved that the sweep or a test shows fixed

**Definition of Done:**

- [ ] `pre-commit run --all-files` exits 0
- [ ] `uv run pytest claude/skills/survey/tests claude/skills/test-log-review/tests claude/skills/todo-review/tests tests -q -p no:cacheprovider` exits 0
- [ ] `uv run --group docs mkdocs build --strict` exits 0
- [ ] The sweep (header) lists no unaccepted hit

**Notes:**

- Depends on Tasks 1-6

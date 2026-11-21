# Audit Summary

**Last updated:** 2026-11-21
**Last review:** review-1
**Total reviews conducted:** 1
**Last script run hit count:** 7 (0 accepted)
**Script version:** e924b332c5c6809821c1635aa7a1d3714064120de0317c733f7f09dfa6b50537

The sweep runs as `audit.py . --extra-root claude --extra-root tests`: the
repository has no `src/`, and `bin/` holds no Python.

## Unresolved findings

### Status line hides every failure and runs git four times per refresh

- **Rule or category:** `silent-broad-except`; A19, P2
- **Severity:** medium
- **Location:** `claude/statusline.py:24`, `:12`
- **First raised:** review-1 (2026-11-21)
- **Description:** a bare `except:` swallows any error; four sequential git calls run on every refresh.
- **Recommendation:** catch `subprocess.CalledProcessError` and `FileNotFoundError` only; one `git status --porcelain=v2 --branch` call.

### Untested scripts and branches

- **Rule or category:** T1, T2, T3
- **Severity:** medium
- **Location:** `claude/statusline.py`; `claude/skills/todo-review/verify_bodies.py`; `claude/skills/survey/inventory.py:46`, `:182`; `claude/skills/test-log-review/scan.py:46`
- **First raised:** review-1 (2026-11-21)
- **Description:** `statusline.py` and `verify_bodies.py` have no tests; `inventory.main` never runs in a test; the pure parsers have no property tests.
- **Recommendation:** add the missing test files, an end-to-end test of `inventory.main`, and bounded hypothesis tests.

### Untyped `dict` parameters in the status line

- **Rule or category:** `bare-parametric-annotation`
- **Severity:** low
- **Location:** `claude/statusline.py:31`, `:37`, `:45`, `:53`
- **First raised:** review-1 (2026-11-21)
- **Description:** each getter takes `data: dict`.
- **Recommendation:** `dict[str, object]` or a `TypedDict`.

### Duplicated expected list in the survey tests

- **Rule or category:** `literal-duplication`
- **Severity:** low
- **Location:** `claude/skills/survey/tests/test_inventory.py:74`, `:104`
- **First raised:** review-1 (2026-11-21)
- **Description:** two tests spell out the same expected list.
- **Recommendation:** a module constant, or a scoped accept marker.

### Scripts let I/O errors escape as tracebacks

- **Rule or category:** A1
- **Severity:** low
- **Location:** `claude/statusline.py:61`; `claude/skills/survey/inventory.py:57`, `:70`, `:124`, `:149`; `claude/skills/test-log-review/scan.py:61`, `:67`; `claude/skills/todo-review/verify_bodies.py:40`, `:41`
- **First raised:** review-1 (2026-11-21)
- **Description:** no script translates `OSError`, `UnicodeDecodeError` or git failures into a one-line message.
- **Recommendation:** catch them in each `main` and exit non-zero with the path named.

### Pure-prefixed names that do I/O

- **Rule or category:** A9
- **Severity:** low
- **Location:** `claude/skills/survey/inventory.py:61`, `:89`; `claude/skills/test-log-review/scan.py:51`, `:66`
- **First raised:** review-1 (2026-11-21)
- **Description:** `find_repositories`, `is_merged` and `parse_log` read the file system or run git.
- **Recommendation:** rename, or accept with scoped markers.

### Unmemoised merge check per branch

- **Rule or category:** A24
- **Severity:** low
- **Location:** `claude/skills/survey/inventory.py:165`, `:173`
- **First raised:** review-1 (2026-11-21)
- **Description:** `is_merged` runs twice for a branch checked out in a worktree.
- **Recommendation:** compute once per branch.

### Status line trusts the session JSON's shape

- **Rule or category:** Sec2
- **Severity:** low
- **Location:** `claude/statusline.py:32`, `:38`, `:46`, `:49`, `:54`, `:57`, `:61`
- **First raised:** review-1 (2026-11-21)
- **Description:** a `null`, a non-number or empty stdin crashes the script.
- **Recommendation:** type-check each field and drop the part on a mismatch.

### `--glob` can leave the repository

- **Rule or category:** Sec4
- **Severity:** low
- **Location:** `claude/skills/test-log-review/scan.py:59`
- **First raised:** review-1 (2026-11-21)
- **Description:** a `..` in the pattern reads logs outside the repository.
- **Recommendation:** skip matches outside the repository.

### pytest undeclared

- **Rule or category:** D1
- **Severity:** low
- **Location:** `claude/skills/survey/tests/test_inventory.py:7`
- **First raised:** review-1 (2026-11-21)
- **Description:** `pytest` is imported but not declared.
- **Recommendation:** `uv add --dev pytest`.

### Skill reference drifts from three skills

- **Rule or category:** Doc5
- **Severity:** low
- **Location:** `docs/reference/skills.md:9`, `:85`, `:131`
- **First raised:** review-1 (2026-11-21)
- **Description:** `when_to_use` claimed for every skill (paper-pdf-hunter has none); `/specdev` and `/testplan` commit messages wrong.
- **Recommendation:** fix the page or the skill frontmatter, and copy the messages from the skills.

## Recently resolved

| Finding | Severity | Raised in | Resolved in |
|---------|----------|-----------|-------------|

## Recurring patterns

- (none yet: one review)

## Checker changes since the last review

- (none: first review)

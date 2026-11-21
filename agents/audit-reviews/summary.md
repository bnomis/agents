# Audit Summary

**Last updated:** 2026-11-21
**Last review:** review-1
**Total reviews conducted:** 1
**Last script run hit count:** 0 (0 accepted)
**Script version:** e924b332c5c6809821c1635aa7a1d3714064120de0317c733f7f09dfa6b50537

The sweep reads the roots `claude` and `tests`, declared under `[tool.auditme]`
in `pyproject.toml`: the repository has no `src/`, and `bin/` holds no Python.

## Unresolved findings

(none)

## Recently resolved

| Finding | Severity | Raised in | Resolved in |
|---------|----------|-----------|-------------|
| Status line hides every failure and runs git four times per refresh | medium | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Untested scripts and branches | medium | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Untyped `dict` parameters in the status line | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Duplicated expected list in the survey tests | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Scripts let I/O errors escape as tracebacks | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Pure-prefixed names that do I/O | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Unmemoised merge check per branch | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Status line trusts the session JSON's shape | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| `--glob` can leave the repository | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| pytest undeclared | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |
| Skill reference drifts from three skills | low | review-1 (2026-11-21) | review-1 task list (Tasks 1-6), swept 2026-11-21 |

## Recurring patterns

- (none yet: one review)

## Checker changes since the last review

- (none: first review)

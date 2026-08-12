# Counts in prose

A count written into prose is a snapshot in the grammar of a fact:
correct when typed, silently wrong afterwards, and read as authoritative
in between. Nobody notices, because nothing checks it and it was true
once.

**A number in prose is either generated or dropped.**

This applies to `.md` files, docstrings and code comments alike. A
docstring saying "the six sources" rots exactly as fast as a README
saying "82 settings".

## Before typing a number, pick one

### Drop it

Usually the sentence is stronger without. "Every non-test file is
annotated" is an invariant a reader can check; "all 120 non-test files
are annotated" is a measurement that expires. Prefer `every`, `each`,
`no`, `both`, or simply naming the things:

| Decays | Does not |
|--------|----------|
| "all 120 non-test files are annotated" | "every non-test file is annotated" |
| "imports each of the six command submodules" | "imports each command submodule" |
| "none of the five command classes has a consumer" | "no command class has a consumer" |
| "Four of the six sources wrap sync libraries" | "the `a`, `b`, `c` and `d` sources wrap sync libraries" |

The last row is the general move: when a list is short, name its members
instead of counting them. The list is self-counting and cannot disagree
with itself.

### Name the command that produces it

For a figure that genuinely varies, give the command rather than its
output on some past afternoon:

- "run `ruff check --select ANN --statistics`" beats "2483 missing
  annotations (1018 parameter, 1465 return)"
- "run `pytest --collect-only -q`" beats "71 test modules, roughly 1905
  test functions"
- "`uv tree --package docling`" beats "resolves to 124 packages"

The reader gets a live answer, and the document cannot rot.

### Generate it

Only where the magnitude changes what a reader does - whether to skim a
table or read it, whether a dependency is heavy enough to worry about.
Wrap the number in a marker and fill it from the code:

```markdown
These <!--count:env-overridable-->33<!--/count--> settings are the only ones
```

A generator is about sixty lines: import the thing, count it, rewrite
every marker in place, and offer a `--check` mode that reports stale
markers and exits non-zero without writing, so it can gate a commit the
way `ruff format --check` does. Put it in `bin/` with a wrapper script
(see [python/utilities.md](python/utilities.md)).

Keep the set of generated counts small. Each one is a function someone
has to maintain, and most numbers do not earn that.

## Dated measurements are exempt

A number attached to a date is a record, not a claim about the present,
and is the one honest way to keep a figure in prose:

- an audit review recording what it found on the day it ran
- a spec paragraph beginning "measured on `<date>`"
- a benchmark result with the commit it was taken at

**Never regenerate these.** Rewriting a review's figures falsifies the
record. Keep them outside any generator's search path.

If a number matters and cannot be generated, date it.

## Why this rule exists

On one project, every counted claim in every document was found stale in
a single audit: a settings registry described as 82 entries when it held
101, six command submodules when there were ten, 85 test modules when
there were 141. None was wrong when written. Two of the figures had been
copied forward into three separate specs, so the same wrong number was
"confirmed" by repetition.

The damage is not the wrong number. It is that a document demonstrably
stale in its checkable parts teaches the reader to discount its
uncheckable parts too - and the uncheckable parts are the ones carrying
the design rationale.

## Related

- [markdown.md](markdown.md) - formatting conventions for the same files
- [user-guides.md](user-guides.md) - keeping user docs in sync with code

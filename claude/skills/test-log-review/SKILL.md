---
name: test-log-review
description: Review the newest pytest log files of every repository in a workspace for failures and warnings - trace each to its cause with subagents, publish a review page of proposed fixes and decisions, file the approved fixes in each repository's TODO.md and give an implementation order
when_to_use: |
    Use this skill whenever the user mentions:
        - look in the pytest logs for failures and warnings
        - review the test logs
        - what warnings do the test runs show
        - investigate test warnings across the projects
        - turn the test warnings into todo items

allowed_tools: [Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion, Artifact, ArtifactData]
---

# Test log review

Invoke as:
    /test-log-review [root] [--glob PATTERN]

Root defaults to the current directory: a workspace holding several
repositories, or one repository. The pattern defaults to `pytest*.log` at each
repository's root; a project's own rule may name another (and where its logs
come from).

The skill runs in stages, each ending where the user has something to do:

1. scan the logs (scripted);
2. trace every failure and warning to its cause (read-only subagents);
3. re-check the findings that matter, then publish a review page;
4. after the user answers: file the approved fixes in each `TODO.md`;
5. commit on a yes, and give the implementation order.

A project's own rules win where they differ from this skill: when tests may
run, what a probe may load, how its `TODO.md` is shaped, where its reviews
live, and how a change that alters output is versioned.

## Ground rules

- **Read only until the user answers the review.** No edits to code,
  configuration or `TODO.md` before then, and no commits.
- **No test runs.** The logs are the evidence. Another session may be using
  the machine, and a project may allow one run at a time. Short probes
  (`python -c`, a small script in the scratchpad) are fine, within the
  project's limits on what a probe may load or download.
- **Secrets.** Never print environment variables or env files. Repeat this in
  every subagent brief.
- **State with a time.** Every claim about repository state comes from a
  check made for it, with `date -u +%H:%M:%S` in the same command.
- **A subagent's finding is a lead.** Before the review calls something a
  real defect, reproduce it yourself (a probe, or the cited code line). A
  finding outside a subagent's brief is checked, then filed or dropped; say
  which on the page.

## Stage 1: Scan (scripted)

```shell
python3 ~/.claude/skills/test-log-review/scan.py <root> [--glob PATTERN] [--depth N] [--json]
```

For the newest log of each kind in each repository (a kind is the file name
with its timestamp removed, so a full run's log and a correctness run's log
are read separately), it prints pytest's summary line, every `FAILED` and
`ERROR` line, and the warnings summary grouped by category and message. Each
log is marked `INVESTIGATE`, `clean` or `NO TESTS`. Keep the output in the
scratchpad.

- Counts come from pytest's summary line. A grep for "failed" matches log
  lines that passing tests print (a retry message, a test id containing the
  word), so never report a failure from one.
- `NO TESTS` is expected in a repository with no tests; say so in one line.
- Tell the user at once whether anything failed, and which repositories have
  warnings, before the investigation starts.

## Stage 2: Investigate (subagents)

Failures come before warnings. Group the work, keeping to the session's
agent-count guideline:

- **One agent for third-party warnings seen in two or more repositories.**
  Several repositories sharing one dependency's warning would otherwise get
  the same investigation each.
- **One agent per repository with many warnings or any failure**, and one
  per group of the rest. Each is told to skip the shared warnings.

Each brief carries the log paths, the warnings it covers, and this:

```text
Read-only: do not edit files, commit, or run the test suite (another session
may be using the machine). Short probes are fine: <the project's probe
limits, e.g. what must never be loaded or downloaded>. Never print
environment variables or env files.

For each failure or warning group, read the log's warnings summary in full and
report:
- count, and the tests that trigger it;
- origin: the source line that raises it (our code or a dependency's,
  file:line) and our call site that reaches it;
- cause, and whether it signals a real defect in our code (a wrong or silently
  missing value in production output) or only degenerate test data, a test's
  own design, or a dependency's noise. Prove a claimed defect with a probe;
- for a dependency: the installed version, whether a released version fixes
  it (check the registry and release notes, not memory, with dates), whether
  the package's version is recorded or checked in our outputs (an upgrade
  then changes results or refuses saved work), and whether a sibling
  repository already filters or works around it (copy its form);
- options: fix the code, fix the test, assert it with pytest.warns, a narrow
  filterwarnings entry (the last field is the module the warning is raised
  in, not the caller), upgrade, or leave it - each with its consequence;
- whether a fix changes output values, and so needs the project's version
  bump or output-fingerprint step;
- a recommendation with a one-line reason.
```

Relay each agent's headline to the user as it returns.

## Stage 3: Re-check and publish the review

1. **Re-check** every claimed real defect yourself, and any claim a decision
   rests on. Record each re-check, confirmed or dropped, in the review's
   automatic checks.
2. **Write the review document**, where the project's rules put reviews (else
   `agents/reviews/test-logs-N.md` at the root), following the shared
   `reviews.md` rule's order: what is reviewed and how; automatic checks (the
   scan's table and the re-checks); the items; the decisions; an empty
   Answers section. Group the items:
   - **real defects** (change output values), each pointing at its decision;
   - **our code or tests, no output change**, one row per fix with its
     recommendation and whether it needs a version step;
   - **third-party warnings**, one row per warning with the repositories it
     appears in.
   An item whose recommendation is "leave it" stays on the page, so the user
   can flag it.
3. **Only real choices are decisions** (the shared `reviews.md` rule): a fix
   that changes output, an upgrade of a recorded dependency, where a shared
   filter lives, and how approved work is carried out (file it in each
   `TODO.md`, fix the small items now, or write specs). Give each its
   background with dates, what it affects, and each option's consequence.
4. **Publish the page** from `page-template.html` in this directory. Re-read
   the shared `reviews.md` rule from disk first. Copy the template, fill the
   block between the `REVIEW-DATA-START` and `REVIEW-DATA-END` markers
   (`META`, `CHECKS`, `SECTIONS`, `DECISIONS`, `ITEMS`), then:

   ```shell
   node ~/.claude/skills/test-log-review/check-page.js <page.html>
   ```

   It must exit 0. Publish with `capabilities: {db: {}}`, write one probe
   answer with `ArtifactData`, read it back, delete it, and put the page's URL
   in the document's header as `**Review page:** <URL>`. Hand over the page
   URL and the document's absolute path, and stop.

## Stage 4: File the approved fixes

When the user says they have answered:

1. Read the answers back (`ArtifactData` list of `answers`) and copy them into
   the document's Answers section with the date: each decision's option, the
   items flagged, and every comment.
2. A flagged item or a comment that changes a fix is acted on as it says
   before filing. Ask only if it cannot be read as an instruction.
3. Check each repository's `TODO.md` is unchanged and note its branch, with
   the time. If one has uncommitted changes, ask before writing to it.
4. File, through the `todo-add` skill's conventions
   (`~/.claude/skills/todo-add/SKILL.md`,
   `~/.claude/skills/todo-review/conventions.md`), with subagents, one per
   repository or group. Each brief carries every approved finding for its
   repositories (paths, causes, fix directions, the decision's option) and
   says: follow `todo-add`; re-verify each cause in the code and file what
   the code shows; join findings that share a cause (the third-party filters
   of one repository are usually one item); place by the conventions' order,
   never append; write only `TODO.md`; run the repository's checks on it; do
   not commit; report each item's placement and the updated list.
   - An item approved as "leave it" is not filed.
   - A dependency upgrade is filed where the dependency is declared, and each
     repository whose results it changes points at it.
   - An item a decision made unnecessary (a filter replaced by an upgrade) is
     not filed; say so in the document.
5. When a filing agent corrects a claim the review made, record the
   correction in the review document under the Answers, beside what was
   filed. Carry it into any other repository's item that cites it.
6. Check every repository again (`git status --porcelain`, with the time) and
   that each one changed only `TODO.md`. Report what was filed, with the
   corrections, and ask with `AskUserQuestion`, as one yes-or-no question,
   whether to commit: one `docs(todo): ...` commit per repository and one for
   the review document, no push.

## Stage 5: Commit and give the order

On a yes, commit each repository's `TODO.md` and the review document, then
check each repository's state (ahead of its remote by one; name any other
unpushed commit that is not yours). When the user asks for the order, or at
the end, give it in waves, in a table per wave:

- **A change to a shared environment goes alone and first** (a dependency
  upgrade in a venv or lock every repository's tests use): every test run
  after it then uses one environment. Its snapshot comparison runs in each
  repository whose results it changes.
- **One cause per snapshot review.** A fix that changes a repository's output
  snapshots goes after an upgrade that changes the same snapshots, not with
  it.
- A shared library's fix goes before consumer work that relies on it; a spec
  before its code.
- Within a repository, items go in its `TODO.md` order. Different
  repositories run in parallel.
- A machine-wide limit on test runs serialises the heavy runs, not the
  editing: say which lists end in a long run and should not overlap, and
  where the project's batch checkpoints (a full correctness run) fall.

## Do not

- Report a failure from a grep, or a defect no probe or code line confirmed.
- Run the test suite, or a probe that downloads or replaces shared models or
  data.
- Present a choice the project's rules already settle as a decision.
- File anything before the user has answered the review page.
- Commit or push without the user's yes.

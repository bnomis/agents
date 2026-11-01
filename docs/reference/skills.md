# Skills

Each skill is a directory under `claude/skills/<name>/` holding a `SKILL.md`
and any scripts or templates it uses. `bin/install-claude.py` links `claude/`
into `~/.claude/`, so every skill is available in every project as
`~/.claude/skills/<name>/`.

Invoke a skill in Claude Code as `/<name> [args]`, or by asking for what it
does: the `when_to_use` list in each skill's frontmatter names the phrases
that trigger it ("ship it", "add a todo", "audit the code").

Common behaviour:

- The planning, TODO and audit skills check `git status` first and ask
  whether to commit uncommitted changes before touching a file they own.
- They ask before committing, and do not push unless asked. The exceptions
  are `/ship`, whose job is to commit, merge and push, and `/project-setup`,
  which never pushes.
- Steps that change something outside the working tree (deleting branches,
  creating a deploy key, setting a CI secret) are confirmed with the user
  first.
- Questions to the user go through Claude Code's `AskUserQuestion` tool
  where the skill names it.

## Summary

### Planning

| Skill | Invocation | Purpose |
|---|---|---|
| [specdev](#specdev) | `/specdev <spec-name>` | Write, review or update a spec; detect drift from the code |
| [taskdev](#taskdev) | `/taskdev <spec-name-or-path>` | Turn a spec or review into an ordered task list |
| [testplan](#testplan) | `/testplan [scope]` | Find testing gaps and write a test plan |

### TODO workflow

| Skill | Invocation | Purpose |
|---|---|---|
| [todo-add](#todo-add) | `/todo-add [description]` | File one verified, dated finding in `TODO.md`, in order |
| [todo-review](#todo-review) | `/todo-review` | Re-check, consolidate and reorder the whole of `TODO.md` |
| [todo-do](#todo-do) | `/todo-do [item title]` | Do the first (or named) item, or start a spec for it |
| [note-add](#note-add) | `/note-add [note]` | Append a dated, self-explanatory note to `NOTES.md` |

### Git

| Skill | Invocation | Purpose |
|---|---|---|
| [ship](#ship) | `/ship [message hint]` | Commit, merge the branch into `main`, push `main` |
| [cleanup](#cleanup) | `/cleanup [repo-path]` | Delete local branches and worktrees already merged |

### Auditing and setup

| Skill | Invocation | Purpose |
|---|---|---|
| [auditme](#auditme) | `/auditme [scope]` | Scripted and checklist audit of code, specs and docs |
| [project-setup](#project-setup) | `/project-setup new [path]`, `/project-setup adopt [path]` | Install the shared audit hooks, CI gate and project files |

### Other

| Skill | Invocation | Purpose |
|---|---|---|
| [paper-pdf-hunter](#paper-pdf-hunter) | `/paper-pdf-hunter <list> <folder>` | Find and download paper PDFs by driving a browser |

## /specdev {#specdev}

```text
/specdev <SPEC-NAME>
```

With no argument, lists specs from `agents/specs/index.md` and asks which.
The name is slugified (lowercase ASCII alphanumerics, spaces to hyphens,
repeated hyphens collapsed): `"C++ Parser v2.0"` becomes `c-parser-v20`.

- **Reads:** `AGENTS.md`, `README.md`, `agents/specs/index.md`, the spec, and
  the implementation at the spec's module location.
- **New spec:** interviews the user, writes a draft from the template
  (`Version`, `Status: proposed`, `Date`, then Module location, API, Error
  handling, Implementation, Settings, External dependencies), and adds it to
  the index.
- **Existing spec:** runs drift detection against the code when it exists,
  checks the spec against the template and validation criteria, and suggests
  changes. Drift findings are never resolved without the user choosing a
  direction for each one.
- **Stops for:** interview answers; each drift item (update spec, update
  code, or skip); commit.
- **Writes:** `agents/specs/<slug>/spec.md`, `agents/specs/index.md`.
  Commits only the spec file, with a message such as
  `specdev: add error handling section to <slug> spec`.

One spec covers one repository and is self-contained; cross-repository work
is one spec per repository.

## /taskdev {#taskdev}

```text
/taskdev <SPEC-NAME>
/taskdev <SPEC-PATH>
```

An argument containing `/` is a path. A path that is not
`agents/specs/<slug>/spec.md` (an audit review or test plan, for example) is
non-spec input: the slug is the parent directory's name, and tasks cite
**Source** instead of **Spec**.

- **Reads:** the spec and its sibling documents, `agents/tasks/index.md`,
  earlier `agents/tasks/<slug>/tasks-*.md`, and the code under `src/` to mark
  work already done.
- **Writes:** `agents/tasks/<slug>/tasks-N.md` (never overwrites; N
  increments) and `agents/tasks/index.md`.
- **Stops for:** an ambiguous spec (offers `/specdev` first, or proceeds with
  caveats); tasks that need a user decision; review of the list; commit.

Each task carries status, priority, complexity, spec reference, subtasks,
acceptance criteria, notes, and a **Definition of Done** naming the
project's own check commands literally. Per-task checks are scoped to the
changed files; the last task runs the whole-tree lint and the full
affected-tests run, and sets the spec's status to `implemented`. No task
edits another repository.

## /testplan {#testplan}

```text
/testplan                 # every module under src/
/testplan <module-path>   # one module and its tests
/testplan <spec-name>     # a spec's implementation
```

- **Reads:** `AGENTS.md`, the modules in scope and their tests (`src/tests/`),
  earlier plans in `agents/test-plans/`, and `uv run pytest --co -q`.
- **Writes:** `agents/test-plans/plan-N.md` (never overwrites), capped at 20
  recommendations, favouring branching logic, error paths and edge cases.
- **Then:** if there are recommendations, runs
  `/taskdev agents/test-plans/plan-N.md`.
- **Stops for:** commit (`testplan: add plan-N`).

## /todo-add {#todo-add}

```text
/todo-add <description>
/todo-add                 # files the finding just established in the conversation
```

- **Reads:** the project's `TODO.md` convention section (in `AGENTS.md` or
  `CLAUDE.md`), `TODO.md` in full, the tail of `DONE.md`, and the code needed
  to confirm the cause.
- **Writes:** one item in `TODO.md`: a specific `##` title, the dated
  finding (inside the project's accept markers), the cause with `path:line`,
  and a Fix direction. It is inserted in implementation order, never
  appended. A finding that shares a root cause with an open item joins it as
  a `###` finding; one that touches several items is proposed as a
  consolidation first.
- **Stops for:** uncommitted `TODO.md` changes; a proposed consolidation;
  commit (`docs(todo): ...`).

A fix that belongs to another repository is filed in that repository's
`TODO.md`. Conventions shared by the TODO skills are in
`claude/skills/todo-review/conventions.md`; a project's own `TODO.md`
section overrides them.

## /todo-review {#todo-review}

```text
/todo-review
```

- **Reads:** `TODO.md`, `DONE.md`, and the project's specs, task lists,
  reviews, code markers (`TODO`, `FIXME`, expected failures) and recent
  commit bodies, looking for promised work no item records.
- **Proposes**, before any edit: items to move to `DONE.md` with evidence,
  stale premises, missing items, groups sharing a root cause, and the new
  order, shown as a table.
- **Writes**, once confirmed: `TODO.md` reordered and consolidated (original
  bodies kept verbatim under `###`), finished items appended to `DONE.md`
  with a `Done:` line, missing items added, stale premises corrected with a
  dated note.
- **Verifies:** saves `HEAD:TODO.md` to a scratch file first, then runs
  `python3 ~/.claude/skills/todo-review/verify_bodies.py <before> TODO.md
  DONE.md`, which exits non-zero if any original item body is lost or
  altered.
- **Stops for:** uncommitted `TODO.md` changes; the proposal; commit
  (`docs(todo): ...`).

Order, highest first: work-losing defects, blockers, waste, features (each
before what it makes cheaper or safer), then deferred items.

## /todo-do {#todo-do}

```text
/todo-do
/todo-do <item title>
```

Re-checks the item is still open, still true, and not one symptom of a
shared cause (if it is, proposes `/todo-review` and stops). Then sizes it:

| Size | Condition | Action |
|---|---|---|
| Small | One logical change; no artefact, contract or public API change; no spec section rewrite; no paid run or real-data change | Fix on a branch, test first for defects, run the project's checks, move the item to `DONE.md` with a `Done:` line, add dated notes to other items whose `path:line` moved |
| Large | Anything else, or the item says it goes through a spec | Run `/specdev`, stop for spec review, offer `/taskdev`, add a `Spec: ...; tasks: ...` line to the item; it moves to `DONE.md` when the task list finishes |

- **Stops for:** a done or stale item; a shared cause; spec review; a paid
  LLM run (asks for provider and a cost estimate); commit.
- Backs up real project artefacts before a run that rewrites them; a new
  defect found mid-run is filed with `/todo-add`, not fixed in place.

## /note-add {#note-add}

```text
/note-add <the note>
/note-add                 # asks what to note
```

- **Reads:** `NOTES.md` in the repository root (offers to create it), and the
  repository to fill in missing context.
- **Writes:** appends one note to `NOTES.md`:

  ```markdown
  ## <short title>

  Added YYYY-MM-DD. <the note>
  ```

  Adds to an existing note on the same subject instead of duplicating it.
  Never edits other notes.
- **Stops for:** up to a few clarifying questions on what a later reader
  would miss (what, why, where, when, who); a preview with
  add / change / cancel; commit (`docs(notes): <subject>`).

Open work with a cause belongs in `TODO.md`; the skill redirects to
`/todo-add`.

## /ship {#ship}

```text
/ship [commit message hint]
```

1. Inspects `git status`, diffs, branch, worktrees and recent log; stops if
   it sees secrets, build output, large binaries or unrelated changes.
2. Commits by logical change, staging files by name, with conventional
   commit messages; fixes hook failures rather than bypassing them.
3. On a feature branch: fetches, rebases onto `origin/main`, and
   fast-forwards `main` (in the worktree that holds `main`, if another one
   does).
4. Pushes `main`, after `git pull --rebase` if `origin/main` moved. Never
   force-pushes; stops on rejection.
5. Reports the commits, the merge and the push, with repository state stated
   only from a fresh `git fetch` and `git status -sb`.

Feature branches and worktrees are left in place; use `/cleanup`.

## /cleanup {#cleanup}

```text
/cleanup [repo-path]
```

Works on one repository (default: the current one) and all its worktrees;
never changes the remote. It reads only until the plan is approved.

- **Merged** means, against the local default branch or `origin/<default>`:
  ancestry, a rebase merge (`git cherry` shows no `+`), or a squash merge
  (a probe commit of the branch's tree shows no `+`).
- **Removes:** prunable worktrees; clean worktrees whose branch or detached
  `HEAD` is merged; merged local branches. Skips the main worktree, the
  current one, locked or dirty worktrees, and worktrees holding a submodule
  (for which it prints the commands to run by hand).
- **Stops for:** one approval of the plan - all, a named subset, or cancel.
  The plan lists ignored files each worktree removal will delete.
- Never `--force` on worktrees. Uses `git branch -D` only for a branch it
  proved merged by the rebase or squash test.

## /auditme {#auditme}

```text
/auditme [scope] [--category <category>]
```

Scope is empty (specs, `src/`, `bin/`, `docs/`, `AGENTS.md`, `README.md`), a
file path, a spec slug, or the docs. `--category` (`standards`,
`architecture`, `performance`, `security`, `testing`, `dependencies`,
`documentation`) is a debugging aid; a normal audit runs every category.

- **Runs:** the scripted sweep
  `python3 ~/.claude/skills/auditme/checks/audit.py <project-root>`, then a
  fixed checklist applied by one subagent per question across every file in
  scope, then a spec review and re-verification of earlier findings.
- **Refuses to start** while `claude/skills/auditme/requests.md` has open
  checker change requests.
- **Writes:** `agents/audit-reviews/review-N.md`,
  `agents/audit-reviews/summary.md`, `agents/audit-reviews/index.md`, and
  marks shipped tasks done in `agents/tasks/audit-reviews/`.
- **Then:** runs `/taskdev agents/audit-reviews/review-N.md` if there are
  findings.
- **Stops for:** uncommitted changes; commit (`auditme: add review-N`).

The checker, its rules and accept markers are described in
[The checker](../guide/checker.md).

## /project-setup {#project-setup}

```text
/project-setup new [<path>]
/project-setup adopt [<path>]
```

Path defaults to the current repository root. Templates are in
`claude/skills/project-setup/templates/`.

- **`new`:** writes `.pre-commit-config.yaml` (ruff, shellcheck, and the
  `auditme-changed` and `auditme-all` hooks pinned to the shared repository's
  current `main` commit), `.github/workflows/ci.yml`, `AGENTS.md`,
  `CLAUDE.md`, `TODO.md`, `DONE.md` and `claude/rules/README.md`; installs the
  pre-commit and pre-push hooks; then runs the deploy-key steps. Asks before
  overwriting any existing file.
- **`adopt`:** adds the auditme hooks, offers to remove a project-local hook
  doing the same job, and counts unaccepted hits with
  `pre-commit run auditme-all --hook-stage manual --all-files`. At zero hits
  it enables the pre-push stage, adds the CI audit step and runs the
  deploy-key steps; otherwise it files a dated `TODO.md` item instead and
  enables neither gate.
- **Deploy-key steps:** generate an ed25519 key in a temporary directory, add
  the public key as a read-only deploy key on the shared repository, set it
  as the `AGENTS_DEPLOY_KEY` secret on the project, then delete the files.
  The private key is never printed.
- **Stops for:** the project name and test command; each deploy-key and
  secret command; commit. Never pushes.

See [Setup](../setup.md) for the full walk-through.

## /paper-pdf-hunter {#paper-pdf-hunter}

```text
/paper-pdf-hunter <PAPER-LIST> <OUTPUT-FOLDER>
```

Drives a real browser (Claude in Chrome preferred, else Playwright MCP; stops
if neither is connected) to find a PDF for each paper in a Markdown list. It
does not use scholarly APIs.

- **Reads:** the Markdown list in any citation shape, extracting title,
  authors, year, DOI, arXiv ID and URLs.
- **Searches**, stopping at the first verified PDF: arXiv or DOI landing
  page, Google Scholar (including all versions), preprint and repository
  sites, general web search, then public ResearchGate or Academia.edu
  copies. Shadow libraries and paywall bypasses are out of scope.
- **Verifies** each file: `%PDF` header, size, and title on the first pages
  via `pdftotext`.
- **Writes:** `<FirstAuthor>_<Year>_<first-five-title-words>.pdf` (with
  `_preprint` or `_accepted` suffixes, never overwriting) and
  `download_report.md` in the output folder. Output defaults to `./papers/`
  beside the list.
- **Stops for:** a missing list or folder, Chrome's PDF download setting,
  CAPTCHAs (the user solves them), and any login it would have to perform on
  the user's behalf.

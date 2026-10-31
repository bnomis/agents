# Cleanup skill

**Version:** 1.1
**Status:** implemented
**Date:** 2026-10-27

`/cleanup` deletes local branches and worktrees that no longer hold anything
that is not already in the default branch. It exists because feature
branches and worktrees accumulate after `/ship` (which leaves them in place
unless asked) and after squash or rebase merges on the remote, and deleting
them by hand means checking each one for unmerged commits and uncommitted
files first.

The plugin command `commit-commands:clean_gone` already deletes branches
whose upstream is `[gone]`, but it deletes them whether or not they are
merged and removes their worktrees with `--force`, discarding uncommitted
work. `/cleanup` deletes only what it has proved is merged and clean, and
never forces.

## Module location

`claude/skills/cleanup/SKILL.md` - a skill file, no code. It is installed into
`~/.claude/skills/cleanup` by `bin/install-claude.py`, which symlinks each
directory under `claude/skills/`.

## API

Invocation:

```text
/cleanup [<repo-path>]
```

- `<repo-path>`: optional; any path inside the repository to clean. Default:
  the current working directory. The skill resolves it with
  `git -C <repo-path> rev-parse --show-toplevel` and works on that repository
  only, including all of its worktrees.

Frontmatter, matching the other skills in `claude/skills/`:

```yaml
---
name: cleanup
description: Delete local branches and worktrees whose work is already in the default branch
when_to_use: |
    Use this skill whenever the user mentions:
        - clean up branches
        - delete stale branches
        - remove old worktrees
        - cleanup

allowed_tools: [Read, Bash, AskUserQuestion]
---
```

## Definitions

- **Default branch**: `origin/HEAD` with the `origin/` stripped
  (`git symbolic-ref --short refs/remotes/origin/HEAD`); if unset, `main`
  if it exists, else `master`; if neither exists, stop and ask.
- **Merged** (for a commit range): every commit on `<branch>` that is not on
  the default branch is present in the local default branch *or* in
  `origin/<default>`, shown by any of:
  1. ancestry: `git merge-base --is-ancestor <branch> <ref>`;
  2. rebase merge: `git cherry <ref> <branch>` prints no line starting with
     `+`;
  3. squash merge: the branch squashed into one commit,
     `git commit-tree <branch>^{tree} -p $(git merge-base <ref> <branch>) -m cleanup-probe`,
     makes `git cherry <ref> <that commit>` print no line starting with
     `+`. Its output is usually one `-` line, but is empty when the probe
     commit happens to be byte-identical to the squash commit on `<ref>`.
     The probe commit is unreferenced and left for `git gc`.
- **Clean** (for a worktree): `git -C <path> status --porcelain` prints
  nothing (no staged, unstaged or untracked changes) and the worktree is not
  locked.

## Implementation

The skill tells Claude to follow these steps in order. Steps 1-3 only read;
nothing is deleted before step 5.

1. **Refresh**: if the repository has a remote named `origin`,
   `git fetch --prune origin` so that `origin/<default>` is current and
   remote-tracking refs for deleted remote branches go. If the fetch fails
   (offline, auth), say so and continue against the local default branch
   only.
2. **Collect worktrees** from `git worktree list --porcelain`. Classify each
   linked worktree (never the main worktree, never the one Claude is running
   in) as:
   - **prunable**: git marks it `prunable` (its directory is gone);
   - **stale branch**: it has a branch, that branch is merged, and the
     worktree is clean;
   - **stale detached**: detached HEAD, `HEAD` commit is merged, and the
     worktree is clean;
   - **kept**, with the reason: dirty (list the changed paths, up to a
     handful, then "and more"), locked (with the lock reason), branch not
     merged, or holds a submodule (1.1, below).

   (1.1) A worktree **holds a submodule** when its git directory
   (`git -C <path> rev-parse --absolute-git-dir`) contains a `modules`
   directory. Git refuses to remove such a worktree without `--force`, even
   once the submodule's checkout is cleared, so it is never removable here.
   When it is otherwise clean and its branch merged, it is kept with that
   reason, and the plan gives the user the commands to run themselves:
   `git worktree remove --force <path>`, then `git branch -d <branch>`.
3. **Collect branches** from
   `git for-each-ref --format='%(refname:short)' refs/heads`. Exclude the
   default branch, the current branch of the worktree Claude runs in, and
   any branch checked out in a worktree classified as kept or in the main
   worktree. Classify each remaining branch as **stale** if merged, else
   **kept** with the reason "not merged" and its count of unmerged commits
   from `git cherry`. A kept branch whose upstream is gone is labelled so,
   since it is the case `clean_gone` would have deleted.
4. **Show the plan** as one list grouped as: worktrees to remove (path,
   branch or commit, reason), branches to delete (name, which merge test
   passed, last commit date and subject), and kept items with reasons. For
   each worktree to remove, also list its ignored top-level entries
   (`git -C <path> status --porcelain --ignored`, lines starting `!!`),
   because `git worktree remove` deletes ignored files such as virtual
   environments and generated data. Then ask once with AskUserQuestion:
   delete all listed, choose a subset, or cancel. If nothing is stale, say
   so and stop.
5. **Delete**, worktrees first so their branches are free:
   - prunable worktrees: `git worktree prune`;
   - other worktrees: `git worktree remove <path>`, never `--force`;
   - branches: `git branch -d <name>`; if git refuses because the branch is
     not an ancestor of `HEAD` or its upstream (the rebase and squash cases),
     `git branch -D <name>`, which is allowed only for a branch this run
     proved merged in step 3.
6. **Report**: re-run `git worktree list` and `git branch -vv` and show what
   was removed, what was kept and why, and any step that failed. Do not
   report from the plan; report from the re-run.

The remote is never changed: no `git push --delete`.

(1.1) `git submodule deinit` is never run in a linked worktree to get past a
refusal. A submodule's registration lives in the configuration every
worktree shares, so deinit there unregisters it in the main checkout too,
and the worktree stays unremovable.

## Error handling

- Not a git repository: stop and say so.
- No default branch found (step "Default branch" above): stop and ask the
  user which branch is the default.
- `git fetch` fails: report the error, continue with the local default
  branch only, and say in the plan that remote merges were not checked.
- `git worktree remove` refuses (a file changed since step 2): keep the
  worktree and its branch, report git's message, carry on with the rest.
- `git branch -d`/`-D` fails: report git's message, carry on.
- The user cancels at step 4: delete nothing and say so.

## Settings

None. The default branch, remote name (`origin`) and repository come from
git and the optional argument; there is no age threshold because only
merged work is deleted.

## Testing

A skill has no unit tests. Verify by hand in a throwaway repository under
the scratchpad directory, with a bare repository as `origin`, containing:

- a branch fast-forward merged into `main` (deleted);
- a branch rebase-merged (deleted, via `git cherry`);
- a branch squash-merged (deleted, via the squash test);
- an unmerged branch whose upstream is gone (kept, labelled);
- a clean worktree on a merged branch (removed with its branch);
- a dirty worktree on a merged branch (both kept);
- a locked worktree (kept);
- a worktree whose directory was deleted (pruned);
- a clean detached worktree at a commit in `main` (removed);
- (1.1) a clean worktree on a merged branch with an initialised submodule
  (kept, with the `--force` commands for the user).

Run `/cleanup` there, accept all, and check the result with
`git branch` and `git worktree list`.

## External dependencies

- git, with `git worktree` and `git cherry` (any git from the last several
  years has both).
- No plugin dependency; `commit-commands:clean_gone` is unrelated and can
  stay installed.

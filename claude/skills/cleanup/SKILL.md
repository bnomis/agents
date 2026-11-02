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

# Cleanup

Invoke as:
    /cleanup [repo-path]

Deletes local branches and worktrees that hold nothing the default branch
does not already have. Deletes only what it has proved merged and clean,
and never forces. Works on one repository and all of its worktrees; the
remote is never changed.

`repo-path` is any path inside the repository; default is the current
directory. Resolve it with `git -C <repo-path> rev-parse --show-toplevel`
and run every command below with `git -C <that path>`. If it is not a git
repository, stop and say so.

Steps 1-4 only read. Nothing is deleted before step 5.

## Definitions

- **Default branch**: `git symbolic-ref --short refs/remotes/origin/HEAD`
  with `origin/` stripped; if unset, `main` if it exists, else `master`. If
  neither exists, stop and ask the user which branch is the default.
- **Refs**: the local default branch, and `origin/<default>` if it exists.
- **Merged**: a branch or commit `<x>` is merged if, for at least one ref
  `<ref>`, any of these holds:
  1. ancestry: `git merge-base --is-ancestor <x> <ref>` exits 0;
  2. rebase merge: `git cherry <ref> <x>` prints no line starting with `+`;
  3. squash merge: with
     `p=$(git commit-tree '<x>^{tree}' -p "$(git merge-base <ref> <x>)" -m cleanup-probe)`,
     `git cherry <ref> "$p"` prints no line starting with `+`. The output
     is usually one `-` line, and empty when the probe happens to be
     identical to the squash commit; both mean merged. The probe commit is
     unreferenced and left for `git gc`.
  Record which test passed; the plan shows it.
- **Clean**: `git -C <path> status --porcelain` prints nothing and the
  worktree is not locked.

Test each pipeline by its output, not its exit status (`pipefail` is on).

## Workflow

1. **Refresh**: if `git remote` lists `origin`, run
   `git fetch --prune origin`. If it fails, report the error, use the local
   default branch as the only ref, and say in the plan that remote merges
   were not checked.

2. **Collect worktrees** from `git worktree list --porcelain`. Skip the
   main worktree (the first entry) and the worktree Claude is running in
   (`git rev-parse --show-toplevel` from the working directory). Classify
   each other one:
   - **prunable**: the entry has a `prunable` line (its directory is gone);
   - **stale branch**: clean, and its branch is merged;
   - **stale detached**: clean, detached, and its `HEAD` commit is merged;
   - **kept**, with the reason: locked (give the lock reason), dirty (list
     a few changed paths, then "and N more"), branch not merged, or holds a
     submodule (below).

   A worktree **holds a submodule** when its git directory
   (`git -C <path> rev-parse --absolute-git-dir`) contains a `modules`
   directory. Git refuses to remove such a worktree without `--force`, even
   once the submodule's checkout is cleared, so it is never removable here.
   When it is otherwise clean and its branch merged, keep it with that
   reason and give the user the commands to run themselves:
   `git worktree remove --force <path>`, then `git branch -d <branch>`.

3. **Collect branches** from
   `git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads`.
   Exclude the default branch, the current branch of the worktree Claude is
   in, and any branch checked out in the main worktree or in a kept
   worktree. Classify each remaining branch:
   - **stale** if merged;
   - **kept** otherwise, with "not merged" and the count of `+` lines from
     `git cherry <default> <branch>`. If its upstream is `[gone]`, say so:
     these are the branches `commit-commands:clean_gone` would delete.

4. **Show the plan**, grouped:
   - worktrees to remove: path, branch or short commit, reason; and its
     ignored top-level entries (lines starting `!!` in
     `git -C <path> status --porcelain --ignored`), because
     `git worktree remove` deletes ignored files such as virtual
     environments and generated data;
   - branches to delete: name, the merge test that passed, last commit date
     and subject (`git log -n 1 --format='%cs %s' <branch>`);
   - kept worktrees and branches, each with its reason.

   If nothing is to be removed, say so and stop. Otherwise ask once with
   AskUserQuestion: delete everything listed, choose a subset (then ask
   which, by name), or cancel. On cancel, delete nothing and say so.

5. **Delete** what the user approved, worktrees first so their branches
   are free:
   - prunable worktrees: `git worktree prune`;
   - other worktrees: `git worktree remove <path>`. Never `--force`. If git
     refuses (something changed since step 2), keep the worktree and its
     branch, report git's message, and carry on;
   - branches: `git branch -d <name>`. If git refuses with "not fully
     merged" (the rebase and squash cases), use `git branch -D <name>`,
     allowed only for a branch step 3 proved merged. Report any other
     failure and carry on.

   Never `git push --delete`, and never delete anything not in the plan.
   Never run `git submodule deinit` in a linked worktree to get past a
   refusal: the submodule's registration lives in the configuration every
   worktree shares, so it unregisters the submodule in the main checkout
   too, and the worktree stays unremovable.

6. **Report** from a fresh look, not from the plan: run
   `git worktree list` and `git branch -vv`, then say what was removed,
   what was kept and why, and any step that failed.

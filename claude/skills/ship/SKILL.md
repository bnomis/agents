---
name: ship
description: Commit the work in progress, merge it to main and push main
when_to_use: |
    Use this skill whenever the user mentions:
        - commit, merge to main and push
        - merge to main and push
        - ship it

allowed_tools: [Read, Bash, Glob, Grep, AskUserQuestion]
---

# Ship

Invoke as:
    /ship [commit message hint]

Commits the uncommitted work, merges the current branch into `main` and
pushes `main`. Follow [git-conventions.md](../../rules/git-conventions.md)
for commit messages and hooks.

## Workflow

1. **Look** before touching anything:
   `git status`, `git diff`, `git diff --staged`, `git branch --show-current`,
   `git worktree list`, `git log -n 5 --oneline`.
   Stop and ask if you see files that look unintended (secrets, build
   output, large binaries, scratch files) or changes unrelated to this
   session's work.

2. **Commit** if there is anything to commit.
   - Split into one commit per logical change; do not bundle a refactor
     with feature work.
   - Stage files by name, not `git add -A`.
   - Message per the conventions: `type(scope): subject`, 50 characters or
     fewer, imperative, with a body only when the why is not obvious.
     Use the hint argument if given. End with the attribution lines the
     session asks for.
   - If a pre-commit hook fails, fix the cause and commit again. Never
     `--no-verify`. If a hook reformatted files, stage them and commit
     again rather than amending.

3. **Merge** into `main`.
   - Already on `main`: skip to step 4.
   - On a feature branch: `git fetch origin`, rebase the branch onto
     `origin/main`, then `git switch main` and fast-forward it
     (`git merge --ff-only <branch>`). This leaves the working tree on
     `main` after the merge. If `main` is checked out in another worktree,
     git will not check it out here: run the merge there with
     `git -C <that path>` and stay on the branch in this one, saying so in
     the report.
   - On a rebase conflict, resolve it only when the right answer is
     obvious from both sides; otherwise abort the rebase and ask.

4. **Push** `main`.
   - `git pull --rebase origin main` first if `origin/main` has moved, then
     `git push origin main`.
   - Never force-push `main`. If the push is rejected, stop and report.

5. **Tidy**: check with `git branch --show-current` that this worktree is
   on `main` (unless `main` lives in another worktree, as above). Leave the
   feature branch and any worktree in place unless the user asked to delete
   them.

6. **Report** in a few lines: the commits made (hash and subject), the
   branch merged, and the push result. If any step was skipped or failed,
   say so plainly.

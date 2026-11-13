"""Inventory every repository under a root: state, branches, worktrees, open plans.

Usage:
    python3 inventory.py [ROOT] [--depth N]

Finds the git repositories at ROOT and below it (to --depth levels, default
2), skipping worktrees, virtual environments and dependency directories. For
each one it prints, as Markdown:

- the branch line of `git status -sb` and the count of changed paths;
- each extra worktree: its branch, whether it is locked, its changed paths,
  and whether its commits are all in the default branch;
- each local branch other than the default: commits ahead of and behind the
  default branch, and whether it is merged (by ancestry, or by `git cherry`
  finding every commit's patch already there, as after a rebase merge);
- each task list under `agents/tasks/` with a task status that is not
  done, complete or superseded, unless the list's own header (above its
  first `## ` heading) carries a `**Superseded:**` line; a list with no
  status at all is reported when any of its checkboxes is unticked;
- each spec `agents/specs/<name>/spec.md` whose first status is not
  implemented, done, superseded, archived, frozen or a historical record, with
  whether it has a task-list directory of the same name.

A status is read from a `**Status:** <value>` line or from a table row whose
first cell is `**Status**`: `| **Status** | <value> |`.

It reads only; it changes nothing. A squash-merged branch shows as unmerged:
`/cleanup` has the stronger test.
"""

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

SKIP_DIRS = frozenset({'.claude', '.git', '.tox', '.venv', '__pycache__', 'node_modules', 'site-packages', 'venv'})
STATUS_RE = re.compile(r'^(?:\*\*Status:\*\*\s*(?P<line>.*)|\|\s*\*\*Status\*\*\s*\|(?P<cell>[^|]*)\|.*)$')
CHECKBOX_RE = re.compile(r'^\s*[-*+]\s+\[(?P<mark>[ xX])\]\s')
DONE_TASK_RE = re.compile(r'^(done|complete|superseded)', re.IGNORECASE)
SUPERSEDED_LIST_RE = re.compile(r'^\*\*Superseded:\*\*')
DONE_SPEC_RE = re.compile(r'implemented|done|superseded|historical|complete|index|archived|frozen', re.IGNORECASE)


def statuses(text_lines: list[str]) -> list[str]:
    """Every status in `text_lines`, from `**Status:**` lines and `| **Status** |` table rows, in order."""
    found: list[str] = []
    for match in map(STATUS_RE.match, text_lines):
        if match:
            found.append((match.group('line') if match.group('line') is not None else match.group('cell')).strip())
    return found


def git(repo: pathlib.Path, *args: str) -> str:
    """Run git in `repo` and return its stripped output ('' on failure)."""
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ''


def find_repositories(root: pathlib.Path, depth: int) -> list[pathlib.Path]:
    """Every repository whose top level is `root` or a directory below it, to `depth` levels."""
    found: list[pathlib.Path] = []

    def walk(directory: pathlib.Path, level: int) -> None:
        if (directory / '.git').exists():
            found.append(directory)
        if level >= depth:
            return
        for child in sorted(directory.iterdir()):
            if child.is_dir() and not child.is_symlink() and child.name not in SKIP_DIRS:
                walk(child, level + 1)

    walk(root, 0)
    return found


def default_branch(repo: pathlib.Path) -> str:
    """The branch `origin/HEAD` names, else `main` or `master`, whichever exists."""
    head = git(repo, 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD')
    if head:
        return head.split('/', 1)[1]
    for name in ('main', 'master'):
        if git(repo, 'rev-parse', '--verify', '--quiet', name):
            return name
    return git(repo, 'branch', '--show-current')


def is_merged(repo: pathlib.Path, ref: str, base: str) -> bool:
    """True when every commit of `ref` is in `base`, by ancestry or by patch."""
    tip = git(repo, 'rev-parse', ref)
    if tip and git(repo, 'merge-base', base, ref) == tip:
        return True
    cherry = git(repo, 'cherry', base, ref)
    return bool(cherry) and not any(line.startswith('+') for line in cherry.splitlines())


def changed_paths(path: pathlib.Path) -> int:
    """How many paths `git status --porcelain` lists in the worktree at `path`."""
    return len(git(path, 'status', '--porcelain').splitlines())


def worktrees(repo: pathlib.Path) -> list[dict[str, str]]:
    """Every worktree except the main one, as parsed from `git worktree list --porcelain`."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in git(repo, 'worktree', 'list', '--porcelain').splitlines() + ['']:
        if not line:
            if current:
                entries.append(current)
            current = {}
            continue
        key, _, value = line.partition(' ')
        current[key] = value
    return entries[1:]


def open_task_lists(repo: pathlib.Path) -> list[str]:
    """Task lists with a status that is not done, or with no status and an unticked box, as 'path: progress'."""
    lines: list[str] = []
    for path in sorted((repo / 'agents' / 'tasks').glob('**/*.md')):
        if path.name == 'index.md':
            continue
        text_lines = path.read_text(encoding='utf-8').splitlines()
        header = text_lines[: next((i for i, line in enumerate(text_lines) if line.startswith('## ')), len(text_lines))]
        if any(SUPERSEDED_LIST_RE.match(line) for line in header):
            continue
        found = statuses(text_lines)
        if not found:
            marks = [m.group('mark') for m in map(CHECKBOX_RE.match, text_lines) if m]
            ticked = sum(mark != ' ' for mark in marks)
            if ticked < len(marks):
                lines.append(f'{path.relative_to(repo)}: {ticked}/{len(marks)} boxes ticked; no status lines')
            continue
        open_ = [status for status in found if not DONE_TASK_RE.match(status)]
        if open_:
            kinds = sorted({status.split()[0].lower() if status else '(empty)' for status in open_})
            done = len(found) - len(open_)
            lines.append(f'{path.relative_to(repo)}: {done}/{len(found)} done; open: {", ".join(kinds)}')
    return lines


def open_specs(repo: pathlib.Path) -> list[str]:
    """Specs not marked implemented, each with whether it has a task-list directory."""
    lines: list[str] = []
    tasks = repo / 'agents' / 'tasks'
    for path in sorted((repo / 'agents' / 'specs').glob('*/spec.md')):
        name = path.parent.name
        status = next(iter(statuses(path.read_text(encoding='utf-8').splitlines())), '')
        if DONE_SPEC_RE.search(status):
            continue
        task_note = 'has a task list' if (tasks / name).is_dir() else 'no task list'
        lines.append(f'{path.relative_to(repo)}: status "{status or "none"}"; {task_note}')
    return lines


def report(repo: pathlib.Path, root: pathlib.Path) -> list[str]:
    """The Markdown section for one repository."""
    base = default_branch(repo)
    out = [f'## {repo.relative_to(root) if repo != root else "."}', '']
    out.append(f'- status: `{git(repo, "status", "-sb").splitlines()[0]}`, {changed_paths(repo)} changed paths')
    for entry in worktrees(repo):
        branch = entry.get('branch', '').removeprefix('refs/heads/') or f'detached {entry.get("HEAD", "")[:8]}'
        ref = entry.get('branch') or entry.get('HEAD', '')
        merged = 'merged' if base and is_merged(repo, ref, base) else 'UNMERGED'
        locked = ', LOCKED' if 'locked' in entry else ''
        out.append(f'- worktree `{entry["worktree"]}` [{branch}]: {merged}, {changed_paths(pathlib.Path(entry["worktree"]))} changed paths{locked}')
    for branch in git(repo, 'branch', '--format=%(refname:short)').splitlines():
        if branch == base:
            continue
        ahead = git(repo, 'rev-list', '--count', f'{base}..{branch}')
        behind = git(repo, 'rev-list', '--count', f'{branch}..{base}')
        merged = 'merged' if is_merged(repo, branch, base) else 'UNMERGED'
        last = git(repo, 'log', '-1', '--format=%cs %s', branch)
        out.append(f'- branch `{branch}`: +{ahead} -{behind}, {merged} | {last}')
    out.extend(f'- open task list: {line}' for line in open_task_lists(repo))
    out.extend(f'- spec: {line}' for line in open_specs(repo))
    out.append('')
    return out


def main(argv: list[str]) -> int:
    """Print the inventory of every repository under the root."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('root', nargs='?', default='.', type=pathlib.Path)
    parser.add_argument('--depth', type=int, default=2)
    options = parser.parse_args(argv)
    root = options.root.resolve()
    repos = find_repositories(root, options.depth)
    if not repos:
        print(f'no git repository at or below {root}', file=sys.stderr)
        return 1
    now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    lines = [f'# Inventory of {root}', '', f'Taken at {now}. Fetch first if remote state matters.', '']
    for repo in repos:
        lines.extend(report(repo, root))
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

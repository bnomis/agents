"""Tests of the survey skill's inventory script, against throwaway repositories."""

import pathlib
import subprocess
import sys

import hypothesis
import hypothesis.strategies
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import inventory  # noqa: E402

PROBE_OPEN_LISTS = ['agents/tasks/probe/tasks-1.md: 1/2 done; open: todo']


def run(repo: pathlib.Path, *args: str) -> None:
    """Run git in `repo`, failing the test on error."""
    subprocess.run(
        ['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
        check=True,
        capture_output=True,
    )


def commit(repo: pathlib.Path, name: str, text: str) -> None:
    """Write `name` and commit it."""
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    run(repo, 'add', name)
    run(repo, 'commit', '-m', f'add {name}')


@pytest.fixture
def repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A repository on `main` with one commit, inside a workspace root."""
    path = tmp_path / 'pkg'
    path.mkdir()
    run(path, 'init', '-b', 'main')
    commit(path, 'README.md', 'probe\n')
    return path


def test_finds_nested_repositories_and_skips_worktrees(tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    run(repo, 'worktree', 'add', '-b', 'side', str(repo / '.claude' / 'worktrees' / 'side'))

    assert inventory.scan_repositories(tmp_path, 2) == [repo]


def test_branch_merged_by_ancestry_and_unmerged(repo: pathlib.Path) -> None:
    run(repo, 'branch', 'old')
    run(repo, 'checkout', '-b', 'new')
    commit(repo, 'x.txt', 'x\n')
    run(repo, 'checkout', 'main')

    assert inventory.branch_is_merged(repo, 'old', 'main')
    assert not inventory.branch_is_merged(repo, 'new', 'main')


def test_branch_merged_by_patch_after_cherry_pick(repo: pathlib.Path) -> None:
    run(repo, 'checkout', '-b', 'picked')
    commit(repo, 'y.txt', 'y\n')
    run(repo, 'checkout', 'main')
    commit(repo, 'z.txt', 'z\n')
    run(repo, 'cherry-pick', 'picked')

    assert inventory.branch_is_merged(repo, 'picked', 'main')


def test_open_task_list_is_reported_and_superseded_one_is_not(repo: pathlib.Path) -> None:
    tasks = repo / 'agents' / 'tasks'
    (tasks / 'probe').mkdir(parents=True)
    (tasks / 'probe' / 'tasks-1.md').write_text('# Tasks\n\n## Task 1\n\n**Status:** done\n\n## Task 2\n\n**Status:** todo\n', encoding='utf-8')
    (tasks / 'probe' / 'tasks-0.md').write_text('# Tasks\n\n**Superseded:** by tasks-1.md\n\n## Task 1\n\n**Status:** todo\n', encoding='utf-8')

    assert inventory.open_task_lists(repo) == PROBE_OPEN_LISTS


def test_spec_status(repo: pathlib.Path) -> None:
    specs = repo / 'agents' / 'specs'
    for name, status in [('built', 'implemented'), ('pending', 'approved 2026-01-01'), ('bare', None)]:
        (specs / name).mkdir(parents=True)
        header = f'**Status:** {status}\n' if status else ''
        (specs / name / 'spec.md').write_text(f'# Spec\n\n{header}', encoding='utf-8')
    (repo / 'agents' / 'tasks' / 'pending').mkdir(parents=True)

    assert inventory.open_specs(repo) == [
        'agents/specs/bare/spec.md: status "none"; no task list',
        'agents/specs/pending/spec.md: status "approved 2026-01-01"; has a task list',
    ]


def test_frozen_spec_is_finished(repo: pathlib.Path) -> None:
    specs = repo / 'agents' / 'specs'
    (specs / 'probe').mkdir(parents=True)
    (specs / 'probe' / 'spec.md').write_text('# Spec\n\n**Status:** Frozen - kept as a record\n', encoding='utf-8')

    assert inventory.open_specs(repo) == []


def test_task_list_status_in_a_table_row_is_read(repo: pathlib.Path) -> None:
    tasks = repo / 'agents' / 'tasks' / 'probe'
    tasks.mkdir(parents=True)
    (tasks / 'tasks-1.md').write_text('# Tasks\n\n## Task 1\n\n| **Status** | done |\n\n## Task 2\n\n| **Status** | todo |\n', encoding='utf-8')

    assert inventory.open_task_lists(repo) == PROBE_OPEN_LISTS


def test_checkbox_only_task_list_is_reported_when_a_box_is_unticked(repo: pathlib.Path) -> None:
    tasks = repo / 'agents' / 'tasks' / 'probe'
    tasks.mkdir(parents=True)
    (tasks / 'tasks-1.md').write_text('# Tasks\n\n## Task 1\n\n- [x] one\n- [ ] two\n', encoding='utf-8')
    (tasks / 'tasks-2.md').write_text('# Tasks\n\n## Task 1\n\n- [x] one\n- [X] two\n', encoding='utf-8')

    assert inventory.open_task_lists(repo) == ['agents/tasks/probe/tasks-1.md: 1/2 boxes ticked; no status lines']


def test_spec_status_in_a_table_row(repo: pathlib.Path) -> None:
    specs = repo / 'agents' / 'specs'
    for name, status in [('built', 'Implemented'), ('draft', 'Draft'), ('old', 'Archived - replaced by built')]:
        (specs / name).mkdir(parents=True)
        (specs / name / 'spec.md').write_text(f'# Spec\n\n| Field | Value |\n|---|---|\n| **Status** | {status} |\n', encoding='utf-8')

    assert inventory.open_specs(repo) == ['agents/specs/draft/spec.md: status "Draft"; no task list']


def test_report_flags_locked_unmerged_worktree(tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    worktree = repo / '.claude' / 'worktrees' / 'side'
    run(repo, 'worktree', 'add', '-b', 'side', str(worktree))
    commit(worktree, 'w.txt', 'w\n')
    run(repo, 'worktree', 'lock', str(worktree))

    lines = inventory.report(repo, tmp_path)

    assert any('[side]: UNMERGED, 0 changed paths, LOCKED' in line for line in lines)
    assert any(line.startswith('- branch `side`: +1 -0, UNMERGED') for line in lines)


def test_branch_checked_out_in_a_worktree_is_merge_checked_once(tmp_path: pathlib.Path, repo: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run(repo, 'worktree', 'add', '-b', 'side', str(repo / '.claude' / 'worktrees' / 'side'))
    calls: list[tuple[str, ...]] = []
    real_git = inventory.git

    def counting_git(path: pathlib.Path, *args: str) -> str:
        calls.append(args)
        return real_git(path, *args)

    monkeypatch.setattr(inventory, 'git', counting_git)

    inventory.report(repo, tmp_path)

    assert sum(args[0] == 'merge-base' for args in calls) == 1


def test_main_prints_heading_and_repository_section(tmp_path: pathlib.Path, repo: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert inventory.main([str(tmp_path)]) == 0

    out = capsys.readouterr().out
    assert out.startswith(f'# Inventory of {tmp_path.resolve()}')
    assert '## pkg' in out


def test_main_without_a_repository_exits_1(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert inventory.main([str(tmp_path)]) == 1

    assert 'no git repository at or below' in capsys.readouterr().err


def test_main_with_an_unreadable_task_list_names_the_path(repo: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    tasks = repo / 'agents' / 'tasks'
    tasks.mkdir(parents=True)
    bad = tasks / 'bad.md'
    bad.write_bytes(b'\xff\xfe not utf-8 \x80\n')

    assert inventory.main([str(repo)]) == 1

    assert str(bad) in capsys.readouterr().err


@hypothesis.settings(max_examples=50, deadline=None)
@hypothesis.given(
    hypothesis.strategies.lists(hypothesis.strategies.sampled_from(['todo', 'in-progress', 'done', 'blocked']), max_size=8), hypothesis.strategies.booleans()
)
def test_statuses_yields_each_status_in_order(words: list[str], as_table: bool) -> None:
    lines = [f'| **Status** | {w} |' if as_table else f'**Status:** {w}' for w in words]
    interleaved = [x for line in lines for x in (line, 'prose')]

    assert inventory.statuses(interleaved) == words

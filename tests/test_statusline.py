"""Tests for claude/statusline.py, the Claude Code status line command."""

import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / 'claude' / 'statusline.py'
module_spec = importlib.util.spec_from_file_location('statusline', SCRIPT)
assert module_spec is not None
assert module_spec.loader is not None
statusline = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(statusline)

GREEN = '\033[32m'
RESET = '\033[0m'
YELLOW = '\033[33m'


def make_stub_git(tmp_path: pathlib.Path, stdout: str = '', exit_code: int = 0) -> pathlib.Path:
    """A `git` that records each call's arguments and prints `stdout`."""
    stub_dir = tmp_path / 'stub'
    stub_dir.mkdir()
    record = tmp_path / 'calls.txt'
    stub = stub_dir / 'git'
    stub.write_text(
        '#!/usr/bin/env python3\n'
        'import sys\n'
        f'open({str(record)!r}, "a").write(" ".join(sys.argv[1:]) + "\\n")\n'
        f'sys.stdout.write({stdout!r})\n'
        f'sys.exit({exit_code})\n'
    )
    stub.chmod(0o755)
    return stub_dir


def with_path(monkeypatch: pytest.MonkeyPatch, stub_dir: pathlib.Path) -> None:
    monkeypatch.setenv('PATH', f'{stub_dir}{os.pathsep}{os.environ["PATH"]}')


def test_model_present():
    assert statusline.get_model({'model': {'display_name': 'Opus'}}) == 'Opus'


@pytest.mark.parametrize('data', [{}, {'model': None}, {'model': {}}, {'model': {'display_name': 3}}, {'model': 'x'}])
def test_model_absent_or_malformed(data):
    assert statusline.get_model(data) == ''


def test_directory_present():
    assert statusline.get_directory({'workspace': {'current_dir': '/a/b'}}) == 'cwd: /a/b'


@pytest.mark.parametrize(
    'data',
    [{}, {'workspace': None}, {'workspace': {'current_dir': ''}}, {'workspace': {'current_dir': None}}, {'workspace': {'current_dir': 4}}],
)
def test_directory_absent_or_malformed(data):
    assert statusline.get_directory(data) == ''


def test_context_window_present():
    assert statusline.get_context_window({'context_window': {'used_percentage': 42.9}}) == 'ctx: 42%'


@pytest.mark.parametrize('value', [None, 0, 0.0, 'n/a', '5', True, [1]])
def test_context_window_zero_or_non_number(value):
    assert statusline.get_context_window({'context_window': {'used_percentage': value}}) == ''


@pytest.mark.parametrize('data', [{}, {'context_window': None}, {'context_window': {}}])
def test_context_window_missing(data):
    assert statusline.get_context_window(data) == ''


def test_rate_present():
    assert statusline.get_rate_percentage({'rate_limits': {'five_hour': {'used_percentage': 7}}}) == '5h: 7%'


@pytest.mark.parametrize(
    'data',
    [
        {},
        {'rate_limits': None},
        {'rate_limits': {'five_hour': None}},
        {'rate_limits': {'five_hour': {}}},
        {'rate_limits': {'five_hour': {'used_percentage': 0}}},
        {'rate_limits': {'five_hour': {'used_percentage': 'high'}}},
    ],
)
def test_rate_absent_or_malformed(data):
    assert statusline.get_rate_percentage(data) == ''


def test_git_status_with_staged_and_modified_files(tmp_path, monkeypatch):
    porcelain = (
        '# branch.oid abc\n# branch.head main\n'
        '1 M. N... 100644 100644 100644 a b one.py\n'
        '1 .M N... 100644 100644 100644 a b two.py\n'
        '2 R. N... 100644 100644 100644 a b R100 new.py\told.py\n'
        '? untracked.py\n'
    )
    with_path(monkeypatch, make_stub_git(tmp_path, porcelain))
    assert statusline.git_status() == f'git: main{GREEN}+2{RESET}{YELLOW}~1{RESET}'
    assert (tmp_path / 'calls.txt').read_text().splitlines() == ['status --porcelain=v2 --branch']


def test_git_status_clean_tree(tmp_path, monkeypatch):
    with_path(monkeypatch, make_stub_git(tmp_path, '# branch.oid abc\n# branch.head feat/x\n'))
    assert statusline.git_status() == 'git: feat/x'


def test_git_status_detached_head_clean(tmp_path, monkeypatch):
    with_path(monkeypatch, make_stub_git(tmp_path, '# branch.head (detached)\n'))
    assert statusline.git_status() == ''


def test_git_status_not_a_repository(tmp_path, monkeypatch):
    with_path(monkeypatch, make_stub_git(tmp_path, exit_code=128))
    assert statusline.git_status() == ''


def test_git_status_git_missing(tmp_path, monkeypatch):
    monkeypatch.setenv('PATH', str(tmp_path))
    assert statusline.git_status() == ''


def test_git_status_in_a_real_repository(tmp_path, monkeypatch):
    repo = tmp_path / 'repo'
    repo.mkdir()
    env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull}
    for args in (['init', '-b', 'main'], ['config', 'user.email', 'a@b.c'], ['config', 'user.name', 'n']):
        subprocess.run(['git', *args], cwd=repo, check=True, env=env, capture_output=True)
    (repo / 'a').write_text('1')
    (repo / 'b').write_text('1')
    subprocess.run(['git', 'add', '.'], cwd=repo, check=True, env=env)
    subprocess.run(['git', 'commit', '-m', 'x'], cwd=repo, check=True, env=env, capture_output=True)
    (repo / 'a').write_text('2')
    (repo / 'b').write_text('2')
    subprocess.run(['git', 'add', 'a'], cwd=repo, check=True, env=env)
    monkeypatch.chdir(repo)
    assert statusline.git_status() == f'git: main{GREEN}+1{RESET}{YELLOW}~1{RESET}'


def run_script(stdin: str, tmp_path: pathlib.Path) -> subprocess.CompletedProcess[str]:
    stub_dir = make_stub_git(tmp_path, exit_code=128)
    env = {**os.environ, 'PATH': f'{stub_dir}{os.pathsep}{os.environ["PATH"]}'}
    return subprocess.run([sys.executable, str(SCRIPT)], input=stdin, capture_output=True, text=True, env=env, check=False)


def test_script_prints_the_joined_parts(tmp_path):
    payload = {
        'model': {'display_name': 'Opus'},
        'context_window': {'used_percentage': 12},
        'rate_limits': {'five_hour': {'used_percentage': 3}},
        'workspace': {'current_dir': '/w'},
    }
    result = run_script(json.dumps(payload), tmp_path)
    assert result.returncode == 0
    assert result.stdout == 'Opus | ctx: 12% | 5h: 3% | cwd: /w\n'


@pytest.mark.parametrize('stdin', ['', 'not json', '[1, 2]', '"text"', '{"model": null}', '{"context_window": {"used_percentage": "n/a"}}'])
def test_script_survives_unusable_input(tmp_path, stdin):
    result = run_script(stdin, tmp_path)
    assert result.returncode == 0
    assert result.stderr == ''
    assert result.stdout == '\n'

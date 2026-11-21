"""Tests of the todo-review skill's body-preservation check."""

import pathlib
import sys

import hypothesis
import hypothesis.strategies
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import verify_bodies  # noqa: E402


def test_item_bodies_ignores_text_before_first_heading() -> None:
    assert verify_bodies.item_bodies('intro\n\n## A\nbody\n') == {'A': 'body'}


def test_item_bodies_handles_consecutive_headings() -> None:
    assert verify_bodies.item_bodies('## A\n## B\ntext\n') == {'A': '', 'B': 'text'}


def test_item_bodies_keeps_a_trailing_item_and_strips_blank_lines() -> None:
    text = '## A\n\n\nfirst\n\n## B\n\nlast\n\n\n'

    assert verify_bodies.item_bodies(text) == {'A': 'first', 'B': 'last'}


def test_item_bodies_of_empty_text() -> None:
    assert verify_bodies.item_bodies('') == {}


def write(tmp_path: pathlib.Path, name: str, text: str) -> str:
    path = tmp_path / name
    path.write_text(text, encoding='utf-8')
    return str(path)


def test_main_returns_0_when_every_body_survives(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    old = write(tmp_path, 'old.md', '## A\nalpha\n## B\nbeta\n')
    new = write(tmp_path, 'new.md', '## A\nalpha\n')
    done = write(tmp_path, 'done.md', '## B\nbeta\n')

    assert verify_bodies.main(['x', old, new, done]) == 0
    assert '2 of 2 item bodies preserved' in capsys.readouterr().out


def test_main_returns_1_and_names_each_lost_body(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    old = write(tmp_path, 'old.md', '## A\nalpha\n## B\nbeta\n## C\n')
    new = write(tmp_path, 'new.md', '## A\ngamma\n')

    assert verify_bodies.main(['x', old, new]) == 1

    out = capsys.readouterr().out
    assert 'LOST OR ALTERED: A' in out
    assert 'LOST OR ALTERED: B' in out
    assert 'LOST OR ALTERED: C' not in out
    assert '1 of 3 item bodies preserved' in out


def test_main_returns_2_with_fewer_than_two_paths(capsys: pytest.CaptureFixture[str]) -> None:
    assert verify_bodies.main(['x', 'only-one']) == 2
    assert 'Usage' in capsys.readouterr().out


def test_main_returns_2_and_names_a_missing_new_file(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    old = write(tmp_path, 'old.md', '## A\nalpha\n')
    missing = str(tmp_path / 'missing.md')

    assert verify_bodies.main(['x', old, missing]) == 2

    err = capsys.readouterr().err
    assert err.startswith(f'cannot read {missing}: ')
    assert 'Traceback' not in err


def test_main_returns_2_and_names_a_missing_old_file(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    new = write(tmp_path, 'new.md', '## A\nalpha\n')
    missing = str(tmp_path / 'missing.md')

    assert verify_bodies.main(['x', missing, new]) == 2

    assert f'cannot read {missing}: ' in capsys.readouterr().err


def test_main_returns_2_on_a_file_that_is_not_utf8(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    old = write(tmp_path, 'old.md', '## A\nalpha\n')
    bad = tmp_path / 'bad.md'
    bad.write_bytes(b'\xff\xfe\x80')

    assert verify_bodies.main(['x', old, str(bad)]) == 2

    assert f'cannot read {bad}: ' in capsys.readouterr().err


TITLES = hypothesis.strategies.text(alphabet='abcdefghij XYZ', min_size=1, max_size=12).map(str.strip).filter(bool)
BODY_LINES = hypothesis.strategies.text(alphabet='abcdefghij #-*', max_size=20).filter(lambda line: not line.startswith('## '))
BODIES = hypothesis.strategies.lists(BODY_LINES, max_size=5).map(lambda lines: '\n'.join(lines).strip('\n'))


@hypothesis.settings(max_examples=50, deadline=None)
@hypothesis.given(hypothesis.strategies.dictionaries(TITLES, BODIES, max_size=6))
def test_item_bodies_round_trips_a_generated_file(items: dict[str, str]) -> None:
    text = '\n'.join(f'## {title}\n{body}\n' for title, body in items.items())

    assert verify_bodies.item_bodies(text) == items

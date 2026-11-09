"""Tests of the test-log-review skill's scan script, against throwaway logs."""

import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import scan  # noqa: E402

PASSING_WITH_WARNINGS = """\
2026-01-01@10:00:00
============================= test session starts ==============================
src/tests/test_a.py::test_x 2026-01-01T10:00:01 WARNING  pkg.mod:run:12 failed to remove checkpoint PASSED
src/tests/test_b.py::test_y[3 chunks, 0 failed] PASSED
=============================== warnings summary ===============================
src/tests/test_a.py::test_x
  /venv/lib/lib_a/mod.py:9: FutureWarning: `thing` is deprecated, use `other`
    def f():

src/tests/test_b.py::test_y
src/tests/test_b.py::test_z
  /venv/lib/lib_b/util.py:40: DeprecationWarning: open() is deprecated
    x = open()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 10 passed, 2 skipped, 3 warnings in 4.20s (0:00:04) ==================
"""

FAILING = """\
============================= test session starts ==============================
=========================== short test summary info ============================
FAILED src/tests/test_c.py::test_broken - AssertionError
ERROR src/tests/test_d.py::test_setup - RuntimeError
================= 1 failed, 5 passed, 1 error in 1.00s ==================
"""

NO_TESTS = """\
collecting ... collected 0 items

============================ no tests ran in 1.86s =============================
"""


def make_repo(root: pathlib.Path, name: str, logs: dict[str, str]) -> pathlib.Path:
    repo = root / name
    (repo / '.git').mkdir(parents=True)
    for i, (log_name, text) in enumerate(logs.items()):
        path = repo / log_name
        path.write_text(text)
        os.utime(path, (1_000_000 + i, 1_000_000 + i))
    return repo


def test_log_kind_strips_the_timestamp():
    assert scan.log_kind('pytest-2026-11-08@22.04.02.log') == 'pytest.log'
    assert scan.log_kind('pytest-correctness-2026-11-09@00.54.28.log') == 'pytest-correctness.log'


def test_passing_log_counts_come_from_the_summary_not_from_log_lines(tmp_path):
    repo = make_repo(tmp_path, 'alpha', {'pytest-2026-01-01@10.00.00.log': PASSING_WITH_WARNINGS})
    [report] = scan.scan(tmp_path, 'pytest*.log', 1)
    assert report.repository == 'alpha'
    assert report.counts == {'passed': 10, 'skipped': 2, 'warning': 3}
    assert report.failures == []
    assert pathlib.Path(report.path).parent == repo


def test_warnings_are_grouped_by_category_and_message(tmp_path):
    make_repo(tmp_path, 'alpha', {'pytest-2026-01-01@10.00.00.log': PASSING_WITH_WARNINGS})
    [report] = scan.scan(tmp_path, 'pytest*.log', 1)
    assert dict((w, n) for n, w in report.warnings) == {
        'FutureWarning: `thing` is deprecated, use `other`': 1,
        'DeprecationWarning: open() is deprecated': 1,
    }
    assert report.needs_investigation


def test_failures_and_errors_are_reported(tmp_path):
    make_repo(tmp_path, 'beta', {'pytest-2026-01-02@10.00.00.log': FAILING})
    [report] = scan.scan(tmp_path, 'pytest*.log', 1)
    assert report.counts['failed'] == 1
    assert report.counts['error'] == 1
    assert report.failures == ['FAILED src/tests/test_c.py::test_broken', 'ERROR src/tests/test_d.py::test_setup']
    assert report.needs_investigation


def test_only_the_newest_log_of_each_kind_is_read(tmp_path):
    make_repo(
        tmp_path,
        'gamma',
        {
            'pytest-2026-01-01@10.00.00.log': FAILING,
            'pytest-2026-01-02@10.00.00.log': PASSING_WITH_WARNINGS,
            'pytest-correctness-2026-01-02@11.00.00.log': NO_TESTS,
        },
    )
    reports = scan.scan(tmp_path, 'pytest*.log', 1)
    assert sorted(pathlib.Path(r.path).name for r in reports) == [
        'pytest-2026-01-02@10.00.00.log',
        'pytest-correctness-2026-01-02@11.00.00.log',
    ]


def test_a_log_with_no_tests_needs_no_investigation(tmp_path, capsys):
    make_repo(tmp_path, 'delta', {'pytest-2026-01-01@10.00.00.log': NO_TESTS})
    [report] = scan.scan(tmp_path, 'pytest*.log', 1)
    assert report.no_tests
    assert not report.needs_investigation
    scan.print_text([report])
    assert 'NO TESTS' in capsys.readouterr().out


def test_repositories_are_found_at_each_depth_and_others_ignored(tmp_path):
    make_repo(tmp_path, 'top', {'pytest-2026-01-01@10.00.00.log': NO_TESTS})
    make_repo(tmp_path / 'projects', 'nested', {'pytest-2026-01-01@10.00.00.log': NO_TESTS})
    (tmp_path / 'not-a-repo').mkdir()
    (tmp_path / 'not-a-repo' / 'pytest-2026-01-01@10.00.00.log').write_text(FAILING)
    assert [r.repository for r in scan.scan(tmp_path, 'pytest*.log', 2)] == ['nested', 'top']
    assert [r.repository for r in scan.scan(tmp_path, 'pytest*.log', 1)] == ['top']


def test_json_output_flags_logs_to_investigate(tmp_path, capsys):
    make_repo(tmp_path, 'alpha', {'pytest-2026-01-01@10.00.00.log': PASSING_WITH_WARNINGS})
    assert scan.main([str(tmp_path), '--depth', '1', '--json']) == 0
    [entry] = json.loads(capsys.readouterr().out)
    assert entry['needs_investigation'] is True
    assert entry['kind'] == 'pytest.log'

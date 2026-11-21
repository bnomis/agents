"""Scan the newest pytest log of each kind in every repository below a root.

Prints, per log: the final summary line, its counts, and the warnings in the
log's "warnings summary" grouped by category and message, each with the number
of places (source lines) pytest lists it under; how often each fired is in the
summary line's total and the section's test lists. Counts come from
pytest's own summary line, never from a grep for "failed", which matches log
lines that passing tests print.

Usage:
    python3 scan.py <root> [--glob 'pytest*.log'] [--depth N] [--json]
"""

import argparse
import collections
import dataclasses
import json
import pathlib
import re
import sys

STAMP = re.compile(r'[-_]?\d{4}-\d{2}-\d{2}(?:[@T_ -]?\d{1,2}(?:[.:-]\d{2}){1,2})?')
SUMMARY = re.compile(r'^=+ (?P<body>.*\bin [\d.]+s.*?) =+$')
COUNT = re.compile(r'(?P<n>\d+) (?P<what>failed|passed|skipped|deselected|xfailed|xpassed|warnings?|errors?|rerun)')
NO_TESTS = re.compile(r'^=+ no tests ran\b')
WARNING_LINE = re.compile(r'(?P<cat>[A-Za-z_.]*(?:Warning|Deprecation\w*)): (?P<msg>.+)')
FAILURE_LINE = re.compile(r'^(?P<kind>FAILED|ERROR) (?P<test>\S+)')


@dataclasses.dataclass
class LogReport:
    repository: str
    path: str
    kind: str
    summary: str
    counts: dict[str, int]
    no_tests: bool
    failures: list[str]
    warnings: list[tuple[int, str]]

    @property
    def needs_investigation(self) -> bool:
        return bool(self.counts.get('failed') or self.counts.get('error') or self.failures or self.warnings)


def log_kind(name: str) -> str:
    """The log's name with its timestamp removed: logs of one kind share it."""
    return STAMP.sub('', name)


def scan_repositories(root: pathlib.Path, depth: int) -> list[pathlib.Path]:
    """The root and every directory up to `depth` levels below it that holds a `.git`."""
    levels = [[root]] + [list(root.glob('/'.join(['*'] * n))) for n in range(1, depth + 1)]
    return sorted({p for level in levels for p in level if p.is_dir() and (p / '.git').exists()})


def newest_per_kind(repository: pathlib.Path, pattern: str) -> list[pathlib.Path]:
    newest: dict[str, pathlib.Path] = {}
    root = repository.resolve()
    for path in repository.glob(pattern):
        if not path.resolve().is_relative_to(root):
            continue
        kind = log_kind(path.name)
        if kind not in newest or path.stat().st_mtime > newest[kind].stat().st_mtime:
            newest[kind] = path
    return [newest[k] for k in sorted(newest)]


def read_log(repository: pathlib.Path, path: pathlib.Path) -> LogReport:
    lines = path.read_text(errors='replace').splitlines()
    summary, counts, no_tests = '', {}, False
    for line in lines:
        if NO_TESTS.match(line):
            no_tests = True
        m = SUMMARY.match(line)
        if m:
            summary = m.group('body')
    for m in COUNT.finditer(summary):
        what = m.group('what').rstrip('s') if m.group('what') != 'xpassed' else 'xpassed'
        counts[what] = int(m.group('n'))
    failures = [f'{m.group("kind")} {m.group("test")}' for line in lines if (m := FAILURE_LINE.match(line))]
    warnings = collections.Counter()
    in_section = False
    for line in lines:
        if re.match(r'^=+ warnings summary', line):
            in_section = True
            continue
        if in_section and (line.startswith('-- Docs:') or re.match(r'^=+ ', line)):
            in_section = False
        if in_section:
            m = WARNING_LINE.search(line)
            if m:
                warnings[f'{m.group("cat").rsplit(".", 1)[-1]}: {m.group("msg").strip()[:140]}'] += 1
    return LogReport(
        repository=repository.name,
        path=str(path),
        kind=log_kind(path.name),
        summary=summary,
        counts=counts,
        no_tests=no_tests,
        failures=failures,
        warnings=[(n, w) for w, n in warnings.most_common()],
    )


def scan(root: pathlib.Path, pattern: str, depth: int) -> list[LogReport]:
    return [read_log(repo, path) for repo in scan_repositories(root, depth) for path in newest_per_kind(repo, pattern)]


def print_text(reports: list[LogReport]) -> None:
    for r in reports:
        state = 'INVESTIGATE' if r.needs_investigation else ('NO TESTS' if r.no_tests else 'clean')
        print(f'== {r.repository} | {pathlib.Path(r.path).name} | {state}')
        print(f'   summary: {r.summary or "(none)"}')
        for f in r.failures:
            print(f'   {f}')
        for n, w in r.warnings:
            print(f'   {n:>3} place(s): {w}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('root', type=pathlib.Path)
    parser.add_argument('--glob', default='pytest*.log', help='log file pattern at each repository root')
    parser.add_argument('--depth', type=int, default=2, help='how many directory levels below root to look for repositories')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        reports = scan(args.root.resolve(), args.glob, args.depth)
    except OSError as error:
        print(error, file=sys.stderr)
        return 1
    if args.json:
        json.dump([dataclasses.asdict(r) | {'needs_investigation': r.needs_investigation} for r in reports], sys.stdout, indent=2)
        print()
    else:
        print_text(reports)
    return 0


if __name__ == '__main__':
    sys.exit(main())

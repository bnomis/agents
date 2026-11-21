#!/usr/bin/env python
import json
import subprocess
import sys

# ruff: noqa: S607

GREEN = '\033[32m'
RESET = '\033[0m'
YELLOW = '\033[33m'


def git_status() -> str:
    """Return `git: <branch>+S~M` for the working directory, or '' outside a repository."""
    try:
        output = subprocess.check_output(['git', 'status', '--porcelain=v2', '--branch'], text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError, FileNotFoundError:
        return ''
    branch = ''
    staged = modified = 0
    for line in output.splitlines():
        if line.startswith('# branch.head '):
            head = line.removeprefix('# branch.head ')
            branch = '' if head == '(detached)' else head
        elif line.startswith(('1 ', '2 ')):
            xy = line.split(' ', 2)[1]
            staged += xy[0] != '.'
            modified += xy[1] != '.'
    result = branch
    if staged:
        result += f'{GREEN}+{staged}{RESET}'
    if modified:
        result += f'{YELLOW}~{modified}{RESET}'
    return f'git: {result}' if result else ''


def walk_section(data: dict[str, object], *keys: str) -> object:
    """Walk nested objects by key; None when a step is missing or not an object."""
    value: object = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def whole_percentage(value: object) -> int:
    """The whole percentage, or 0 when the value is absent, zero or not a number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return int(value)


def get_model(data: dict[str, object]) -> str:
    name = walk_section(data, 'model', 'display_name')
    return name if isinstance(name, str) else ''


def get_directory(data: dict[str, object]) -> str:
    cwd = walk_section(data, 'workspace', 'current_dir')
    return f'cwd: {cwd}' if isinstance(cwd, str) and cwd else ''


def get_context_window(data: dict[str, object]) -> str:
    ctx = whole_percentage(walk_section(data, 'context_window', 'used_percentage'))
    return f'ctx: {ctx}%' if ctx else ''


def get_rate_percentage(data: dict[str, object]) -> str:
    rate = whole_percentage(walk_section(data, 'rate_limits', 'five_hour', 'used_percentage'))
    return f'5h: {rate}%' if rate else ''


def read_fields(text: str) -> dict[str, object]:
    """The session's fields; empty when the text is not a JSON object."""
    try:
        data = json.loads(text)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def main() -> int:
    data = read_fields(sys.stdin.read())
    parts = [
        get_model(data),
        get_context_window(data),
        get_rate_percentage(data),
        get_directory(data),
        git_status(),
    ]
    print(' | '.join(part for part in parts if part))
    return 0


if __name__ == '__main__':
    sys.exit(main())

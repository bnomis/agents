#!/usr/bin/env python
"""
install-claude: symlinks files in to ~/.claude/
"""

import argparse
import json
import logging
import os
import pathlib
import shutil
import sys
import tempfile
from typing import NoReturn


def symlink_file(options, src: pathlib.Path, dst: pathlib.Path) -> None:
    """link a file from source to target, renaming existing file if necessary"""
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink():
            dst.unlink()
        else:
            existing = dst
            rn = existing.with_suffix(dst.suffix + '.orig')
            i = 2
            while rn.exists():
                rn = rn.with_name(rn.stem + f'.{i}' + rn.suffix)
                i += 1
            existing.rename(rn)

    dst_parent = dst.parent
    src_parent = src.parent
    relative_parent = src_parent.relative_to(dst_parent, walk_up=True)
    print(f'Linking {src} to {dst} via {relative_parent / src.name}')
    dst.symlink_to(relative_parent / src.name)


def symlink_dir(options, src: pathlib.Path, dst: pathlib.Path) -> None:
    """links files in a directory from src to dst"""
    print(f'Linking directory {src} to {dst}')
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        srcf = f
        dstf = dst / f.name
        symlink_file(options, srcf, dstf)


def this_dir() -> pathlib.Path:
    """returns the directory of this script"""
    return pathlib.Path(__file__).parent.resolve()


def src_claude_dir() -> pathlib.Path:
    """returns the directory of the claude files"""
    return this_dir().parent / 'claude'


def dest_claude_dir() -> pathlib.Path:
    """returns the directory of the claude files"""
    return pathlib.Path.home() / '.claude'


STOP_HOOK_SCRIPT = 'auditme-stop.sh'
STOP_HOOK_COMMAND = f'bash "$HOME/.claude/hooks/{STOP_HOOK_SCRIPT}"'


class SettingsError(Exception):
    """~/.claude/settings.json cannot be merged into; nothing was written."""


def _read_settings(path: pathlib.Path) -> dict:
    """returns the parsed settings, {} when the file is absent"""
    if not path.exists():
        return {}
    try:
        settings = json.loads(path.read_text())
    except ValueError as e:
        raise SettingsError(f'{path} is not valid JSON ({e}); not changed') from e
    if not isinstance(settings, dict):
        raise SettingsError(f'{path} is not a JSON object; not changed')
    return settings


def _has_stop_hook(settings: dict) -> bool:
    """whether any Stop hook command already names the script"""
    entries = settings.get('hooks', {}).get('Stop', [])
    return any(STOP_HOOK_SCRIPT in hook.get('command', '') for entry in entries for hook in entry.get('hooks', []))


def register_stop_hook(options, settings_path: pathlib.Path) -> None:
    """adds the Stop hook to settings.json once, keeping everything else"""
    settings = _read_settings(settings_path)
    if _has_stop_hook(settings):
        print(f'Stop hook already registered in {settings_path}')
        return

    entry = {'hooks': [{'type': 'command', 'command': STOP_HOOK_COMMAND}]}
    settings.setdefault('hooks', {}).setdefault('Stop', []).append(entry)

    if settings_path.exists():
        orig = settings_path.with_name(settings_path.name + '.orig')
        if not orig.exists():
            shutil.copy2(settings_path, orig)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=settings_path.parent, prefix=f'{settings_path.name}.')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(json.dumps(settings, indent=2) + '\n')
        if settings_path.exists():
            shutil.copymode(settings_path, tmp)
        os.replace(tmp, settings_path)
    except BaseException:
        pathlib.Path(tmp).unlink(missing_ok=True)
        raise
    print(f'Registered Stop hook in {settings_path}')


def find_dangling_symlinks(options, dir: pathlib.Path, max_depth: int = 2) -> None:
    root_depth = len(dir.parts)
    dangle = []
    for dirpath, dirnames, filenames in dir.walk(top_down=True):
        depth = len(dirpath.parts) - root_depth
        if depth >= max_depth - 1:
            dirnames.clear()

        for f in filenames:
            p = pathlib.Path(dirpath) / f
            if p.is_symlink() and not p.exists():
                dangle.append(p)

    if dangle:
        print('Dangling symlinks found:')
        for p in dangle:
            print(f'  {p}')
        print('Remove with:')
        print(f'rm {" ".join(str(p) for p in dangle)}')


def install_claude(options) -> None:
    """link files from source to target"""
    fdir = src_claude_dir()
    tdir = dest_claude_dir()
    tdir.mkdir(parents=True, exist_ok=True)

    for f in fdir.iterdir():
        if f.name[0] == '.':
            continue

        src = f
        dest = tdir / f.name
        if src.is_dir():
            symlink_dir(options, src, dest)
        else:
            symlink_file(options, src, dest)

    find_dangling_symlinks(options, tdir)
    register_stop_hook(options, tdir / 'settings.json')


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='install-claude',
        description='symlinks files into ~/.claude',
    )
    return parser.parse_args(argv)


def main(argv) -> NoReturn:
    options = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG)
    options.logger = logging.getLogger('install-claude')
    m = 0
    try:
        install_claude(options)
    except SettingsError as e:
        m = f'Error: {e}'
    except Exception as e:
        m = f'Exception: {e}'
        options.logger.exception(m)
    sys.exit(m)


if __name__ == '__main__':
    main(sys.argv[1:])

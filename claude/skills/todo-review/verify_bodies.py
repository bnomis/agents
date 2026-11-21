"""Check that every item body of an old TODO.md survives a rewrite.

Usage:
    git show HEAD:TODO.md > /tmp/todo-before.md
    python3 verify_bodies.py /tmp/todo-before.md TODO.md [DONE.md ...]

An item is a `## ` heading and the text up to the next `## ` heading. Its
body (the text after the heading line, stripped of surrounding blank lines)
must appear, character for character, in at least one of the new files: in
TODO.md as a consolidated `###` finding or a reordered item, or in DONE.md
when it was moved. Exits 1 and names each body that was lost or altered, and
2 when given fewer than two paths or when a file cannot be read (the path and
the reason go to stderr).
"""

import pathlib
import sys


def item_bodies(text: str) -> dict[str, str]:
    """Map each `## ` heading's title to its body, in file order."""
    bodies: dict[str, str] = {}
    title: str | None = None
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith('## '):
            if title is not None:
                bodies[title] = '\n'.join(lines).strip('\n')
            title, lines = line[3:].strip(), []
        elif title is not None:
            lines.append(line)
    if title is not None:
        bodies[title] = '\n'.join(lines).strip('\n')
    return bodies


def main(argv: list[str]) -> int:
    """Report every old body found in none of the new files."""
    if len(argv) < 3:
        print(__doc__)
        return 2
    texts: list[str] = []
    for path in argv[1:]:
        try:
            texts.append(pathlib.Path(path).read_text(encoding='utf-8'))
        except (OSError, UnicodeDecodeError) as error:
            print(f'cannot read {path}:', error, file=sys.stderr)
            return 2
    old = item_bodies(texts[0])
    new_text = '\n'.join(texts[1:])
    lost = [title for title, body in old.items() if body and body not in new_text]
    for title in lost:
        print(f'LOST OR ALTERED: {title}')
    print(f'{len(old) - len(lost)} of {len(old)} item bodies preserved')
    return 1 if lost else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

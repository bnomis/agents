---
paths:
  - "**/*.py"
---

# argparse standards

New command-line interfaces use `cappa`
(Data structures in `~/.claude/rules/auditme/coding-standards.md`,
from the auditor repository). argparse is
used only in existing code not yet converted, and in a script that must stay
standard-library only, such as a checker run with no project dependencies
installed. Where it is used, follow the standards below.

Add a trailing comma to the arguments passed to argparse functions so the arguments are formatted one per line, see below:

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='Program name',
        description='Program description',
    )
    parser.add_argument(
        '--argument',
        help='Argument help',
    )
    return parser.parse_args()
```

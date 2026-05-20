---
paths:
  - "**/*.py"
---

# argparse standards

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

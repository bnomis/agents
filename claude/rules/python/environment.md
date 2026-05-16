---
paths:
  - "**/*.py"
  - "**/bin/*"
---

# Python environment and scripts

## Python environment activation

Before running Python scripts, activate the Python environment by sourcing `bin/activate.sh` as shown below:

```shell
source bin/activate.sh
```

This activates the `.venv` and adds `src/` to `PYTHONPATH` so the `<project>` package is importable without installation.

After activation, run scripts, and `pytest` directly.

For example:

```shell
bin/script.py

cd src/tests; pytest
```

No `uv run` prefix is needed. Avoid `uv run`.

## Running scripts

We prefer to execute scripts directly, rather than prefixing all commands with `uv run`.

After the Python environment has been activated (see above), the scripts in the `bin/` directory can be executed directly without prefixing with `uv run`. For example, to run `bin/script.py` after environment activation simply run the command `bin/script.py`.

The same is true with `pytest`. To run `pytest` after Python environment activation, simply run `pytest` in the projects root directory.

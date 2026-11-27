---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/uv.lock"
  - "**/requirements.txt"
---

# Python Development tools and libraries

- Python 3.14 (minimum supported version) <https://docs.python.org/3.14/>
- Package and virtual environment management: uv <https://docs.astral.sh/uv/>
- Logging: `loguru` <https://loguru.readthedocs.io/en/stable/>
- Command line argument processing: `cappa` <https://cappa.readthedocs.io/en/latest/index.html>, for every CLI (argparse only as [argparse.md](argparse.md) allows)
- Coding standards, quality and lint: ruff <https://docs.astral.sh/ruff/>
- Containerisation: Docker <https://docs.docker.com/>
- Testing: `pytest` <https://docs.pytest.org/en/stable/>
- Property based testing: hypothesis <https://hypothesis.works/>
- Network http[s] requests: `aiohttp` <https://docs.aiohttp.org/en/stable/>
- Type checking: `mypy` <https://github.com/python/mypy>

## Editor diagnostics are not the project's type checker

The harness may show diagnostics after an edit from its own language server
(Pyright, for example), run without the project's virtual environment. They
are not the project's checks: do not relay or comment on them. Judge types
with the project's own configured checker (`mypy`, run in the project's
environment), and report only what it says.

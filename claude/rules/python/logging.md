---
paths:
  - "**/*.py"
---

# Logging conventions

General logging rules (use `loguru`, log levels, exception logging) are
in [coding-standards.md](../auditme/coding-standards.md#logging), from the
auditor repository. PII rules are in
[security.md](../security.md). This file covers structured log lines that
other tools parse.

## ETA log lines

ETA (estimated time of arrival) log lines report how long a long-running
operation has left to run. They are parsed by downstream tooling, so the
format is load-bearing:

- Level: `info`.
- Prefix: `ETA: ` (with the trailing space).

Example:

```python
loguru.logger.info(f'ETA: training will finish in {duration}')
```

A project that parses any other prefix documents it in its own
`claude/rules/`, with its level and format.

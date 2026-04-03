---
paths:
  - "**/*.sh"
---

# Bash guidelines

## Avoid pipes and output buffering

Do not pipe output through `head`, `tail`, `less` or `more` when monitoring or checking command output.

Do not use `| head -n X` or `| tail -n X` to truncate output, these cause buffering problems.

Avoid chained pipes, these can cause output to buffer indefinitely.

Let commands complete fully or use command-specific flags to limit output. For example, use `git log -n 10` instead of `git log | head -n 10`.

For log monitoring, prefer reading files directly rather than piping through filters.

## Avoid interactive commands

Do not use interactive flags such as `-i` or commands that require user input (e.g., `less`, `vim`, `nano`).

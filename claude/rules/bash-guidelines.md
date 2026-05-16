# Bash guidelines

Claude runs commands in a non-TTY subprocess. Pagers hang, interactive
prompts have no one to answer them, and some pipes buffer indefinitely.

## Output handling

- Use command flags to limit output: `git log -n 10`, not `git log | head`.
- Prefer `grep -m N` (or `rg -m N`) over `grep | head`.
- Read log files directly instead of piping through filters.
- Avoid `watch` and `tail -f` without a timeout.

## No interactive tools

- No pagers: `less`, `more`, `fzf` (they expect a TTY and hang).
- No editors: `vim`, `nano`.
- No `-i` flags or anything that prompts for input.

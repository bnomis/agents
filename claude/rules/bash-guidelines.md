# Bash guidelines

Claude runs commands in a non-TTY subprocess. Pagers hang, interactive
prompts have no one to answer them, and some pipes buffer indefinitely.

## Output handling

- Use command flags to limit output: `git log -n 10`, not `git log | head`.
- Prefer `grep -m N` (or `rg -m N`) over `grep | head`.
- Read log files directly instead of piping through filters.
- Avoid `watch` and `tail -f` without a timeout.
- Judge a command that runs several checks (`pre-commit`, a test runner over
  many directories) by its exit status, or by grepping its whole output for
  `Failed`, never by a `tail` of it: the failing check can sit above the
  lines kept, and the report then claims a pass that the next push refutes.

## No interactive tools

- No pagers: `less`, `more`, `fzf` (they expect a TTY and hang).
- No editors: `vim`, `nano`.
- No `-i` flags or anything that prompts for input.

## Cutting text out of a file

Cut a section by its heading or another marker
(`sed -n '/^const state/,$p'`), never by a line number you have not just
read: a file that has grown since the lines were counted loses the end of
the section without any error.

## Finding and stopping processes

- A pattern search over command lines (`pgrep -f`, `ps | grep`) matches the
  shell running it, whose own command line contains the pattern. Match on
  the process name (`ps -o comm=`) instead, so the checking shell is never
  counted.
- The Bash tool's shell has `pipefail` on. In `ps | grep -q pattern`, `grep`
  exits at its first match, `ps` dies of SIGPIPE, and the pipeline fails
  exactly when a match was found. Count matches and test the count; never
  test a pipeline's exit status.
- Before trusting a new check, run it once by hand against each known state
  (a process running, none running) and see that it reports both correctly.
- Never `pkill -f`: it reaches other sessions' processes on the machine, and
  the killing shell itself. Stop a background command with `TaskStop` and
  its task id. If a process outlives that, find its PID, check that its
  command line is this session's, and kill that PID alone.
- While a background run is going, do not change, stash or check out any
  file it can read. Wait for it, or work in a separate worktree.

#!/usr/bin/env bash
# Install this repository's Claude Code files (claude/) into ~/.claude, and
# set claude/statusline.py as the status line unless one is set, with the
# shared installer install-in-claude at the commit this repository was tested
# with. Extra arguments pass through, e.g. --dry-run.
set -euo pipefail

INSTALL_IN_CLAUDE_REV=fa68deb10fb77ed1c59f1c35a79a93881f955901

REPO=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

STATUS_LINE='statusLine={"command":"~/.claude/statusline.py","type":"command"}'

exec uvx --from "git+ssh://git@github.com/bnomis/install-in-claude.git@$INSTALL_IN_CLAUDE_REV" \
    install-in-claude --source "$REPO/claude" --set-if-absent "$STATUS_LINE" "$@"

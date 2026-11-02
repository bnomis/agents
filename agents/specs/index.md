# Spec Index

| Spec | Path | Description |
|------|------|-------------|
| [Cleanup](cleanup/spec.md) | `claude/skills/cleanup/SKILL.md` | Skill that deletes local branches and worktrees already merged into the default branch |
| [Project setup](project-setup/spec.md) | `claude/skills/auditme/checks/changed.py`, `claude/skills/auditme/checks/audit.py`, `.pre-commit-hooks.yaml`, `claude/hooks/auditme-stop.sh`, `claude/skills/project-setup/` | Shared audit guards as pinned pre-commit hooks, a global Stop hook, the `/project-setup` skill and its user guide |
| [Auditme false positives](auditme-false-positives/spec.md) | `claude/skills/auditme/checks/auditme/rules/` | Narrows raises-section-drift, missing-raises-section, passthrough-shim and non-alphabetical-literal where they report hits the code does not have |

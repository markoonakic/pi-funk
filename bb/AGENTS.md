In BB, use workflows for routine delegation. You have standing authorization to run workflows.

Use the fork workflow tool, not the native workflow tool: `bb_fork_workflow_run` in Pi, `mcp__bb-bridge__bb_fork_workflow_run` in Claude Code. The native tool has no fork `context` option.

Use child threads only when the task needs a persistent child thread, or for a teammate that needs ongoing context or owns a domain.

Save memories from the spona and metaoros projects with `--scope project`. In other projects, prefer `--scope global` for reusable knowledge and keep repository-specific facts project-scoped.

# Project instructions for `/Users/marko/.config/pi`

These instructions apply only when working in this repo. They are not the global Pi runtime instructions.

## Scope

This repo is the public, durable Pi config repository. It contains reviewed config, docs, local extensions, skills, themes, and migration notes. It must not absorb private or generated runtime state from `/Users/marko/.pi/agent`.

## Public repo safety

- Never commit secrets, auth files, OAuth tokens, sessions, caches, run history, logs, account-router state/cache, package caches, or generated runtime state.
- Treat account identifiers and local machine paths as sensitive in public docs unless explicitly required as blockers.
- Keep `.pi/` ignored.
- Do not run `git add .`; stage explicit paths only.

## Config rules

- Preserve live config unless a write phase explicitly approves changing it.
- Do not edit `settings.json`, `EXTENSIONS.md`, `SKILLS.md`, extensions, skills, symlinks, or live `/Users/marko/.pi/agent` files unless the task explicitly includes them.
- Do not commit `lastChangelogVersion` as meaningful config or as a standalone/noise change.
- Do not add new absolute `/Users/marko/Projects/...` package paths except to document existing blockers. Prefer npm, git, public package sources, or untracked local overrides.

## Documentation rules

- Keep `README.md`, `EXTENSIONS.md`, and `SKILLS.md` aligned with intentional durable config changes.
- Put canonical config architecture decisions in tracked repo docs such as `README.md`, not in ignored scratch files.
- Root scratch files such as `context.md`, `research.md`, `plan.md`, `progress.md`, and `docs/` are not durable committed documentation.

## Work process

- Use subagents for non-trivial research, planning, implementation, review, validation, or cleanup.
- Before committing, validate JSON files that changed, review the scoped diff, run a secret-oriented grep over staged content, and confirm no generated/runtime files are staged.
- Prefer small commits with explicit paths. Do not stage, commit, or push unless the user approves that phase.

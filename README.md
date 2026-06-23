# Pi config

`/Users/marko/.config/pi` is the public Git repo for durable Pi configuration.

## Canonical architecture

Keep this repo as the canonical place for reviewed, public, durable Pi config. Do **not** move the repo into `/Users/marko/.pi/agent`: that directory contains auth, sessions, package caches, run history, account-router state/cache, and other runtime state that must stay out of Git.

Durable config that belongs here:

- `settings.json` after it is reconciled with live settings
- `models.json`
- `keybindings.json`
- `extensions/`
- `skills/`
- `themes/`
- `prompts/` if used
- root `AGENTS.md` for this repo
- `agent/AGENTS.md` as the future source for global `/Users/marko/.pi/agent/AGENTS.md`
- `EXTENSIONS.md` and `SKILLS.md` catalogs

Runtime/private state that must not be committed:

- `/Users/marko/.pi/agent/auth.json`
- `/Users/marko/.pi/agent/sessions/`
- `/Users/marko/.pi/agent/run-history.jsonl`
- `/Users/marko/.pi/agent/git/`
- `/Users/marko/.pi/agent/npm/`
- `/Users/marko/.pi/agent/mcp-cache.json`
- `/Users/marko/.pi/agent/mcp-npx-cache.json`
- `/Users/marko/.pi/agent/pi-account-router-*.json`
- `/Users/marko/.pi/agent/intercom/`
- `/Users/marko/.pi/agent/messenger/`

## Current status

Most durable runtime surfaces already point from `/Users/marko/.pi/agent` into this repo:

- `models.json`
- `keybindings.json`
- `extensions/`
- `skills/`
- `themes/`

`settings.json` is the exception: `/Users/marko/.pi/agent/settings.json` is currently a separate live file and differs from this repo's `settings.json`. Do not treat repo `settings.json` as fully live/canonical until reconciliation and symlink migration are completed.

## Settings migration plan

Phase 1: reconcile, no symlink yet.

1. Treat `/Users/marko/.pi/agent/settings.json` as the current live source of truth.
2. Copy only intentional durable settings into `/Users/marko/.config/pi/settings.json`.
3. Validate JSON.
4. Run a secret-oriented diff scan.
5. Commit only intentional config/catalog changes.

Phase 2: make repo settings canonical.

1. Back up `/Users/marko/.pi/agent/settings.json`.
2. Replace it with a symlink to `/Users/marko/.config/pi/settings.json`.
3. Start Pi and smoke test.
4. Check whether Pi dirties tracked `settings.json`.

Do not mix `PI_CODING_AGENT_DIR=/Users/marko/.config/pi` with default `/Users/marko/.pi/agent` unless that migration is explicitly planned.

## Public repo caveats

- This repo is public.
- Do not commit auth, sessions, caches, run history, account-router state/cache, generated reports, or other runtime state.
- Do not commit `lastChangelogVersion` as meaningful config or as a standalone/noise change.
- Do not add new absolute `/Users/marko/Projects/...` package paths. Prefer npm, git, public package sources, or untracked local overrides.
- `docs/` is ignored local scratch/reference material, not committed canonical documentation.
- `.poster/` is not yet classified; `.poster/output/` is generated and ignored.

## GitHub update discipline

- Do not use `git add .`; stage intentional files only.
- Keep `README.md`, `EXTENSIONS.md`, and `SKILLS.md` aligned with durable config changes.
- Before committing, review the scoped diff, validate changed JSON, run a secret-oriented grep over staged content, and confirm no generated/runtime files are staged.

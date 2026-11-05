# Project instructions for `~/.config/pi`

These instructions apply only when working in this repo. Runtime instructions are separate: `agent/AGENTS.md` is delivered to regular Pi sessions (including Pi used through Herdr) and, through `profiles/bb/AGENTS.md` → `../../agent/AGENTS.md` and `~/.bb/AGENTS.md`, to the isolated BB profile.

## Scope

This repo is the public, durable Pi config repository. It contains reviewed config, docs, local extensions, skills, themes, profiles, and migration notes. Regular Pi uses private runtime state under `~/.pi/agent`; BB uses the isolated `~/.pi/bb-agent` Pi profile and BB-owned state under `~/.bb`. None of that private or generated state belongs in this repo.

Read `README.md` → **Canonical topology** when changing regular Pi/Herdr delivery. Read `README.md` → **Isolated BB Pi profile** and the relevant `profiles/bb/` sources when changing BB delivery; also compare `nixos-machines/modules/home/bb.nix` with the generated deployed service. A source change or successful source check is not proof that the deployed BB service changed.

## Public repo safety

- Never commit secrets, auth files, OAuth tokens, sessions, caches, run history, logs, account-router state/cache, package caches, or generated runtime state.
- Treat account identifiers and local machine paths as sensitive in public docs unless explicitly required as blockers.
- Keep `.pi/` ignored.
- Do not run `git add .`; stage explicit paths only.

## Config rules

- Preserve live config unless a write phase explicitly approves changing it.
- Do not edit `settings.json`, `EXTENSIONS.md`, `SKILLS.md`, extensions, skills, symlinks, or live state under `~/.pi` or `~/.bb` unless the task explicitly includes them.
- Keep BB-native plugins such as Groups in `bb-extensions`; do not add them to Pi settings or extension catalogs.
- Do not commit `lastChangelogVersion` as meaningful config or as a standalone/noise change.
- Keep machine-specific absolute project paths and temporary legacy browser-migration instructions out of public docs. Prefer npm, git, public package sources, or untracked local overrides.

## Documentation rules

- Keep `README.md`, `EXTENSIONS.md`, and `SKILLS.md` aligned with intentional durable config changes.
- Put canonical config architecture decisions in tracked repo docs such as `README.md`, not in ignored scratch files.
- Root scratch files such as `context.md`, `research.md`, `plan.md`, `progress.md`, and `docs/` are not durable committed documentation.

## Work process

- Use subagents for non-trivial research, planning, implementation, review, validation, or cleanup, with one writer per worktree.
- Before committing, validate JSON files that changed, review the scoped diff, run a secret-oriented grep over staged content, and confirm no generated/runtime files are staged.
- Prefer small commits with explicit paths. Do not stage, commit, or push unless the user approves that phase.

# Project instructions for `~/.config/pi`

These rules apply to this repo.

The shared agent rules are in `agent/AGENTS.md`. Nix links this file to `~/.pi/agent/AGENTS.md`, `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. The BB extras are in `bb/AGENTS.md`. Nix links this file to `~/.bb/AGENTS.md`.

## Scope

This repo is the public source for the one native Pi profile (`~/.pi/agent`), the shared agent rules, the gateway adapter, the MCP render script and the parity check. Private and generated state does not belong here. Read `README.md` before you change links, settings or the MCP files.

A change in this repo does not change the machine. Nix makes the links. A source change is not proof that the live config changed.

## Public repo safety

- Do not commit secrets, auth files, tokens, sessions, caches, run history, logs, package stores or generated state.
- Treat account names and local machine paths as private in docs. Use `~`.
- Keep `.pi/` ignored.
- Stage explicit paths only. Do not run `git add .`.

## Config rules

- Do not change live config under `~/.pi`, `~/.claude`, `~/.codex` or `~/.bb` unless the task includes it.
- Do not use version pins or commit pins in `settings.json`, unless a tool forces one.
- Keep BB-native plugins in `bb-extensions`. Do not add them to `settings.json`.
- Do not add skills to this repo. BB holds the skills.
- Do not commit `lastChangelogVersion` as a change.
- Do not put copies of BB core files in this repo. Do BB core work in the BB core clone.
- Do not delete `.pi/` in this repo before you check that no package store in it is in use.

## Documentation rules

- Keep `README.md` and `EXTENSIONS.md` correct when you change durable config.
- Put architecture decisions in `README.md`. Do not put them in scratch files.
- Put design notes, plans and mockups in the repo they describe, or in `$BB_THREAD_STORAGE`. Do not put them in the repo root.
- Track every file that the docs or the code name. Run `git status` before you finish a task. Report untracked files that the docs need.
- Ignore `__pycache__/` and `/git/`.
- Write docs and rules in ASD-STE100 Simplified Technical English.

## Work process

- Use a BB workflow for non-trivial research, planning, implementation, review or validation. Use one writer for each worktree.
- Before a commit: validate changed JSON files, review the scoped diff, run a secret grep on the staged diff, and check that no generated or runtime file is staged.
- Make small commits with explicit paths. Commit or push only when the user approves.
- Run `scripts/parity-check` and the checks in `README.md` after a change to settings, links or MCP sources.

## Worktrees

- Put worktrees in `~/Projects/worktrees/` or in the worktree folder of the project. Do not use `/tmp`.
- After the merge, remove the worktree and your own branch. Then run `git worktree prune`.
- Delete only your own merged branches. Keep the branches of other people and bots.

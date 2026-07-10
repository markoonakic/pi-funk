# Pi config

`~/.config/pi` is the canonical public Git repo for reviewed, durable Pi configuration. The private Pi runtime root remains `~/.pi/agent`; the repo must not be moved there.

## Canonical topology

The live topology uses selective links; Home Manager declares them on disko, while the Mac currently uses equivalent links.

- `~/.pi/agent/settings.json` → `~/.config/pi/settings.json`
- `~/.pi/agent/models.json` → `~/.config/pi/models.json`
- `~/.pi/agent/keybindings.json` → `~/.config/pi/keybindings.json`
- `~/.pi/agent/extensions` → `~/.config/pi/extensions`
- `~/.pi/agent/skills` → `~/.config/pi/skills`
- `~/.pi/agent/themes` → `~/.config/pi/themes`
- `~/.pi/agent/AGENTS.md` → `~/.config/pi/agent/AGENTS.md`

`~/.config/pi` must exist before Home Manager activation. `prompts/` should be linked by the same selective pattern only if that target is added to this repo; it is currently absent and unmanaged.

`~/.pi/settings.json` must not exist. Home Manager activation fails rather than deleting it. A project-local `.pi/settings.json` is only for an intentional project override, not global configuration.

Pi may update `lastChangelogVersion` in tracked `settings.json`; do not commit that field as meaningful config or as a standalone/noise change. Host-local sidecars in otherwise linked directories are ignored by Git and remain machine-specific.

## Public and private boundaries

Durable public config belongs here:

- `settings.json`
- `models.json`
- `keybindings.json`
- `extensions/`
- `skills/`
- `themes/`
- `prompts/` if used later
- root `AGENTS.md` for this repo
- `agent/AGENTS.md` for global runtime instructions
- `EXTENSIONS.md` and `SKILLS.md` catalogs

Private runtime state stays under `~/.pi/agent` and outside Git, including auth, sessions, trust data, package state/caches, run history, logs, account-router state/cache, and other generated runtime files. Do not manage private state or workflow settings through this repo or Home Manager.

## Extension placement policy

`extensions/` is the live global extension directory because `~/.pi/agent/extensions` points here. Anything loadable there can affect every Pi session.

Use `extensions/` only for package config sidecars, tiny reviewed one-file hooks, and vendor/installer-managed hooks that must live in the global extension directory.

Durable custom packages in `settings.json` should use npm/git sources. Local project checkouts are dev-only working copies, not public-portable global config.

Use `local-extensions/` only for untracked private experiments or machine-specific hooks that should not be committed. Avoid `archived-extensions/`; Git history is the archive.

## Public repo caveats

- This repo is public.
- Do not commit auth, sessions, trust data, package state/caches, logs, run history, account-router state/cache, generated reports, or other runtime state.
- Do not add absolute local project paths to durable config. Use npm/git sources; keep local checkouts dev-only.
- `docs/` is ignored local scratch/reference material, not committed canonical documentation.
- `.poster/` is not yet classified; `.poster/output/` is generated and ignored.

## GitHub update discipline

- Do not use `git add .`; stage intentional files only.
- Keep `README.md`, `EXTENSIONS.md`, and `SKILLS.md` aligned with durable config changes.
- Before committing, review the scoped diff, validate changed JSON, run a secret-oriented grep over staged content, and confirm no generated/runtime files are staged.

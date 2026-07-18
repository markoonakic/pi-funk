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

Pi may update `lastChangelogVersion` in tracked `settings.json`. This is harmless bookkeeping: Pi records which release changelog has already been shown, and the repository appears dirty only because the live settings file is also Git-tracked. Do not commit that field as meaningful config or as a standalone/noise change. Host-local sidecars in otherwise linked directories are ignored by Git and remain machine-specific.

## Remaining-work decisions (2026-07-18)

The extension consolidation and standalone-repository cleanup are complete. The remaining work is governed by these decisions:

1. **Herdr and Nix are the final phase.** Last, update Herdr, replace the outdated Pi integration with the official current hook, remove the custom session-name sync hook, reconcile the Pi Nix pin, rebuild, and smoke-test lifecycle/subagent isolation. Do not mix this infrastructure phase into earlier extension work.
2. **Security and compatibility maintenance proceeds now.** Review and update the obsolete `pi-thinking-steps` dependency stack, upgrade Funky UI's vulnerable `diff` dependency, and process the green `pi-zza` dependency-update pull requests. Run this work from a fresh Pi instance in tab 1 of the existing Herdr `pi` workspace, reusing an existing pane rather than creating new topology.
3. **Moshi hardening is ignored for now.** Do not spend time on payload documentation, subagent suppression, or subprocess-error changes unless this decision is revisited.
4. **FFF standard-tool ownership is approved only after safe research.** Determine how FFF can own `find` and `grep` without losing Funky UI's current tool rendering, previews, expansion behavior, or general UI. Do not change ownership until the design is validated against both packages and fresh Pi startup.
5. **Custom Subagents remains unexposed.** Do not qualify, activate, publish, or replace Nico's active provider unless this decision is revisited.
6. **Package follow-ups are documented but deferred.** This includes adding GPT-5.6 to Fast Mode defaults, replacing Codex Usage's private Account Router state/cache reads with a stable contract, Peon Ping timing/network/relay polish, and explicit license decisions for owner-authored packages that currently lack licenses.
7. **Optional housekeeping is ignored.** Do not prioritize stale one-run package caches, the inactive Computer Use update, Rewind retention tuning, or `lastChangelogVersion` Git noise.

New XAI Tools and unified subscription-usage proposals are feature work, not consolidation debt.

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

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

The extension consolidation, standalone-repository cleanup, and Herdr/Nix finalization are complete. The current state and remaining work are governed by these decisions:

1. **Herdr and Nix finalization is complete.** The upstream Herdr flake input remains floating in `flake.nix` and reproducible through `flake.lock`; Herdr 0.7.4 with protocol 17 is active. The official Pi hook v6 remains vendor/installer-managed lifecycle/session authority. `@pi-zza/auto-session-name` owns one-time canonical Pi naming for unnamed root sessions, while `@pi-zza/herdr-session-name-sync` remains the separate presentation-only companion that mirrors Pi `/name` values into Herdr `display_agent` metadata. Structural restore succeeded, but only panes with valid persisted root-session references auto-resume.
2. **Security and compatibility maintenance is complete.** Funky UI now uses `diff` 8.0.4; Dependabot workflow updates #1–#3 landed; incompatible `@types/node` #4 was closed to preserve the Node 22.19 contract; and the `pi-zza` production audit was clean. `pi-thinking-steps` remains unchanged at official 1.0.11 because no safe official update exists. A vetted fork or removal requires separate authorization.
3. **The private Agent Team migration and source archival are complete.** `pi-zza` PR #13 landed as `c48f94f21a5376a73d26f6bddf43fbfcdafc5b4f` from private source revision `a757fa7ccd1c9a40691e2223ae7f91a7ae1e7cef`. The result is the private, inactive, independently testable `@pi-zza/agent-team`, absent from the root `pi.extensions` and live/global config. All 27 runtime/entrypoint files and 290 approved curated docs were preserved byte-identically; seven tests were adapted to Vitest; runtime/private/raw/generated boundaries are ignored. This makes no license or publication claim. `https://github.com/markoonakic/pi-agent-team` remains private and is now archived/read-only; its default `main` remains exactly `a757fa7ccd1c9a40691e2223ae7f91a7ae1e7cef`, without deletion, transfer, publication, or history rewriting. The local source clone remains preserved and clean. Deletion or unarchival would be a separate future decision.
4. **Moshi hardening is ignored for now.** Do not spend time on payload documentation, subagent suppression, or subprocess-error changes unless this decision is revisited.
5. **FFF standard-tool ownership is approved only after safe research.** Research found that Pi gives the first same-name tool registration ownership of both execution and extension rendering, so load-order changes alone cannot preserve Funky UI. The safest future design is to load FFF first in `override` mode for `find`/`grep` execution, stop Funky UI from registering those two executors, and route their presentation through Funky UI's existing renderer-dispatch seam with explicit adapters/tests for FFF's different result shapes. Validate synthetic ownership/rendering tests and an isolated fresh Pi startup before changing live ownership. No ownership or configuration change has been made.
6. **Custom Subagents remains unexposed.** Do not qualify, activate, publish, or replace Nico's active provider unless this decision is revisited.
7. **Package follow-ups are documented but deferred.** This includes adding GPT-5.6 to Fast Mode defaults, replacing Codex Usage's private Account Router state/cache reads with a stable contract, Peon Ping timing/network/relay polish, and explicit license decisions for owner-authored packages that currently lack licenses.
8. **Optional housekeeping is ignored.** Do not prioritize stale one-run package caches, the inactive Computer Use update, Rewind retention tuning, or `lastChangelogVersion` Git noise.

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

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

On Home Manager-managed hosts, `~/.pi/agent/models.json` may be a generated store symlink; verify `readlink -f ~/.pi/agent/models.json` resolves to this repo file. If it does not, apply the existing reviewed Home Manager activation path; do not replace the symlink manually.

## Isolated BB Pi profile

`profiles/bb/settings.json` defines a separate Pi profile at `~/.pi/bb-agent`. Its private settings are a writable copy, not a link to standalone settings. Pi authentication, model configuration, and runtime state stay separate; Pi auth stores are never copied or linked. Tool credentials may use explicit host-local references as documented below. Existing Herdr/Pi configuration remains unchanged.

The BB Home Manager module in `nixos-machines/modules/home/bb.nix` selects the Nix-managed Pi executable through `profiles/bb/launch.py`. Ambient Pi extensions, skills, prompt templates, themes and context-file discovery stay disabled. Account Router, Web Access, MCP adapter, FFF, native Codex compaction and BB's generated bridge are explicit extensions in the activated BB user unit; Agent Browser Session is an explicitly selected skill, and the native BB Accounts/Usage panel controls the separate profile. The mutable launcher explicitly adds RPIV Todo from the existing standalone installation to each new BB Pi runtime. Neither standalone TUI extensions nor Pi Processes are selected.

The launcher adds **Pi Lens only at approved exact working directories**, listed in private `~/.pi/bb-agent/lens-projects.json` (an array of absolute paths). Missing lists deny trust. Nested directories and managed worktrees need their own deliberate entry; symlink aliases resolve to the same directory. Approved entries receive Pi's `--approve`, including permission to honor project settings; other directories receive `--no-approve`, even when Pi would otherwise auto-trust a resource-free directory. This is a startup policy, not a filesystem sandbox. Review project-local configuration before adding a directory.

Lens reuses the canonical installed `npm:pi-lens` code at `~/.config/pi/.pi/npm/node_modules/pi-lens/dist/index.js` (qualified: **4.1.3**), not standalone Lens state. Keep that package installed and re-run qualification after updating it. `PI_LENS_HOME`, `PILENS_DATA_DIR` and `PI_LENS_CONFIG_PATH` point inside `~/.pi/bb-agent/lens`. The BB service provisions TypeScript and its language server through Nix. Interactive/automatic tool installation is disabled. This first diagnostics/navigation slice disables automatic formatting, autofix and test running via explicit Lens flags; deliberate tool calls remain available. Other languages need their servers provisioned separately.

`profiles/bb/AGENTS.md` is a relative symlink to `../../agent/AGENTS.md`, and `~/.bb/AGENTS.md` keeps the existing Home Manager link to that repo path. BB therefore uses the same standalone global agent policy, including the orchestrator default, allowed Flash/Luna/Sol/Astra models, and Simplified Technical English. BB resource and authentication isolation remains separate; this policy change does not merge profiles or state. New sessions receive the new policy; existing sessions are not hot-reloaded.

Pi startup network checks and telemetry are disabled. `PI_OFFLINE=1` does not prohibit later model requests. Profile separation is not a sandbox: both processes retain the user's filesystem access, and BB thread environment overrides remain authoritative. BB owns its sessions under `~/.bb/pi-bridge-sessions`; do not share them with standalone Pi. Keep one writer per worktree across both systems.

### Headless tool parity

The activated BB user unit reuses the installed standalone code for Web Access **0.28.0**, MCP adapter **2.32.1**, FFF **0.10.6**, and the reviewed `pi-zza` native-compaction overlay. The mutable launcher also selects the existing RPIV Todo **2.10.1** entry without changing the service unit. Keep those sources installed; package updates affect future launches and require requalification. Configuration/cache files live in `~/.pi/bb-agent`, not the standalone profile.

- **Web Access:** the private `web-search.json` uses the approved Exa → Parallel MCP → Gemini route, retains its browser-cookie opt-in/profile and HTTP → Firecrawl fetch policy, and keeps `workflow: "none"`. Like standalone, the Firecrawl key uses the supported `$FIRECRAWL_API_KEY` environment reference, not a copied token or command. Presence-only checks found no nonempty key in BB's effective environment or systemd provisioning; that optional backend is unavailable until separately provisioned. Hosted-fetch restrictions and cache-only Firecrawl behavior are unchanged. Real provider/cookie access remains untested; the configured route is not Codex-backed search. Explicit OpenAI searches use the BB Pi registry/auth path.
- **MCP:** `PI_MCP_CONFIG_MODE=exclusive` loads only the BB profile's `mcp.json`; `MCP_UI_VIEWER=none` suppresses host browser windows, not permission checks. The actual standalone resolver found **zero configured servers** in this config workspace and the BB extension workspace; old cached server entries are not configuration and were not imported. Project-specific MCP files elsewhere are not promoted globally. Select and review any desired server definitions before adding them to the BB config. Approval/elicitation requests still cancel/fail closed because BB cannot render Pi dialogs; no approval bypass is installed. MCP OAuth uses the machine credential store, not a profile-specific namespace.
- **FFF:** `override` registers FFF as BB's `find`/`grep` tools without terminal autocomplete. This installed version leaves multi-grep off unless `PI_FFF_MULTIGREP=1`, despite README examples. Explicit frecency/history paths stay inside the BB profile, avoiding implicit Neovim history reuse.
- **RPIV Todo:** the launcher explicitly selects the existing `@juicesharp/rpiv-todo` entry, which registers the same `todo` tool and `/todos` command as standalone Pi. Task history stays in each BB-owned Pi session. Its terminal widget output is not BB UI; the BB Custom UI renderer reconstructs successful `todo` calls into a composer card. Existing Pi runtimes keep their original extension set; start a new runtime to receive this selection.
- **Native compaction:** loaded after Router, preserving its Codex-only event channel and portable-summary fallback. BB settings match standalone automatic compaction (`enabled: true`, `reserveTokens: 100000`). Pi's BB-profile fallback is `openai-codex` / `gpt-6-astra` / `high`, and the BB-only model file contains only reviewed numeric context/output overrides for built-in OpenAI and OpenAI Codex models. BB's explicit thread choice and remembered per-project execution defaults take precedence. This project's stored BB choice remains `pi` / `openai-codex/gpt-6-astra` / `xhigh`: BB 0.41.0 exposes only a read API, and it remembers a new app-composer selection when that thread is created, so changing it to `high` without creating a paid thread is not supported. Existing thread selections stay unchanged. No paid thread, real model request, or compaction request was used for validation.

### Daily BB extension monitor

`profiles/bb/monitor-updates.py` is a **monitor-only** standard-library script for a BB script automation. It reads an explicit host-local inventory rather than BB's empty Pi package list. It checks public npm/GitHub metadata, installed versions/SHAs, dirty Git checkouts, deployed launcher selection, guarded local files, and the six actual Ponytail skill copies. Unknown or failed lookups are not reported as current. The shared `pi-zza` upstream may be inaccessible through public GitHub; that is a visible check failure, not permission to read credentials or silently use another source.

The reviewed inventory/configuration is private at `~/.bb/pi-update-monitor/config.json`; reports, exact-candidate review receipts and the latest daily result stay under its owner-only `state/` directory. The config specifies the server hostname, project/environment IDs, installed paths/source identities/owners, historical qualification identities, selection/file hashes, BB CLI and review model. State output is restricted to that private BB directory, outside worktrees/package stores, with symlink checks and atomic writes. These are accidental-write guards, not a sandbox against another process running as the same user.

The daily schedule is **09:00 UTC**. Checks require the local BB server host and never install, update, reset, approve lifecycle scripts, or restart anything. They do not use model tokens. New exact candidates can start one bounded, read-only BB review per day; previously submitted candidates are not reviewed again when another package changes. The review snapshot includes all consumer rows for each new exact candidate. Every daily report retains pending candidates and holds. A dispatch with an uncertain result is not retried automatically; inspect its private receipt and BB thread before any retry. A spawned review is not evidence that its model completed successfully.

All updates remain held for explicit approval and candidate qualification; shared code also needs isolation or both consumers' qualification. Notes/code review is not a safety certificate. Pi/BB core, BB-native plugins, standalone-only resources, activation and rollback implementation are outside this first phase. The older RPC fixture receipts do not qualify newer installed versions; current full-stack qualification remains pending. The existing standalone update skill is not a BB batch updater.

Inspect without saving or starting a review:

```bash
BB_PI_MONITOR_CONFIG="$HOME/.bb/pi-update-monitor/config.json" \
  python3 profiles/bb/monitor-updates.py --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s profiles/bb -p 'test_*.py'
```

BB stores a private copy of an automation script. After approved source changes and tests, refresh the stored script explicitly (do not point a daily job at a mutable worktree script):

```bash
bb automation update <automation-id> --project <project-id> \
  --script-file profiles/bb/monitor-updates.py --interpreter python3 --timeout 300000 \
  --env-json "{\"BB_PI_MONITOR_CONFIG\":\"$HOME/.bb/pi-update-monitor/config.json\"}"
```

No extension/skill selection changes are involved, so their catalogs remain unchanged.

### Ponytail skills

BB discovers real skill directories under `~/.bb/skills`; symlinks are not supported. Copy the six original Ponytail skills and their MIT license from the canonical installed upstream checkout:

```bash
python3 profiles/bb/sync-skills.py \
  "$HOME/.config/pi/.pi/git/github.com/DietrichGebert/ponytail" "$HOME/.bb/skills"
bb skill list --json
```

The copier refuses differing destinations or symlinks. Back up changed destination directories before explicitly replacing them after an upstream update. Skill bodies remain upstream-owned, not another local fork. Select/invoke Ponytail in BB; this does not install Pi's persistent mode extension or implement its TUI commands. Upstream help may describe controls for other hosts; BB invocation and selection apply here.

### BB naming and startup

The BB package is stock; the custom naming patch and its
`BB_CUSTOM_THREAD_NAMING=true` opt-in are gone. New root threads follow the
standalone `day.month-slug` convention; existing and manual titles are
preserved. The `thread-naming` plugin in `bb-extensions` owns naming and needs
no BB patch. A real Pi-backed thread passed automatic and forced naming, and the
naming worker was deleted after each run, on 2026-09-20.

With the preserved `JITI_FS_CACHE=false` guard, a cold approved Lens/tools launch
took 42 seconds. The bundled Pi provider therefore uses its existing readiness
budget (default 60 seconds) for the initial `get_state` request; ordinary requests
keep their 30-second timeout. This avoids disabling tools or weakening the guard.

Lens was also qualified at the approved BB-extension checkout using real RPC,
TypeScript diagnostics and navigation with no model or credentials. Existing
Homelab environments were not silently approved: project trust still requires
an explicit reviewed exact path.

### Qualification and activation

Additional credential-free checks:

```bash
python3 -m unittest discover -s profiles/bb -p 'test_*.py'
python3 profiles/bb/check-lens.py "$PI_EXECUTABLE" "$LENS_ENTRY" "$LSP_BIN_PATHS"
```

The Lens check uses a disposable trusted fixture, actual Pi RPC and Lens tool definitions, a preinstalled TypeScript language server, and empty auth. It verifies a real type error, definition navigation, lazy tool activation preserving built-ins, explicit Ponytail skill loading, and isolated state paths. Optional trailing extension-entry arguments exercise Lens alongside the selected headless tools; this combined fixture also passed. It does not prove browser rendering or model-driven diagnostics injection.

Ponytail skill copies are discoverable through BB. The reviewed Lens and headless-tools user unit was **activated on 2026-09-07** with the explicitly approved BB restart; standalone Pi was not reloaded. Native server/host health, effective launcher selection, Ponytail discovery and the read-only Router bridge passed. Credential-free real Pi RPC fixtures verified tool/hook loading and Lens diagnostics/navigation; these checks do not establish live model, search, browser-cookie authentication or compaction success. The private activation receipt records the exact unit, backup and rollback commands. Activate only the reviewed user unit, never unrelated dirty NixOS changes. Retain its `nix build --out-link` registered GC root while the live unit depends on it; an ordinary systemd symlink is not a registered root. Preserve Account Router, auth/state, pending reset guards and Funky overlays; never use real reset redemption for validation.

## Remaining-work decisions (2026-07-18)

The extension consolidation, standalone-repository cleanup, and Herdr/Nix finalization are complete. The current state and remaining work are governed by these decisions:

1. **Herdr and Nix finalization is complete.** The upstream Herdr flake input remains floating in `flake.nix` and reproducible through `flake.lock`; Herdr 0.7.4 with protocol 17 is active. The official Pi hook v6 remains vendor/installer-managed lifecycle/session authority. `@pi-zza/auto-session-name` owns one-time canonical Pi naming for unnamed root sessions, while `@pi-zza/herdr-session-name-sync` remains the separate presentation-only companion that mirrors Pi `/name` values into Herdr `display_agent` metadata. Structural restore succeeded, but only panes with valid persisted root-session references auto-resume.
2. **Security and compatibility maintenance is complete.** Funky UI now uses `diff` 8.0.4; Dependabot workflow updates #1–#3 landed; incompatible `@types/node` #4 was closed to preserve the Node 22.19 contract; and the `pi-zza` production audit was clean. `pi-thinking-steps` remains extension-disabled because no safe official update exists; its package source follows latest. A vetted fork or removal requires separate authorization.
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

The sole global goal driver is the `pi-codex-goal` package. It provides `/goal` and model-callable `create_goal`, `get_goal`, and `update_goal`; its state follows Pi session history across resume, fork, tree navigation, reload, and compaction. Do not load another goal driver alongside it.

Use `local-extensions/` only for untracked private experiments or machine-specific hooks that should not be committed. Avoid `archived-extensions/`; Git history is the archive.

## Extension updates

Configured extension sources normally follow latest: npm package names and Git default branches, without version or revision suffixes. The temporary exception is regular Pi's `pi-subagents`, pinned to `f6d2135ec2ca4010b83b7d5ee46774176d49d1e6` before a native-runner module-resolution regression that prevented Account Router from loading in children. Keep this pin until a replacement passes an authenticated child tool-loop test. Keep resource filters unchanged, including disabled extensions and the `pi-zza` eleven-file allowlist. The skill-only Herdr revision remains held to the host; this is not an extension pin. Dependency versions and package locks remain package-owned.

Funky UI's thinking view is currently activated as a reviewed local overlay in the managed `pi-zza` checkout, with native thinking visible. The old `pi-thinking-steps` extension remains disabled. Regular Pi also has a Router-only local overlay that combines local control/usage changes with published credential-refresh fix `51f9987` (PR #48). BB's separate Router and shared compaction code remain unchanged. Preserve local overlays before updating: wait for a release containing these changes, or explicitly back them up for reapplication. See `EXTENSIONS.md` for qualification details and the view commands.

After checking managed Git stores for local work, use Pi's native package updater:

```bash
pi update --extensions --no-approve
```

This updates global packages, including floating skill-only packages, without Pi core or project settings. Plain `pi update --extensions` also covers trusted exact-cwd project packages. For isolated project updates, run these at each configured root (see `EXTENSIONS.md`):

```bash
pi update npm:pi-lens --approve
pi update git:github.com/DietrichGebert/ponytail --approve
```

Targets match package identity across global and project scopes; these project identities have no global overlap. `update -l` is unsupported. Native Git reconciliation resets/cleans managed stores: preserve local work and stop on unexplained dirt first. Review blocked dependency lifecycle scripts rather than approving them automatically. Use `/skill:pi-config-update` for audit or approved batch preparation. Restart Pi after validation; do not reload a coordinating session mid-update.

Pi core/model catalogs and the host remain Nix-managed. Bare `pi update`, `--self`, `--all`, and `--models` are outside extension maintenance.

Regular Pi does not retain day-long subagent model-failure blocks. Its `extensions/subagent/config.json` sets `modelExclusions.defaultTtlMs` to `1`, the supported 1 ms expiry rather than an unsupported zero/off value. Restart Pi after changing this policy; running sessions retain their loaded policy and exclusion cache. This is separate from Account Router's provider quota cooldowns, which remain unchanged.

## Public repo caveats

- This repo is public.
- Do not commit auth, sessions, trust data, package state/caches, logs, run history, account-router state/cache, generated reports, or other runtime state.
- Do not add absolute local project paths to durable config. Use npm/git sources; keep local checkouts dev-only.
- `docs/` is ignored local scratch/reference material, not committed canonical documentation.
- `.poster/` is not yet classified; `.poster/output/` is generated and ignored.

## Browser direction

The custom shared-browser integration is retired from source. Prefer BB’s native Mac manual browser path; agent browser automation requires a compatible official release and is not promised by stable 0.42.1. Host removal still requires a reviewed maintenance activation; retained profile data is not purged.

## GitHub update discipline

- Do not use `git add .`; stage intentional files only.
- Keep `README.md`, `EXTENSIONS.md`, and `SKILLS.md` aligned with durable config changes.
- Before committing, review the scoped diff, validate changed JSON, run a secret-oriented grep over staged content, and confirm no generated/runtime files are staged.

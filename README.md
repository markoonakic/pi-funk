# Pi config

`~/.config/pi` is the canonical public Git repo for reviewed, durable Pi configuration. The private Pi runtime root remains `~/.pi/agent`; the repo must not be moved there.

## Prepared Pi 1.4 cutover (2026-10-26)

Source preparation is not deployment. The audit found Pi **1.1.0** and BB
**0.46.1** running. The approved targets are Pi **1.4.0**, Subagents **0.83.0**,
Goal **0.6.1**, and BB **0.47.1**. Package stores and copied BB skills have not
been updated by this source change. Nix remains the owner of Pi and BB; retain
Node **>=24** for Goal, including when using Pi's upstream Nix package.

The Subagents declaration now tracks upstream instead of the old 0.67 pin.
**Do not start or reload regular Pi with online package reconciliation before
the coordinated cutover.** Its settings link points here. Current Subagents
requires Pi >=1.2; old Goal does not handle custom-message starts in new Pi.
Update core, Subagents and Goal together with the candidate Pi executable.
The reviewed Subagents revision is `d9c5ca29d881ee173681cafb66af1cc774285276`;
tracking the default branch is not a claim that later commits are qualified.
The archived, explicitly obsolete Shaping Skills source is removed. Herdr's
skill-only pin and all retained resource filters remain unchanged.

The intended single command is `scripts/update-ai-stack` in the Nix owner
repository. Run it only from an independent terminal, after source and candidate
checks pass. Stop BB and close Pi before changing their shared package stores.
Do not activate unrelated dirty Nix changes. The command must report failed or
held updates rather than restart an old core with partially updated packages.
No backup process, rollback script, or automatic commit is required. Lens
**4.4.5** supports Pi **>=0.86.1 <1.5.0**; recheck this before later core updates.

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

## Gateway model discovery

The local `extensions/cliproxy-models/` adapter discovers the gateway's available
chat models for **Codex**, **Antigravity**, **OpenCode Go**, and **Command Code**.
Standalone Pi loads it normally; BB's launcher selects it explicitly. Internal
provider IDs stay `openai-codex`, `antigravity`, `cliproxy-go`, and `cliproxy`.
Model names stay clean. BB Custom UI's frontend content script formats the
native picker source qualifier with the friendly provider name; BB core and
routing IDs are unchanged. Disabling that UI plugin restores the raw qualifier.
Overlapping models remain distinct routes. Muse Spark is hidden from both Go
and Command Code; no account is removed.

`models.json` and the isolated BB copy now contain provider connection settings
and reviewed Codex `modelOverrides`. Model arrays are no longer needed.
GPT-6.1 Terra uses the same 1,000,000 context and 128,000 output override as the
other configured Codex models. Its published reasoning map and image support
are explicit overrides because the Nix-managed Pi 1.4 catalog predates Terra.
Remove those capability overrides once the installed catalog supplies them;
retain the deliberate context/output override. Pi catalog metadata and the
adapter's reviewed gateway compatibility metadata supply other defaults. Unknown
models use conservative client defaults, not guessed upstream maxima. The private per-profile gateway
key and cached model inventory never belong in Git.

Discovery runs at startup. Use `/gateway-models-refresh` in an existing Pi
runtime. BB also has a separate model-picker cache of up to ten minutes. New
runtimes receive extension changes; do not reload a coordinating session during
work. See [the adapter documentation](extensions/cliproxy-models/README.md) for
source mapping, cache behavior, metadata boundaries, and credential-free tests.

## Isolated BB Pi profile

`profiles/bb/settings.json` defines a separate Pi profile at `~/.pi/bb-agent`. Its private settings are a writable copy, not a link to standalone settings. Pi authentication, model configuration, and runtime state stay separate; Pi auth stores are never copied or linked. Tool credentials may use explicit host-local references as documented below. Existing Herdr/Pi configuration remains unchanged.

The BB Home Manager module in `nixos-machines/modules/home/bb.nix` selects the Nix-managed Pi executable through `profiles/bb/launch.py`. `--no-extensions` disables automatic discovery, not explicitly selected `--extension` entries. This keeps standalone/Herdr TUI extensions out of BB. The reviewed launcher explicitly selects Web Access, FFF, native Codex compaction, `builtin:codemode`, and `builtin:mcp`; BB also injects its generated bridge extensions. The mutable launcher adds Pi Processes core and the local gateway model-discovery adapter. It resolves the Web Access package through its manifest, so published `dist/` entries work without loading the old source entry. Account Router, RPIV Todo, and Pi Processes terminal log/dock overlays are not selected. Pi skill, prompt-template, theme and context-file discovery remain disabled; BB's own agent instructions and skills are separate.

Native Code Mode is additive: `defaultTools: ["+codemode"]` keeps ordinary tools available. Its built-in identifier belongs directly in `bridgeArgs`, not the file-based `toolEntries` readability checks. Native MCP and Code Mode are selected explicitly by the deployed Home Manager unit; the 2026-10-26 service check found no drop-ins. The launcher still removes managed adapter paths from older bridge arguments. Existing Pi runtimes keep their loaded tools until they exit.

The launcher adds **Pi Lens only at approved exact working directories**, listed in private `~/.pi/bb-agent/lens-projects.json` (an array of absolute paths). Missing lists deny trust. Nested directories and managed worktrees need their own deliberate entry; symlink aliases resolve to the same directory. Lens-approved entries receive Pi's `--approve`, including permission to honor project settings. Native MCP project approval is separate: an exact canonical directory mapped to `true` in the BB profile's native `trust.json` also receives `--approve`, but does not select Lens. Parent trust does not extend the launcher's exact-path policy. Other directories receive `--no-approve`, even when Pi would otherwise auto-trust a resource-free directory. This is a startup policy, not a filesystem sandbox. Review project-local configuration before adding a directory.

Lens reuses the canonical installed `npm:pi-lens` code at `~/.config/pi/.pi/npm/node_modules/pi-lens/dist/index.js` (installed at the 2026-10-26 audit: **4.3.0**; prepared target: **4.4.5**), not standalone Lens state. Keep that package installed and re-run qualification after updating it. `PI_LENS_HOME`, `PILENS_DATA_DIR` and `PI_LENS_CONFIG_PATH` point inside `~/.pi/bb-agent/lens`. The BB service provisions TypeScript and its language server through Nix. Interactive/automatic tool installation is disabled. This first diagnostics/navigation slice disables automatic formatting, autofix and test running via explicit Lens flags; deliberate tool calls remain available. Other languages need their servers provisioned separately.

`profiles/bb/AGENTS.md` is a relative symlink to `../../agent/AGENTS.md`, and `~/.bb/AGENTS.md` keeps the existing Home Manager link to that repo path. BB therefore uses the same standalone global agent policy, including the orchestrator default, allowed Flash/Luna/Sol/Astra models, and Simplified Technical English. BB resource and authentication isolation remains separate; this policy change does not merge profiles or state. New sessions receive the new policy; existing sessions are not hot-reloaded.

Pi startup network checks and telemetry are disabled. `PI_OFFLINE=1` does not prohibit later model requests. Profile separation is not a sandbox: both processes retain the user's filesystem access, and BB thread environment overrides remain authoritative. BB owns its sessions under `~/.bb/pi-bridge-sessions`; do not share them with standalone Pi. Keep one writer per worktree across both systems.

### Headless tool parity

The selected shared code is Web Access **0.35.0**, Pi Processes **0.13.1** core, FFF **0.11.0**, and the reviewed `pi-zza` native-compaction source. Lens **4.3.0** remains selected only at approved exact directories. MCP uses the Nix Pi core's native implementation in both profiles (installed **1.1.0**, prepared target **1.4.0**). The legacy adapter package declarations and native-MCP exclusions are removed. Server settings and OAuth state remain profile-specific.

Earlier qualification record: Pi **1.0.2** was tested with the full BB selection in real RPC mode, including a native Code Mode call, FFF search, process listing, MCP status/scripting, Lens diagnostics and definition navigation. The complete standalone profile also passed an isolated startup check with unchanged settings. These checks use a local deterministic model fixture, not real credentials or a paid provider. Activation, real provider authentication, UI rendering, and resumed live threads require separate post-activation checks.

- **Web Access:** the private `web-search.json` uses the approved Exa → Parallel MCP → Gemini route, retains its browser-cookie opt-in/profile and HTTP → Firecrawl fetch policy, and keeps `workflow: "none"`. Like standalone, the Firecrawl key uses the supported `$FIRECRAWL_API_KEY` environment reference, not a copied token or command. Presence-only checks found no nonempty key in BB's effective environment or systemd provisioning; that optional backend is unavailable until separately provisioned. Hosted-fetch restrictions and cache-only Firecrawl behavior are unchanged. Real provider/cookie access remains untested; the configured route is not Codex-backed search. Explicit OpenAI searches use the BB Pi registry/auth path.
- **MCP:** Native Pi reads `<agent-dir>/mcp.json` and the trusted exact-cwd `.pi/mcp.json`. It does not discover root `.mcp.json` or parent project files. A project can alias a credential-free shared file through `.pi/mcp.json`; private bearer-header commands stay in each agent profile. Personal servers are disabled globally and enabled only through reviewed project overrides. Native Code Mode replaces `mcp` and `mcpScript`: discover tools with `searchTools()` and call `tools.mcp__<server>__<tool>()`. Results are MCP `CallToolResult` objects, not adapter wrappers. Native OAuth uses each profile's `mcp-auth.json`; old adapter credentials are preserved but not silently copied or decrypted. Native MCP connects every enabled server at startup and does not provide the adapter's Apps, sampling, elicitation, prompt-template, or Tasks features. Web Access's Parallel MCP provider is independent of the removed adapter.
- **FFF:** `override` registers FFF as BB's `find`/`grep` tools without terminal autocomplete. This installed version leaves multi-grep off unless `PI_FFF_MULTIGREP=1`, despite README examples. Explicit frecency/history paths stay inside the BB profile, avoiding implicit Neovim history reuse.
- **RPIV Todo:** remains installed for standalone Pi, but the current BB launcher does not select it. This update does not add it. BB Custom UI's optional Todo renderer is not proof that the Pi `todo` tool is loaded.
- **Pi Processes:** the launcher loads the shared package's `extensions/processes/index.ts`. The `process` tool supports background process start/list/output/write/stop/update/clear. Terminal log and dock overlays are not loaded in BB. New Pi runtimes receive this selection; existing runtimes are not reloaded.
- **Native compaction:** explicitly loaded, preserving its Codex-only event channel and portable-summary fallback. Account Router is not part of BB's current selection. BB settings match standalone automatic compaction (`enabled: true`, `reserveTokens: 100000`). Pi's BB-profile fallback is `openai-codex` / `gpt-6-astra` / `high`, and the BB-only model file contains reviewed Codex context/output overrides and the Terra capability override described above. BB's explicit thread choice and remembered per-project execution defaults take precedence. This project's stored BB choice remains `pi` / `openai-codex/gpt-6-astra` / `xhigh`: BB 0.41.0 exposes only a read API, and it remembers a new app-composer selection when that thread is created, so changing it to `high` without creating a paid thread is not supported. Existing thread selections stay unchanged. No paid thread, real model request, or compaction request was used for validation.

### Updating BB's shared extension packages

BB's Pi package list is empty. Its explicit shared code comes from the regular
profile and the Pi config project's Lens package. Updating the BB profile does
not update these tools. Native MCP and Code Mode ship with the Nix Pi core.

Use the global and exact-project commands in [Extension updates](#extension-updates)
with the absolute candidate Pi executable. First close regular Pi and stop BB
from an independent terminal. Inspect managed Git stores for source edits or
local-only commits; Pi's updater resets and cleans these stores. Stop on
unapproved changes, rather than discard them. The audited active `pi-zza` source
matches upstream and has no tracked source overlay; an untracked generated lock
file is not an overlay to restore. The gateway adapter remains repo-owned.

Verify package versions and run candidate launcher/MCP/Lens checks. Start fresh
BB Pi children only after the coordinated core and package cutover.

### Manual updates

The BB Maintenance dashboard, sensors, watchdog, and daily extension monitor
are removed. No maintenance automation is installed. Check and update packages
manually with the commands above. Updates, builds, and activation still need
explicit approval.

### Ponytail skills

BB discovers real skill directories under `~/.bb/skills`; symlinks are not supported. Copy the six original Ponytail skills and their MIT license from the canonical installed upstream checkout:

```bash
python3 profiles/bb/sync-skills.py \
  "$HOME/.config/pi/.pi/git/github.com/DietrichGebert/ponytail" "$HOME/.bb/skills"
bb skill list --json
```

The copier updates only the six named `SKILL.md` files and their licenses in place. It refuses source-file symlinks, destination symlinks (including ancestors), and non-regular destination files. It validates the full copy list first and leaves unrelated skills and extra files untouched. Run it only during offline cutover, after updating the project's Ponytail checkout; the source preparation does not copy runtime skills. Skill bodies remain upstream-owned, not another local fork. Select/invoke Ponytail in BB; this does not install Pi's persistent mode extension or implement its TUI commands. Upstream help may describe controls for other hosts; BB invocation and selection apply here.

### BB naming and startup

The BB package has no custom naming patch; its
`BB_CUSTOM_THREAD_NAMING=true` opt-in is gone. Nix packaging and the ACP/OMP
normalizer are separate, retained changes. New root threads follow the
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
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s profiles/bb -p 'test_*.py'
node --test profiles/bb/test_moshi_hooks.mjs profiles/bb/test_gateway_*.mjs
python3 profiles/bb/check-mcp.py "$PI_EXECUTABLE"
python3 profiles/bb/check-lens.py "$PI_EXECUTABLE" "$LENS_ENTRY" "$LSP_BIN_PATHS"
```

The MCP check uses disposable native configuration, a local stdio server, a deterministic local model stub, and the unmodified Code Mode implementation to check discovery and tool calls without real credentials, network access, or an external model request. Live `pi mcp list` checks require saved trust in the selected profile; skipped project files are not a successful project validation.

The Lens check uses a disposable trusted fixture, actual Pi RPC and Lens tool definitions, a preinstalled TypeScript language server, and empty auth. It verifies a real type error, definition navigation, lazy tool activation preserving built-ins, explicit Ponytail skill loading, and isolated state paths. Optional trailing extension-entry arguments exercise Lens alongside the selected headless tools; this combined fixture also passed. It does not prove browser rendering or model-driven diagnostics injection.

Earlier activation record: Lens and the headless-tools unit were activated on
2026-09-07. Those fixture results are not Pi 1.4 qualification. At the
2026-10-26 audit, BB runs 0.46.1 with Pi 1.1.0, native MCP and no service drop-in.
Account Router is not selected. After the approved cutover, verify the live unit,
bridge executable, fresh children and plugin health; a successful source build
is not proof of deployment. Keep auth/state unchanged and never use real quota
redemption or a paid request for a credential-free check.

## Remaining-work decisions (2026-07-18)

The extension consolidation, standalone-repository cleanup, and Herdr/Nix finalization are complete. The current state and remaining work are governed by these decisions:

1. **Herdr and Nix finalization is complete.** The upstream Herdr flake input remains floating in `flake.nix` and reproducible through `flake.lock`; Herdr 0.7.4 with protocol 17 is active. The official Pi hook remains vendor/installer-managed lifecycle/session authority (the current local header reports integration 9). `@pi-zza/auto-session-name` owns one-time canonical Pi naming for unnamed root sessions, while `@pi-zza/herdr-session-name-sync` remains the separate presentation-only companion that mirrors Pi `/name` values into Herdr `display_agent` metadata. Structural restore succeeded, but only panes with valid persisted root-session references auto-resume.
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

The reviewed `extensions/cliproxy-models/` provider adapter is also kept here:
its metadata and tests belong to this repository, while credentials and catalog
cache stay in the private profile. It adds no daemon or tool provider.

The sole global goal driver is the `pi-codex-goal` package. It provides `/goal` and model-callable `create_goal`, `get_goal`, and `update_goal`; its state follows Pi session history across resume, fork, tree navigation, reload, and compaction. Do not load another goal driver alongside it.

Use `local-extensions/` only for untracked private experiments or machine-specific hooks that should not be committed. Avoid `archived-extensions/`; Git history is the archive.

## Extension updates

Configured extension sources track npm releases or Git default branches without
version suffixes. Subagents tracking is prepared for the coordinated Pi 1.4
cutover described above, not qualified for the still-installed Pi 1.1. Keep all
retained filters unchanged, including disabled `pi-thinking-steps` and the
`pi-zza` ten-file allowlist (nine extensions; Funky UI has two entries). Account
Router is not selected and the audited active `pi-zza` has no tracked source
overlay. Do not restore historical Router/Funky patches during updates.

Herdr's skill-only declaration remains pinned to host revision
`7b116c05bfda646af39d2524c54e70c751f57ee8`. The installed skill checkout differed
at audit time; native update reconciles it to this declaration, not upstream
latest. Dependency versions and package locks remain package-owned.

After the offline-cutover preconditions above, set `PI_EXECUTABLE` to the absolute
candidate Nix Pi executable. These commands are not run during source preparation:

```bash
env -u PI_OFFLINE PI_CODING_AGENT_DIR="$HOME/.pi/agent" \
  "$PI_EXECUTABLE" update --extensions --no-approve
```

This updates configured global packages and skill sources, not Pi core or
project settings. Use the exact approved project roots listed in `EXTENSIONS.md`
for each project package update:

```bash
cd "$APPROVED_PROJECT_ROOT"
env -u PI_OFFLINE PI_CODING_AGENT_DIR="$HOME/.pi/agent" \
  "$PI_EXECUTABLE" update npm:pi-lens --approve
env -u PI_OFFLINE PI_CODING_AGENT_DIR="$HOME/.pi/agent" \
  "$PI_EXECUTABLE" update git:github.com/DietrichGebert/ponytail --approve
```

Global Matt Pocock skills also supply Spona's filter delta. Do not update an
unused project cache as a second active owner. Copy the six BB Ponytail skills
only after the canonical project source updates. No package update enables
`pi-thinking-steps`, RPIV tools in BB, or inactive Computer Use.

Targets match package identity across global and project scopes; these project identities have no global overlap. `update -l` is unsupported. Native Git reconciliation resets/cleans managed stores: preserve local work and stop on unexplained dirt first. Review blocked dependency lifecycle scripts rather than approving them automatically. Use `/skill:pi-config-update audit` for inventory only; its older preparation instructions are not the coordinated cutover procedure. Use the Nix owner's update command for this cutover. Restart Pi after validation; do not reload a coordinating session mid-update.

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

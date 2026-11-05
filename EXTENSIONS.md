# Pi extensions catalog

This file documents Pi extensions/packages known to this setup. It is documentation only; runtime loading is controlled by `settings.json`, project `.pi/settings.json` files, or an explicit `pi -e` invocation.

## Prepared update, not deployed (2026-10-26)

Source policy is prepared for Pi 1.4.0 with Subagents 0.83.0 and Goal 0.6.1.
The installed core remains Pi 1.1.0 until the offline Nix cutover. Package stores
are unchanged. Do not start or reload regular Pi with online reconciliation
until core and packages are updated together. See [the cutover policy](README.md#prepared-pi-14-cutover-2026-10-26).

## Runtime loading

- **Global live config:** `settings.json`
- **Project-local config:** `.pi/settings.json`
- **One-run explicit load:** `pi -e <package-or-path>`
- **BB profile:** Automatic Pi resource discovery is disabled with `--no-extensions`, but explicit extension entries still load. The selected shared code is Web Access 0.35.0, Pi Processes 0.13.1 core, FFF 0.11.0 in `override` mode, native Codex compaction, and the local gateway model adapter. Lens 4.3.0 is selected only at approved exact working directories, with separate state and no automatic formatting/autofix/tests or tool installation. Native Code Mode and native MCP replace the npm MCP adapter in both profiles. The launcher's native-MCP selection also handles arguments retained by an older BB daemon, without restarting active threads. Account Router, RPIV Todo and terminal log/dock overlays are not selected. Earlier Pi 1.0.2 checks passed real RPC tool calls and Lens diagnostics/navigation; they do not qualify the prepared Pi 1.4 target. Native MCP configuration is selected for new runtimes; existing runtimes keep their loaded extensions. Source checks alone do not prove live UI, authentication or resumed-session behavior. See `README.md#isolated-bb-pi-profile`.

### Native gateway model discovery

`extensions/cliproxy-models/index.ts` is loaded by standalone Pi and explicitly by
`profiles/bb/launch.py`. It registers native providers named **Codex**,
**Antigravity**, **OpenCode Go**, and **Command Code**, retaining their existing
technical IDs. Startup reads CLIProxyAPI's available chat catalog; the
`/gateway-models-refresh` command refreshes an existing runtime. Model names stay
clean; BB Custom UI formats the separate source qualifier through its content
script, without changing core or routing IDs. Muse Spark is excluded from Go
and Command Code, and the current
`models.json` keeps only Codex per-model context/output overrides. See
[the adapter documentation](extensions/cliproxy-models/README.md) for metadata
sources, conservative defaults, private cache isolation, and the BB picker TTL.
This is a model-provider adapter, not a replacement for BB's native usage plugin.
For the Pi 1.4 Nix layout, it resolves pi-ai metadata through Node's package
resolver rather than assuming pi-ai is nested inside the coding-agent package.

## Status meanings

- **global** — enabled in the live global config
- **project-only** — enabled only at named project roots
- **one-run** — installed or fetchable, but loaded only with `pi -e`
- **inactive** — preserved but deliberately not loaded
- **removed** — no longer configured

## How to enable

### Global

Add to `settings.json`:

```json
{
  "packages": ["npm:example-package"]
}
```

### Project-only

Add to `.pi/settings.json`:

```json
{
  "packages": ["npm:example-package"]
}
```

### One-run explicit load

```bash
pi -e npm:example-package
```

## Consolidated `pi-zza` catalog

Nine custom extensions are loaded from the unpinned private source `git:git@github.com:lmilojevicc/pi-zza`. The source follows its default `main` branch. For a targeted update after checking the managed checkout for local work:

```bash
pi update git:git@github.com:lmilojevicc/pi-zza --no-approve
```

For normal batch updates, follow the unpinned-extension policy and native commands in `README.md#extension-updates`.

The 2026-10-26 audit found no tracked source overlay in the active checkout.
Do not restore old Router or Funky UI patches. Still check for new local work
before each update, because native Git reconciliation resets and cleans the store.

Global settings use an exact ten-file allowlist. Funky UI intentionally owns two entrypoints; the other eight active extensions own one each:

- `packages/auto-session-name/src/index.ts` — Auto Session Name
- `packages/codex-native-compaction/extensions/codex-native-compaction.ts` — Codex Native Compaction
- `packages/herdr-session-name-sync/src/index.ts` — Herdr Session Name Sync
- `packages/root-resume/extensions/root-resume.ts` — Root Resume
- `packages/codex-usage/extensions/codex-usage.ts` — Codex Usage
- `packages/funky-ui/extensions/index.ts` — Funky UI tool/message rendering
- `packages/funky-ui/extensions/funky-ui.ts` — Funky UI header/footer chrome and thinking view
- `packages/working-line/src/index.ts` — Working Line
- `packages/codex-fast-mode/index.ts` — Codex Fast Mode
- `packages/peon-ping/src/index.ts` — Peon Ping

The filter deliberately excludes Funky UI's dormant spinner entrypoint. Working Line remains the sole owner of `ctx.ui.setWorkingMessage()`. Custom Subagents is preserved in `pi-zza` as `@pi-zza/subagents` but remains absent from the root manifest and active allowlist.

Migration provenance, frozen source revisions, behavior reductions, licenses, and attributions are recorded in `pi-zza/docs/migration-provenance.md`.

## Global

Durable global entries use npm/git sources. Local checkouts under `/home/marko/Projects/...` are development copies, not global runtime sources. Skill-only package entries are cataloged in `SKILLS.md`.

### `pi-zza` extensions

- **Auto Session Name** — Names an unnamed interactive root session after a successful prompt using a bounded detached model request. Failed naming requests retry after later successfully completed prompts, up to five automatic attempts; there is no deterministic fallback. `/rename` retries manually without consuming the automatic budget. Manual names and clears remain authoritative; subagent sessions are excluded.
- **Codex Native Compaction** — Uses Codex's native server-side compaction for eligible OpenAI Codex sessions.
- **Herdr Session Name Sync** — Mirrors Pi `/name` values into Herdr presentation metadata for the Agents sidebar and pane-border agent label; Herdr's official Pi integration remains lifecycle/session authority.
- **Root Resume** — Adds `/rr` and `/root-resume`, a root-only fuzzy session manager. Deletion is root-only; cascade deletion was intentionally removed.
- **Codex Usage** — Adds `/codex-usage` and `Ctrl+Shift+U` for native Codex usage windows. Reset-credit details are read-only; consume/redemption behavior was intentionally removed.
- **Funky UI** — Combines Claude-style tool/message rendering, header/footer chrome, and an old-style thinking tree with semantic icons and wrapped labels. `/funky-thinking collapsed|summary|expanded|raw` selects the view; `steps` remains an alias for the default `summary`. `Alt+T` cycles the tree views. Modes are saved on the session branch and survive reload; new sessions default to `summary`. Native thinking is visible (`hideThinkingBlock: false`); `Ctrl+T` still controls visibility. Only its two active entrypoints are loaded. Run `/reload` after activation.
- **Working Line** — Shows a compact working line and final turn summary in the TUI.
- **Codex Fast Mode** — Adds `/fast` for configured OpenAI Codex models by setting `service_tier: "priority"`. Machine-local enablement remains in the ignored sidecar.
- **Peon Ping** — Adds `/peon`, sound packs, and desktop lifecycle notifications. Config/downloaded packs remain under `~/.config/peon-ping`; subagent sounds are suppressed by default.

### Other global extensions

- `npm:pi-codex-goal` — Codex-style goal tracking with `/goal` plus model-callable `create_goal`, `get_goal`, and `update_goal`; goal state follows Pi session history across resume, fork, tree navigation, reload, and compaction.
- `npm:@howaboua/pi-auto-trees` — External upstream package adding `/marker` and `/end` for incremental long-running session workflows; no custom delta is maintained in `pi-zza`.
- `git:github.com/nicobailon/pi-subagents` — Global provider for helper agents, workflows, async runs, and status UI. Default-branch tracking is prepared for Pi 1.4 with reviewed 0.83.0 source (`d9c5ca29d881ee173681cafb66af1cc774285276`); it requires Pi >=1.2. The installed 0.67.0 checkout is unchanged until offline cutover. Qualify host aliases and foreground/background child routing with the candidate before use; do not update this package under the old core. Regular Pi retains `modelExclusions.defaultTtlMs: 1` in `extensions/subagent/config.json` (1 ms expiry, not a true disable switch).
- `npm:pi-web-access` — Canonical upstream web search, content fetching, and opt-in browser-cookie Gemini Web research tools.
- `npm:@ff-labs/pi-fff` — FFF file indexing and fast file discovery.
- `npm:pi-rewind-hook` — Rewind/checkpoint support using hidden session metadata and `refs/pi-rewind/store` without checkpoints on ordinary read-only resume.
- `npm:@aliou/pi-processes` — Background process, watcher, server, and log management. BB explicitly loads its core entry from the shared standalone installation through `profiles/bb/launch.py`; terminal log/dock overlays remain standalone-only. Update this shared package in the standalone Pi scope, with `PI_OFFLINE` unset.
- `npm:pi-intercom` — Direct messaging between local Pi sessions.
- `npm:pi-thinking-steps` — Package source follows latest, but its extension stays globally disabled pending compatibility qualification.
- `npm:@juicesharp/rpiv-todo` — Model-managed task lists, `/todos`, and an above-editor task overlay.
- `npm:@juicesharp/rpiv-btw` — Tool-less side questions via `/btw` without polluting the main transcript.
- `npm:@juicesharp/rpiv-ask-user-question` — Structured clarifying questions with options, previews, multi-select, and review/submit UI.
- `extensions/moshi-hooks.ts` — Ignored machine-local Moshi hook; intentionally absent from durable shared config. Its prepared guard sends `UserPromptSubmit` only when the event has a string prompt, not for Pi >=1.2 custom-message starts. `profiles/bb/test_moshi_hooks.mjs` checks this with a fake subprocess sender.

## Project-only

Pi Lens and Ponytail are loaded only from `.pi/settings.json` at these exact roots:

- `/home/marko/.config/pi`
- `/home/marko/spona`
- `/home/marko/homelab`

The development `pi-zza` checkout has no `.pi/settings.json`; it is not an opted-in project scope.

Pi project settings are exact-cwd settings. Child repositories under Spona and Homelab do not inherit the umbrella settings; `/home/marko/homelab/homelab-private` is not separately opted in.

Other known project-local candidates, not globally loaded:

- `npm:@steel-experiments/pi-steel` — Steel browser automation.
- `npm:pi-annotate` — Browser-based visual annotation workflow.
- `npm:pi-better-openai` — OpenAI subscription workflow helper; its Codex-auth image generation is the useful subset here.
- `npm:pi-hosts` — SSH host inventory and remote execution; reconsider after its old pinned Pi dependency is updated.
- `npm:@marcfargas/pi-test-harness` — Extension test library; use as a repo-local dev dependency, not a runtime package.

## One-run only

These packages are not globally configured:

```bash
pi -e git:github.com/davebcn87/pi-autoresearch
pi -e git:github.com/kostyay/pi-k-excalidraw
pi -e npm:@injaneity/pi-computer-use
```

Computer Use remains installed but inactive. Autoresearch and Excalidraw are fetched on demand.

## Optional browser extensions

`pi-agent-browser-native` remains optional pending lifecycle/version qualification; the existing Computer Use extension is unchanged. The custom browser integration is retired from source.

## Inactive and unexposed

- `@pi-zza/account-router` — Not selected in either the regular Pi allowlist or BB launcher. Old local-overlay notes are historical, not update instructions. Private state and inactive checkouts are unchanged.

- `@pi-zza/agent-team` — Private, inactive, and independently testable; absent from the root `pi.extensions` and live/global config. `pi-zza` PR #13 (`c48f94f21a5376a73d26f6bddf43fbfcdafc5b4f`) preserves the reviewed migration from private source revision `a757fa7ccd1c9a40691e2223ae7f91a7ae1e7cef`. This makes no license or publication claim. `https://github.com/markoonakic/pi-agent-team` remains private and is archived/read-only at that exact default `main`; it was not deleted, transferred, made public, or rewritten. Its local source clone remains preserved and clean. Deletion or unarchival would require a separate future decision.
- `@pi-zza/subagents` — Custom Subagents source migrated from archived `markoonakic/pi-subagents@140e4bc8e4dacdc3250eb8e774a414120efc1ce4`. It remains absent from the root manifest and active settings until separately qualified and approved. Nico Bailon's package remains the active global Subagents provider.

## Removed from active configuration

- `npm:pi-mcp-adapter` — Replaced by Pi's native `builtin:mcp` and `builtin:codemode`. Private profile server definitions use `mcp.json`; reviewed project definitions use exact-cwd `.pi/mcp.json`. Old OAuth credentials remain outside Git for recovery.

- Standalone migrated owners: `markoonakic/pi-account-router`, `pi-root-resume`, `pi-codex-usage`, `pi-funky-ui`, `pi-codex-fast-mode`, and `pi-peon-ping` are archived; their implementations moved to `pi-zza`. Account Router is no longer selected; the other listed implementations remain selected. The corresponding local checkouts were removed.
- `markoonakic/pi-working-line` remains public for downstream compatibility, but its local standalone checkout was removed and active development moved to `pi-zza`.
- `npm:pi-boomerang`
- `npm:pi-messenger`
- `npm:pi-design-deck`
- `git:github.com/nicobailon/visual-explainer`
- `npm:pi-poster`
- `git:github.com/omerxx/pi-head`

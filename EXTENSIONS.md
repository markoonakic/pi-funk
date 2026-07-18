# Pi extensions catalog

This file documents Pi extensions/packages known to this setup. It is documentation only; runtime loading is controlled by `settings.json`, project `.pi/settings.json` files, or an explicit `pi -e` invocation.

## Runtime loading

- **Global live config:** `settings.json`
- **Project-local config:** `.pi/settings.json`
- **One-run explicit load:** `pi -e <package-or-path>`

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

Seven custom extensions are loaded from the unpinned private source `git:git@github.com:lmilojevicc/pi-zza`. The source follows its default `main` branch, so ordinary updates work with:

```bash
pi update --extensions
```

Global settings use an exact eight-file allowlist. Funky UI intentionally owns two entrypoints; the other six active extensions own one each:

- `packages/account-router/src/index.ts` — Account Router
- `packages/root-resume/extensions/root-resume.ts` — Root Resume
- `packages/codex-usage/extensions/codex-usage.ts` — Codex Usage
- `packages/funky-ui/extensions/index.ts` — Funky UI tool/message rendering
- `packages/funky-ui/extensions/funky-ui.ts` — Funky UI header/footer chrome
- `packages/working-line/src/index.ts` — Working Line
- `packages/codex-fast-mode/index.ts` — Codex Fast Mode
- `packages/peon-ping/src/index.ts` — Peon Ping

The filter deliberately excludes Funky UI's dormant spinner entrypoint. Working Line remains the sole owner of `ctx.ui.setWorkingMessage()`. Custom Subagents is preserved in `pi-zza` as `@pi-zza/subagents` but remains absent from the root manifest and active allowlist.

Migration provenance, frozen source revisions, behavior reductions, licenses, and attributions are recorded in `pi-zza/docs/migration-provenance.md`.

## Global

Durable global entries use npm/git sources. Local checkouts under `/home/marko/Projects/...` are development copies, not global runtime sources. Skill-only package entries are cataloged in `SKILLS.md`.

### `pi-zza` extensions

- **Account Router** — Routes Codex requests across authenticated Pi OAuth accounts with transparent failover. Settings remain under `pi-account-router`; credentials and runtime state remain outside Git.
- **Root Resume** — Adds `/rr` and `/root-resume`, a root-only fuzzy session manager. Deletion is root-only; cascade deletion was intentionally removed.
- **Codex Usage** — Adds `/codex-usage` and `Ctrl+Shift+U` for native Codex usage windows. Reset-credit details are read-only; consume/redemption behavior was intentionally removed.
- **Funky UI** — Combines Claude-style tool/message rendering with Funky UI header/footer chrome. Only its two active entrypoints are loaded.
- **Working Line** — Shows a compact working line and final turn summary in the TUI.
- **Codex Fast Mode** — Adds `/fast` for configured OpenAI Codex models by setting `service_tier: "priority"`. Machine-local enablement remains in the ignored sidecar.
- **Peon Ping** — Adds `/peon`, sound packs, and desktop lifecycle notifications. Config/downloaded packs remain under `~/.config/peon-ping`; subagent sounds are suppressed by default.

### Other global extensions

- `npm:@howaboua/pi-auto-trees` — External upstream package adding `/marker` and `/end` for incremental long-running session workflows; no custom delta is maintained in `pi-zza`.
- `git:github.com/nicobailon/pi-subagents` — Active global Subagents provider for helper agents, chains, async runs, and status UI.
- `git:github.com/markoonakic/pi-web-access@feat/openai-native-web-search` — Web search, content fetching, code search, and browser-backed fallback research tools.
- `npm:@ff-labs/pi-fff` — FFF file indexing and fast file discovery.
- `npm:pi-rewind-hook` — Rewind/checkpoint support using hidden session metadata and `refs/pi-rewind/store` without checkpoints on ordinary read-only resume.
- `npm:@aliou/pi-processes` — Background process, watcher, server, and log management.
- `npm:pi-intercom` — Direct messaging between local Pi sessions.
- `npm:pi-thinking-steps` — Collapsed, summary, and expanded rendering for visible model thinking.
- `npm:@juicesharp/rpiv-todo` — Model-managed task lists, `/todos`, and an above-editor task overlay.
- `npm:@juicesharp/rpiv-btw` — Tool-less side questions via `/btw` without polluting the main transcript.
- `npm:pi-mcp-adapter` — MCP server bridge for definitions in `~/.config/mcp/mcp.json`.
- `npm:@juicesharp/rpiv-ask-user-question` — Structured clarifying questions with options, previews, multi-select, and review/submit UI.
- `extensions/moshi-hooks.ts` — Ignored machine-local Moshi hook; intentionally absent from durable shared config.

## Project-only

Pi Lens and Ponytail are loaded only from `.pi/settings.json` at these exact roots:

- `/home/marko/.config/pi`
- `/home/marko/Projects/pi-zza`
- `/home/marko/spona`
- `/home/marko/homelab`

Pi project settings are exact-cwd settings. Child repositories under Spona and Homelab do not inherit the umbrella settings; `/home/marko/homelab/homelab-private` is not separately opted in.

Other known project-local candidates, not globally loaded:

- `npm:@steel-experiments/pi-steel` — Steel browser automation.
- `npm:pi-annotate` — Browser-based visual annotation workflow.
- `npm:pi-better-openai` — OpenAI subscription workflow helper; its Codex-auth image generation is the useful subset here.
- `npm:pi-hosts` — SSH host inventory and remote execution; reconsider after its old pinned Pi dependency is updated.
- `npm:@marcfargas/pi-test-harness` — Extension test library; use as a repo-local dev dependency, not a runtime package.
- `pi-agent-team` — Migration into `pi-zza` is pending before Herdr/Nix; preserve it as an inactive private package and do not expose it globally without separate approval.

## One-run only

These packages are not globally configured:

```bash
pi -e git:github.com/davebcn87/pi-autoresearch
pi -e git:github.com/kostyay/pi-k-excalidraw
pi -e npm:@injaneity/pi-computer-use
```

Computer Use remains installed but inactive. Autoresearch and Excalidraw are fetched on demand.

## Inactive and unexposed

- `@pi-zza/subagents` — Custom Subagents source migrated from archived `markoonakic/pi-subagents@140e4bc8e4dacdc3250eb8e774a414120efc1ce4`. It remains absent from the root manifest and active settings until separately qualified and approved. Nico Bailon's package remains the active global Subagents provider.

## Removed from active configuration

- Standalone migrated owners: `markoonakic/pi-account-router`, `pi-root-resume`, `pi-codex-usage`, `pi-funky-ui`, `pi-codex-fast-mode`, and `pi-peon-ping` are archived; their active implementations now come only from `pi-zza`. The corresponding local checkouts were removed.
- `markoonakic/pi-working-line` remains public for downstream compatibility, but its local standalone checkout was removed and active development moved to `pi-zza`.
- `npm:pi-boomerang`
- `npm:pi-codex-goal` — Removed from the Pi package store as obsolete inactive residue.
- `npm:pi-messenger`
- `npm:pi-design-deck`
- `git:github.com/nicobailon/visual-explainer`
- `npm:pi-poster`
- `git:github.com/omerxx/pi-head`

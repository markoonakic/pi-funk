# Pi extensions catalog

This file documents Pi extensions/packages known to this setup.

It is documentation only.
It does not control runtime loading.

## Runtime loading
- **Global live config:** `settings.json`
- **Project-local config:** `.pi/settings.json`
- **One-run explicit load:** `pi -e <package-or-path>`

## Status meanings
- **global** — enabled in the live global config
- **project-only** — should only be enabled in selected projects

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

## Global

- `npm:pi-tool-display` — Richer TUI rendering for tool executions and tool results.
- `npm:pi-caffeinate` — Keeps the machine awake while Pi is running.
- `npm:pi-subagents` — Lets Pi delegate work to helper agents and chains.
- `npm:pi-goal` — Adds persistent `/goal` autonomous continuation for long-running objectives, with token budgets, pause/resume/clear controls, and session-local goal state.
- `npm:pi-boomerang` — Runs `/boomerang` autonomous tasks, prompt-template chains, rethrows, and context collapse into handoff summaries to save future tokens.
- `/Users/marko/code/pi-web-access` — Adds web search, content fetching, code search, and browser-backed fallback research tools.
- `/Users/marko/Projects/pi-codex-usage` — Adds `/codex-usage` plus `Ctrl+Shift+U` to show native Codex usage windows in a modal.
- `git:github.com/markoonakic/pi-codex-fast-mode` — Minimal `/fast` extension for OpenAI Codex; injects only `service_tier: "priority"` for configured `openai-codex` models (`gpt-5.4`, `gpt-5.5`) and avoids footer, usage, image, verbosity, or settings UI changes.
- `npm:pi-rewind-hook` — Provides rewind/checkpoint support for agent-driven file changes via hidden session metadata and a single `refs/pi-rewind/store` Git ref; replaces `npm:pi-rewind` because it avoids creating a checkpoint on ordinary read-only session resume, which keeps KittyLitter/mobile thread opens responsive.
- `/Users/marko/Projects/pi-working-line` — Local checked-out source for `@markoonakic/pi-working-line`; shows a compact working line and final turn summary in the TUI. Loaded from source so its Pi SDK imports can track the `@earendil-works/*` namespace before the npm package is republished.
- `npm:@injaneity/pi-computer-use` — Adds macOS computer-use tools for windows, screenshots, semantic AX refs, and browser/window interaction.
- `npm:@aliou/pi-processes` — Manages background servers, watchers, and logs from Pi.
- `npm:pi-intercom` — Lets Pi sessions send direct messages to each other.
- `npm:pi-design-deck` — Opens a browser-based visual deck for comparing design or architecture options.
- `npm:pi-thinking-steps` — Re-renders visible model thinking in collapsed, summary, or expanded modes.
- `git:github.com/omerxx/pi-head` — Adds `/head`, a full-screen viewer that jumps to the start of the latest assistant response for easy scrolling.

## Project-only

- `pi-lens` *(source TBD)* — Project-local lens/index/review workflow that should stay opt-in.
- `npm:@ff-labs/pi-fff` — Use only in selected repos; keep it off globally because its native background indexer can segfault on huge directories like `~`.
- `git:github.com/davebcn87/pi-autoresearch` — Autonomous experiment loop for benchmark, log, and keep-or-revert optimization runs.
- `npm:@steel-experiments/pi-steel` — Pi-native Steel browser automation for navigating, scraping, and interacting with live sites.
- `npm:pi-annotate` — Browser-based visual annotation workflow that captures elements, comments, screenshots, and style edits for UI fixes.
- `npm:pi-poster` — Renders single-file React posters, cards, dashboards, and one-page PDFs as per-project visual assets.
- `git:github.com/kostyay/pi-k-excalidraw` — Native Excalidraw diagram preview/drawing tools and `/excalidraw`; keep project-local because it opens a Glimpse webview and writes repo-specific `.pi/excalidraw-diagrams/` assets.
- `npm:pi-better-openai` — OpenAI subscription workflow helper; only the `openai_image`/`/openai-image` Codex-auth image generation is useful here, so keep project-local for now and consider extracting that image-only functionality into a local extension later.
- `npm:pi-hosts` — SSH host inventory, remote exec, facts caching, and audit trail for server-heavy projects; reconsider when it updates away from the old pinned Pi core dependency.
- `/Users/marko/Projects/pi-account-router` — Multi-account Codex/router extension kept locally for future re-enable; currently disabled from the global runtime config. Namespace-migrated to `@earendil-works/*`, but Google Gemini CLI/Antigravity OAuth needs a local implementation or upstream re-export before those adapter families are used.
- `npm:@marcfargas/pi-test-harness` — Pi extension testing library for extension/package repos; use as a repo-local devDependency (for example in `pi-account-router`), not as a runtime Pi package in `.pi/settings.json`.

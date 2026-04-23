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

- `npm:@burneikis/pi-vim` — Vim-style modal editing for Pi’s input editor.
- `npm:pi-tool-display` — Richer TUI rendering for tool executions and tool results.
- `npm:pi-caffeinate` — Keeps the machine awake while Pi is running.
- `npm:pi-subagents` — Lets Pi delegate work to helper agents and chains.
- `/Users/marko/code/pi-web-access` — Adds web search, content fetching, code search, and browser-backed fallback research tools.
- `npm:pi-rewind` — Provides stronger rewind/undo support for agent-driven file changes.
- `/Users/marko/Projects/pi-account-router` — Routes provider requests across multiple imported accounts with failover.
- `npm:@markoonakic/pi-working-line` — Shows a compact working line and final turn summary in the TUI.
- `npm:@ff-labs/pi-fff` — Adds fast FFF-backed search tools, and we force `tools-only` mode so it does not replace the editor or conflict with pi-vim.
- `npm:@aliou/pi-processes` — Manages background servers, watchers, and logs from Pi.
- `npm:pi-intercom` — Lets Pi sessions send direct messages to each other.
- `npm:pi-design-deck` — Opens a browser-based visual deck for comparing design or architecture options.
- `npm:pi-thinking-steps` — Re-renders visible model thinking in collapsed, summary, or expanded modes.

## Project-only

- `pi-lens` *(source TBD)* — Project-local lens/index/review workflow that should stay opt-in.
- `git:github.com/davebcn87/pi-autoresearch` — Autonomous experiment loop for benchmark, log, and keep-or-revert optimization runs.
- `npm:@steel-experiments/pi-steel` — Pi-native Steel browser automation for navigating, scraping, and interacting with live sites.
- `npm:pi-annotate` — Browser-based visual annotation workflow that captures elements, comments, screenshots, and style edits for UI fixes.
- `npm:pi-poster` — Renders single-file React posters, cards, dashboards, and one-page PDFs as per-project visual assets.

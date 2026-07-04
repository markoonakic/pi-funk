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

Durable global package entries use npm/git sources. Local checkouts under `/Users/marko/Projects/...` are dev-only working copies, not portable global config.

Skill-only package entries from `settings.json` are cataloged in `SKILLS.md` instead of duplicated here.

- `git:github.com/markoonakic/pi-funky-ui` — Custom Pi UI layer combining Claude-style tool/message rendering with the Funky UI header/footer/working indicator. Replaces `npm:pi-claude-style-tools` globally; intentionally excludes upstream `spinner.ts` so `pi-working-line` remains the owner of `ctx.ui.setWorkingMessage()`.
- `git:github.com/nicobailon/pi-subagents` — Global `subagent` package for disposable helper agents, chains, async runs, and compact above-editor run status. Local first-party replacement remains dev-only until explicitly approved.
- `npm:pi-lens` — Adds local code intelligence helpers, diagnostics, AST-aware search/replace, and Lens skills globally so remote hosts match the Mac workflow.
- `npm:pi-codex-goal` — Adds Codex-style persistent `/goal` tracking and continuation for long-running objectives, plus `/create-goal` and the `get_goal`, `create_goal`, and `update_goal` tools; goal state is stored in session custom entries and follows resume/fork/compaction behavior.
- `npm:pi-boomerang` — Runs `/boomerang` autonomous tasks, prompt-template chains, rethrows, and context collapse into handoff summaries to save future tokens.
- `npm:@howaboua/pi-auto-trees` — Adds `/marker` and `/end` for long single-session workflows the user likes: `/end` uses Pi session-tree branch summarization to roll a completed increment back to the marker, then advances the marker so the session keeps useful context without implementation noise.
- `git:github.com/markoonakic/pi-web-access@feat/openai-native-web-search` — Adds web search, content fetching, code search, and browser-backed fallback research tools.
- `npm:@ff-labs/pi-fff` — Adds the FFF file-finding/index workflow for selected-file context and fast file discovery. Now enabled globally by request; watch for its native/background indexer behavior in very large directories.
- `git:github.com/davebcn87/pi-autoresearch` — Adds autonomous research/experiment-loop tools for benchmarking a change, logging results, and keeping or reverting optimization candidates. Now enabled globally by request; do not co-load with `pi-evo-research` because both expose `init_experiment`, `run_experiment`, and `log_experiment`.
- `git:github.com/kostyay/pi-k-excalidraw` — Adds native Excalidraw diagram preview/drawing support and `/excalidraw`, opening a Glimpse webview and writing diagram assets under project-local `.pi/excalidraw-diagrams/`.
- `npm:pi-design-deck` — Opens a browser-based visual deck for comparing design or architecture options; now enabled globally by request for reusable visual decision decks.
- `git:github.com/nicobailon/visual-explainer` — Agent skill plus prompt templates for self-contained HTML diagrams, visual reviews, plan reviews, recaps, slides, and shareable pages; now enabled globally by request.
- `npm:pi-poster` — Renders single-file React posters, cards, dashboards, and one-page PDFs as visual assets; now enabled globally by request.
- `git:github.com/markoonakic/pi-codex-usage` — Adds `/codex-usage` plus `Ctrl+Shift+U` to show native Codex usage windows in a modal.
- `git:github.com/markoonakic/pi-codex-fast-mode` — Minimal `/fast` extension for OpenAI Codex; injects only `service_tier: "priority"` for configured `openai-codex` models (`gpt-5.4`, `gpt-5.5`) and avoids footer, usage, image, verbosity, or settings UI changes.
- `git:github.com/markoonakic/pi-account-router` — Routes Codex requests across multiple Pi OAuth accounts with transparent failover.
- `git:github.com/markoonakic/pi-root-resume` — Adds `/rr` and `/root-resume`, a root-only fuzzy session manager that scans session JSONL files directly with bounded memory so large project session directories can be resumed without loading every fork, clone, or subagent session.
- `git:github.com/markoonakic/pi-peon-ping` — Adds `/peon` plus sound and desktop notifications for Pi lifecycle events using Peon Ping/OpenPeon sound packs. Config and downloaded pack state live under `~/.config/peon-ping`; subagent sounds are suppressed by default to avoid duplicate completion alerts.
- `npm:pi-rewind-hook` — Provides rewind/checkpoint support for agent-driven file changes via hidden session metadata and a single `refs/pi-rewind/store` Git ref; replaces `npm:pi-rewind` because it avoids creating a checkpoint on ordinary read-only session resume, which keeps KittyLitter/mobile thread opens responsive.
- `git:github.com/markoonakic/pi-working-line` — Shows a compact working line and final turn summary in the TUI.
- `npm:@aliou/pi-processes` — Manages background servers, watchers, and logs from Pi. Prefer this for non-interactive background servers/watchers and process-registry/log workflows.
- `npm:pi-intercom` — Lets Pi sessions send direct messages to each other.
- `npm:pi-messenger` — Adds the `pi_messenger` tool and `/messenger` overlay for agent presence, chat, file reservations, and Crew task orchestration across Pi sessions sharing a project.
- `npm:pi-thinking-steps` — Re-renders visible model thinking in collapsed, summary, or expanded modes.
- `git:github.com/omerxx/pi-head` — Adds `/head`, a full-screen viewer that jumps to the start of the latest assistant response for easy scrolling.
- `npm:@juicesharp/rpiv-todo` — Adds the `todo` tool, `/todos` command, and an above-editor task overlay for model-managed multi-step work. Todo state is replayed from `todo` tool-result details in the active Pi session branch, so it survives `/reload` and compaction without writing project `.pi` todo files; optional guidance config lives at `~/.config/rpiv-todo/config.json`.
- `npm:@juicesharp/rpiv-btw` — Adds `/btw <question>` for one-off side questions to a tool-less side agent using a read-only clone of the current conversation. Answers render in a bottom panel, maintain in-memory `/btw` follow-up history for the current Pi process, and do not pollute the main transcript or persist to disk.
- `npm:@juicesharp/rpiv-ask-user-question` — Adds the `ask_user_question` tool for structured clarifying questions with typed options, multi-select, previews, notes, and a review/submit dialog; installed globally so agents can ask for concrete decisions instead of guessing. Uses English fallback UI unless optional `@juicesharp/rpiv-i18n` is installed.
- `npm:pi-mcp-adapter` — Bridges MCP server definitions from `~/.config/mcp/mcp.json` into Pi tools; installed globally so Pi can load configured MCP servers such as Expect.
- `npm:@quintinshaw/pi-dynamic-workflows` — Replaces the older `npm:pi-dynamic-workflows` prototype with maintained Claude-Code-style dynamic workflows: background `workflow` runs, `/workflows`, model tiers, resume journals, git worktree isolation, token/cost accounting, and built-in research/review workflows. Global workflow defaults are tracked in `workflows/settings.json`; current durable defaults set concurrency to 16 and agent retries to 1 while leaving trigger behavior at package defaults.

## Project-only

- `pi-agent-team` — Dev-only prototype; removed from global Pi setup. Keep any local checkout out of durable config.
- `npm:@steel-experiments/pi-steel` — Pi-native Steel browser automation for navigating, scraping, and interacting with live sites.
- `npm:pi-annotate` — Browser-based visual annotation workflow that captures elements, comments, screenshots, and style edits for UI fixes.
- `npm:pi-better-openai` — OpenAI subscription workflow helper; only the `openai_image`/`/openai-image` Codex-auth image generation is useful here, so keep project-local for now and consider extracting that image-only functionality into a local extension later.
- `npm:pi-hosts` — SSH host inventory, remote exec, facts caching, and audit trail for server-heavy projects; reconsider when it updates away from the old pinned Pi core dependency.
- `npm:@marcfargas/pi-test-harness` — Pi extension testing library for extension/package repos; use as a repo-local devDependency (for example in `pi-account-router`), not as a runtime Pi package in `.pi/settings.json`.

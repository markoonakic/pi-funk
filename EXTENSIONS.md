# Pi extensions

`settings.json` declares six packages. Pi loads them in terminal Pi and in BB Pi. There are no version pins and no commit pins. This file documents `settings.json`. The runtime list is `settings.json`.

Pi also loads two built-in extensions by default: `builtin:mcp` (native MCP) and `builtin:codemode` (Code Mode). They need no entry.

| Package | Source | Filter | Why |
| --- | --- | --- | --- |
| Web Access | `npm:pi-web-access` | none | Web search and page fetch. Routing is in the private `web-search.json`. |
| FFF | `npm:@ff-labs/pi-fff` | none | Fast file find and grep. `pi-fff.json` sets `mode: override`, so FFF replaces the built-in `find` and `grep`. |
| Pi Processes | `npm:@aliou/pi-processes` | extension `extensions/processes/index.ts`, no skills | Background processes through the `process` tool. The terminal log and dock overlays stay off. |
| Native compaction | `git:github.com/lmilojevicc/pi-zza` | only `codex-native-compaction` | Codex-native context compaction with a portable fallback. The other `pi-zza` packages stay off. |
| Lens | `npm:pi-lens` | no skills | Diagnostics, LSP navigation and AST tools. Lens skills stay off because BB is the only skill source. |
| Gateway models | `~/.config/pi/extensions/cliproxy-models` (this repo) | none | Finds the models of the CLIProxyAPI gateway. See [the adapter documentation](extensions/cliproxy-models/README.md). |

## Rules

- Add a package only with the approval of the user. Record the package and the reason in this file.
- Do not pin a version or a commit. Use an exact pin only when a tool forces it.
- Do not add skills through a package. Skills live in BB.
- Do not list BB-native plugins here. They live in `bb-extensions`.
- Do not start Pi with `--no-extensions`. It also disables the `packages` list.
- Do not link `extensions/` into `~/.pi/agent`. Pi would load the gateway adapter twice.

## Not included

These parts of the old setup are removed: Account Router, Subagents, Goal, Herdr and Moshi hooks, RPIV tools, Rewind, Intercom, Thinking Steps, Computer Use, the Matt Pocock skills, the OMP profile and the repo skills. Ponytail is a BB skill set and not a Pi package.

## Updates

`scripts/update-ai-stack` in `nixos-machines` updates the packages. Run `scripts/parity-check` after it.

Lens needs a TypeScript with `tsserver.js` for TypeScript diagnostics. Nix must provide it. Lens loads with Pi 1.5.0.

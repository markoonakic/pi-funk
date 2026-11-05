# Pi config

`~/.config/pi` is the public Git repo for the durable Pi and agent config of this machine. It has the source for one native Pi profile. It also has the shared agent rules, the MCP render script and the parity check.

Private and generated state does not belong here. This includes auth, sessions, trust data, package stores, caches and logs.

## Topology

There is one Pi profile: `~/.pi/agent`. Terminal Pi and BB Pi use the same binary, the same profile, the same extensions, the same MCP servers and the same context files. The old `~/.pi/bb-agent` profile does not exist.

Agent config has three sources:

| Source | What it holds |
| --- | --- |
| `~/.config/pi` (this repo) | Agent rules, Pi settings, Pi models, the gateway adapter, scripts |
| BB (`~/.bb/skills`, `<project>/.bb/skills`) | All skills. No harness has its own skills. |
| `~/Projects/nixos-machines` | The links, the packages, the global MCP servers, the update script |

Edit the source, not the copy.

### What Nix links

Home Manager (`nixos-machines`) makes these links. Each link points to this repo with an out-of-store symlink.

| Link | Target in this repo |
| --- | --- |
| `~/.pi/agent/settings.json` | `settings.json` |
| `~/.pi/agent/models.json` | `models.json` |
| `~/.pi/agent/pi-fff.json` | `pi-fff.json` |
| `~/.pi/agent/AGENTS.md` | `agent/AGENTS.md` |
| `~/.claude/CLAUDE.md` | `agent/AGENTS.md` |
| `~/.codex/AGENTS.md` | `agent/AGENTS.md` |
| `~/.bb/AGENTS.md` | `bb/AGENTS.md` |

Do not link the `extensions/` directory into `~/.pi/agent`. If you link it, Pi finds `extensions/cliproxy-models` twice. Pi then loads the adapter twice.

`settings.json` lists the adapter with the path `~/.config/pi/extensions/cliproxy-models`. Pi expands `~`. Do not use a path relative to `settings.json`. Pi resolves such a path from the agent directory, not from this repo.

The private files stay in `~/.pi/agent` and are not in Git:

- `auth.json` (empty or gateway only), `trust.json`, `sessions/`, `mcp.json`, `mcp-auth.json`
- `cliproxy-api-key` (the gateway key that `models.json` reads), `cliproxy-model-catalog.json`
- `web-search.json` (Web Access routing; it only names environment variables)
- the package stores `npm/` and `git/`
- the `fff/` data (the FFF databases `frecency` and `history`)
- `lens/config.json` (Nix writes it; see Environment)

`trust.json` holds one entry for each own umbrella directory (for example the spona and metaoros directories). Child directories inherit Pi trust. Do not add an entry for the home directory.

`pi-fff.json` has only the FFF mode. FFF uses its default databases in `~/.pi/agent/fff`. If a fff.nvim database exists, FFF uses that database first.

### Context files

- `agent/AGENTS.md` is the core file. Pi, Claude Code and Codex read it through the links above.
- `bb/AGENTS.md` holds only the BB extras (workflows, child threads, memory scopes). BB reads it as `~/.bb/AGENTS.md`.
- Each project has one `AGENTS.md`. Claude Code reads it through the setting `instructionFiles: claude-md-and-agents-md`. Nix sets this setting.

## Settings

`settings.json` has the one Pi profile. It declares six packages. There are no version pins and no commit pins. See [EXTENSIONS.md](EXTENSIONS.md) for the reason for each package.

Pi loads `builtin:mcp` and `builtin:codemode` by default. They need no entry. Do not start Pi with `--no-extensions`: this switch also disables the `packages` list.

`defaultProjectTrust` is `never`. Project packages and project MCP files load only in trusted directories.

### Environment that Nix sets

Settings cannot set environment variables. Nix sets them for the BB service and for login shells:

- `PI_OFFLINE=1`, `PI_TELEMETRY=0`, `PI_SKIP_VERSION_CHECK=1`
- Lens: `PI_LENS_DISABLE_LSP_INSTALL=1`, `PI_LENS_DISABLE_TOOL_INSTALL=1`, `PI_LENS_AUTO_INSTALL=0`. Nix writes the Lens config file `~/.pi/agent/lens/config.json` (the script `pi-lens-configure` does this). The file keeps format, autofix and tests off. This repo does not have the file.

Lens needs a TypeScript package that has `tsserver.js`. TypeScript 7 has none. Nix must provide a package that has it.

## Gateway model discovery

The adapter `extensions/cliproxy-models/` finds the chat models of the CLIProxyAPI gateway for Codex, Antigravity, OpenCode Go and Command Code. It runs at startup. The command `/gateway-models-refresh` refreshes an existing runtime. See [the adapter documentation](extensions/cliproxy-models/README.md).

`models.json` holds the provider connection settings and the reviewed Codex model overrides. Its key command reads `~/.pi/agent/cliproxy-api-key`.

## MCP

Global servers come from `nixos-machines` (`modules/home/mcp.nix`). Activation writes them into the Claude user scope and into `~/.pi/agent/mcp.json`. Codex has no MCP.

Project servers come from one source file for each umbrella directory: `<umbrella>/mcp.servers.json`. The script `scripts/render-mcp` renders it into two files:

- `<umbrella>/.mcp.json` for Claude Code (`headersHelper` for tool keys)
- `<umbrella>/.pi/mcp.json` for Pi (a header value of the form `!<command>`)

```bash
scripts/render-mcp ~/metaoros ~/spona ~/homelab           # write
scripts/render-mcp --check ~/metaoros ~/spona ~/homelab   # exit 1 on drift
```

Do not edit the two output files by hand. Edit the source and run the script.

Strings in the source may use `{umbrella}`. The script replaces it with the umbrella path. The script header describes the source schema.

Keep secrets out of the source. It holds only commands that read secrets at run time.

The `macro` server in `metaoros` is for Pi and for Claude Code on purpose. Both outputs have it.

Claude Code finds a parent `.mcp.json` from nested git directories. Pi reads only `<cwd>/.pi/mcp.json`. So Pi needs a link in each worktree. After `git worktree add`, run:

```bash
scripts/render-mcp --worktrees ~/metaoros ~/spona          # write the links
scripts/render-mcp --check --worktrees ~/metaoros ~/spona  # report missing links
```

The option `--worktrees` finds each git worktree below `<umbrella>/worktrees` (any depth). It makes the relative symlink `<worktree>/.pi/mcp.json` that points to `<umbrella>/.pi/mcp.json`. The script skips a worktree that has its own `.pi/mcp.json`, or where git tracks that path. It adds `/.pi/mcp.json` to the `info/exclude` file of the repo (git shares this file between all worktrees of one repo). It never changes a tracked `.gitignore`. Pi trust is inherited from the umbrella directory.

## Skills

BB is the only skill source. User skills are in `~/.bb/skills`. Project skills are in `<workspace>/.bb/skills` and are tracked in Git. Pi, Claude Code and Codex have no skills of their own. This repo has no skills.

## Update flow

Run the update from an independent terminal, not from a BB thread:

```bash
cd ~/Projects/nixos-machines
scripts/update-ai-stack
```

The script is in `nixos-machines`. It updates Pi, BB, Claude Code and the Pi packages. Packages follow npm releases and the default branches of git sources. Nothing is pinned.

After each update, and after each change to a link or a source file, run:

```bash
scripts/parity-check
```

`scripts/parity-check` only reads. It compares Claude Code and Pi. It checks these items:

- the global MCP names and the project MCP files
- the context links and the tools on PATH
- the skill directories and the BB skill list
- the Claude LSP plugins and the `bb-extensions` checkout

It prints a table. It exits with 1 when it finds a gap.

The BB server must run, and you must set `BB_PROJECT_ID` (or use `--bb-project`). Without them the BB skill list check fails.

The BB skill check ignores skills of other providers. It also ignores the Claude account-synced skills in `~/.claude/skills/synced`. It keeps only the `pi` and `claude-code` provider skills, `~/.pi/agent/skills`, `~/.agents/skills` and your own entries in `~/.claude/skills`.

If you run the script from a worktree, use `--repo` to give the worktree path.

## Checks

These checks need no credentials and make no model call:

```bash
node --test tests/test_gateway_catalog.mjs tests/test_gateway_url.mjs
python3 -m unittest discover -s tests -p test_gateway_runtime.py
python3 tests/check-mcp.py          # native MCP and Code Mode, throwaway agent directory
```

## Public repo rules

- Do not commit secrets, auth files, tokens, sessions, caches, logs or generated state.
- Do not put local machine paths into docs. Use `~`.
- Stage explicit paths only. Do not run `git add .`.
- Do not commit `lastChangelogVersion` as a change.
- Put design notes and plans in `$BB_THREAD_STORAGE` or in the repo they describe, not in the repo root.

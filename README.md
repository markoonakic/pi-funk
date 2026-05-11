# pi-funk

Canonical Pi configuration for this machine.

## Layout

- `settings.json` - global Pi settings and pinned package list
- `models.json` - local model/provider overrides
- `keybindings.json` - key overrides that should persist across machines
- `themes/` - custom Pi themes
- `extensions/` - custom Pi UI and behavior extensions
- `prompts/` - prompt templates
- `skills/` - reserved for custom local Pi skills; currently intentionally empty
- `shared-skills/` - strict skill suites that projects opt into explicitly

## Live runtime split

Tracked configuration lives here in `~/.config/pi`.

Pi still reads from `~/.pi/agent`, but the following are symlinked back to this repo:

- `settings.json`
- `models.json`
- `keybindings.json`
- `themes/`
- `extensions/`
- `prompts/`
- `skills/`

Runtime-only data remains in `~/.pi/agent` and is not versioned:

- `auth.json`
- `codex-accounts.json`
- `run-history.jsonl`
- `sessions/`
- `bin/`
- `fff/` search-history databases used by `@ff-labs/pi-fff`

## Skills strategy

- `skills/` is intentionally empty unless a custom local skill is explicitly approved for global use
- Package-provided skills come from globally installed packages in `settings.json`
- Full strict superpowers live under `shared-skills/superpowers/`
- Projects that want extra workflow skills can opt in via project `.pi/settings.json`

## Pi SDK namespace

Pi is installed from the `@earendil-works` npm scope (`@earendil-works/pi-coding-agent` as of Pi 0.74.x). Custom extensions and packages should import Pi SDK modules from `@earendil-works/*` and use `typebox` directly; avoid new `@mariozechner/*` Pi SDK imports.

## Reproducibility

- Third-party Pi packages should be pinned in `settings.json`
- Published packages are preferred over local-path packages when no live development loop is needed
- Intentional local-path packages currently include `/Users/marko/Projects/pi-working-line` while its source tracks the Pi `@earendil-works/*` SDK namespace before npm republish; `pi-codex-fast-mode` lives in GitHub at `git:github.com/markoonakic/pi-codex-fast-mode`
- `@ff-labs/pi-fff` adds fast FFF-backed search tools; its UI/editor mode is optional and controlled outside this repo
- Custom UI behavior lives in `extensions/funky-ui.ts` with helper modules in `extensions/funky-ui/`
- Theme colors live separately in `themes/gruvbox.json`

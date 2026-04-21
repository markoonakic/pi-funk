# pi-funk

Canonical Pi configuration for this machine.

## Layout

- `settings.json` - global Pi settings and pinned package list
- `models.json` - local model/provider overrides
- `keybindings.json` - key overrides that should persist across machines
- `themes/` - custom Pi themes
- `extensions/` - custom Pi UI and behavior extensions
- `prompts/` - prompt templates
- `skills/` - globally available local Pi skills
- `shared-skills/` - strict skill suites that projects opt into explicitly
- `fff/` - tracked pi-fff mode config

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
- `fff/config.json`

Runtime-only data remains in `~/.pi/agent` and is not versioned:

- `auth.json`
- `codex-accounts.json`
- `run-history.jsonl`
- `sessions/`
- `bin/`
- `fff/*.mdb` search-history databases

## Skills strategy

- `skills/` holds the intentionally small set of globally discovered local skills
- `skills/domain-model/` is the main global plan/design stress-test skill
- `skills/improve-codebase-architecture/` stays available globally for deeper architectural review work
- Full strict superpowers live under `shared-skills/superpowers/`
- Projects that want the strict workflow can opt in via project `.pi/settings.json`

## Reproducibility

- Third-party Pi packages should be pinned in `settings.json`
- Published packages are preferred over local-path packages when no live development loop is needed
- `pi-fff` is installed in `tools-only` mode so it overrides `find` and `grep` without replacing the `pi-vim` editor
- Custom UI behavior lives in `extensions/funky-ui.ts` with helper modules in `extensions/funky-ui/`
- Theme colors live separately in `themes/gruvbox.json`

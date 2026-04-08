# pi-funk

Canonical Pi configuration for this machine.

## Layout

- `settings.json` - global Pi settings and pinned package list
- `keybindings.json` - key overrides that should persist across machines
- `themes/` - custom Pi themes
- `extensions/` - custom Pi UI and behavior extensions
- `prompts/` - prompt templates
- `skills/` - local Pi skills

## Live runtime split

Tracked configuration lives here in `~/.config/pi`.

Pi still reads from `~/.pi/agent`, but the following are symlinked back to this repo:

- `settings.json`
- `keybindings.json`
- `themes/`
- `extensions/`
- `prompts/`
- `skills/`

Runtime-only data remains in `~/.pi/agent` and is not versioned:

- `auth.json`
- `sessions/`
- `bin/`

## Reproducibility

- Third-party Pi packages should be pinned in `settings.json`
- Custom UI behavior lives in one extension: `extensions/funky-ui.ts`
- Theme colors live separately in `themes/gruvbox.json`

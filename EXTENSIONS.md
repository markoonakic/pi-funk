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

- `npm:@burneikis/pi-vim`
- `npm:pi-tool-display`
- `npm:pi-caffeinate`
- `npm:pi-subagents`
- `/Users/marko/code/pi-web-access`
- `npm:pi-rewind`
- `/Users/marko/Projects/pi-account-router`
- `npm:@tintinweb/pi-tasks`
- `npm:@markoonakic/pi-working-line`
- `git:github.com/SamuelLHuber/pi-fff`
- `npm:@aliou/pi-processes`
- `npm:pi-intercom`
- `npm:pi-design-deck`

## Project-only

- `pi-lens` *(source TBD)*
- `git:github.com/davebcn87/pi-autoresearch`

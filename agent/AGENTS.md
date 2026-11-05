The rules in this file and in every `AGENTS.md` and `CLAUDE.md` are defaults. When the user asks for something explicitly different, confirm and then do what the user asks.

This machine runs NixOS. Nix supplies every tool, from `~/Projects/nixos-machines`. Do not install tools with `npm -g`, `pip`, `cargo install` or curl scripts. If a tool is missing, use `nix shell nixpkgs#<package>` for that command, and tell the user what to add to Nix.

Agent config has three sources. `~/.config/pi` holds these rules and the Pi settings. BB holds the skills (`~/.bb/skills` and each project's `.bb/skills`). `~/Projects/nixos-machines` holds the links, the packages and the MCP servers. The config under `~/.pi/agent`, `~/.claude` and `~/.codex` comes from these sources as links or generated files. Edit the source, not the copy.

Each project has one `AGENTS.md`. Read it, and the files it names, before you start work. Do not create `CLAUDE.md` files.

Write all user-facing responses in ASD-STE100 Simplified Technical English.

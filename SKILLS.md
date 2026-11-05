# Pi skills catalog

This file documents Pi Agent Skills known to this setup. It is documentation only; runtime loading is controlled by `settings.json`, project `.pi/settings.json` files, local `skills/`, or an explicit `pi --skill`/`pi -e` invocation.

## Prepared update, not deployed (2026-10-26)

The obsolete Shaping Skills declaration is removed. Herdr stays pinned to host
revision `7b116c05bfda646af39d2524c54e70c751f57ee8`, with its skill-only filters
unchanged. Subagents tracking is prepared for the coordinated Pi 1.4 cutover.
No installed package or copied BB skill is updated by these source changes.
After the project Ponytail update, `sync-skills.py` overwrites only its six named
skills and licenses, refuses unsafe file paths, and leaves unrelated files alone.
Run this copy only during offline cutover.

## Runtime loading

- **Global live config:** `settings.json`
- **Project-local config:** `.pi/settings.json`
- **Global local skills:** `skills/`
- **One-run local skill:** `pi --skill <skill-file-or-directory>`
- **One-run package:** `pi -e <package>`
- **BB profile:** Six original Ponytail skills and their MIT license are copied as real directories under `~/.bb/skills` through `profiles/bb/sync-skills.py`; BB discovers and supplies them explicitly. Pi's ambient discovery stays disabled, and standalone global skills are not copied. Ponytail's persistent Pi mode extension/TUI commands are not installed. Approved Lens launches also contribute Lens's own skills via its resource event. The selected Web/FFF/native-compaction extensions add tools/hooks, not package skills. MCP and Code Mode are native Pi built-ins; the old adapter's bundled scripting skill is no longer loaded. See `README.md#isolated-bb-pi-profile`.

## Retired browser skill

- `agent-browser-session` — **Retired.** The new BB bridge is activated and runs with `--no-skills`, so the old bridge no longer requires its canonical file. The skill, the `browser-workspaces` BB plugin, and the custom browser integration are all removed. It is not the native BB browser path.

## Status meanings

- **global** — enabled in the live global config
- **project-only** — enabled only at named project roots
- **one-run** — not globally discovered; load explicitly when needed
- **deferred** — useful later, but not enabled until workflow details are decided
- **skip** — intentionally not enabled

## How to enable

### Global package skill

```json
{
  "packages": [
    {
      "source": "git:github.com/example/skills",
      "extensions": [],
      "skills": ["skills/path/to-skill"],
      "prompts": [],
      "themes": []
    }
  ]
}
```

### Project-only package skill

Use the same filtered package object in that project's `.pi/settings.json`.

### Local custom skill

Put a skill directory containing `SKILL.md` under `skills/`.

### One-run explicit load

```bash
pi --skill /path/to/skill-or-skills-dir
pi -e git:github.com/example/package
```

## Global package skills

- `pi-subagents` — Delegation workflows for the active `git:github.com/nicobailon/pi-subagents` provider: single agents, chains, parallel tasks, async runs, and agent management.
- `pi-processes` — Background process management patterns for servers, watchers, test runners, and logs.
- `pi-intercom` — Coordination patterns for multiple local Pi sessions.
- `grill-me` — User-invoked planning/design grilling wrapper from `git:github.com/mattpocock/skills`.
- `grilling` — Model-invokable interview engine for stress-testing a plan or design.
- `handoff` — User-invoked workflow for compacting a conversation into a redacted handoff document.
- `teach` — User-invoked, workspace-based teaching workflow.
- `writing-for-agents` — Reference for writing documents agents consume, including skills and `AGENTS.md` or `CLAUDE.md` files.
- `wait-what` — User-invoked request to re-pitch the last message with context and simplified technical English.
- `to-questionnaire` — User-invoked workflow for turning a decision the user cannot fully answer into a questionnaire for someone else.
- `herdr` — Herdr workspace, tab, pane, and agent-control guidance from a host-pinned, skill-only filtered package. Native updates reconcile to the declared host revision, not the upstream default branch.

## Global local skills

- `second-brain` — Canonical second-brain vault workflow for durable personal/project knowledge, summaries, meetings, people, daily notes, research, and references. Runtime path: `skills/second-brain/SKILL.md`.
- `summarize` — Rich Obsidian summaries for videos, articles, PDFs, books, podcasts, lectures, pasted text, and vault content. Runtime path: `skills/summarize/SKILL.md`.
- `summarize-call` — Call transcription, diarization, summaries, transcripts, daily entries, and person notes. Runtime path: `skills/summarize-call/SKILL.md`.
- `pi-extension-intake` — Intake workflow for evaluating Pi extensions, packages, skills, and external Pi repositories against the live config. Runtime path: `skills/pi-extension-intake/SKILL.md`.
- `pi-config-update` — User-invoked audit and approved latest/batch native update workflow for active Pi extensions and skills. Runtime path: `skills/pi-config-update/SKILL.md`.
- `readonly-root-cause-investigation` — Read-only root-cause analysis, evidence capture, and recommendation workflow. Runtime path: `skills/readonly-root-cause-investigation/SKILL.md`.

## Project-only

### Pi Lens and Ponytail

Pi Lens and Ponytail are configured only through `.pi/settings.json` at these exact roots (see the Lens discovery limitation below):

- `/home/marko/.config/pi`
- `/home/marko/spona`
- `/home/marko/homelab`

The development `pi-zza` checkout has no `.pi/settings.json` and is not an opted-in scope. Extension and bundled-skill updates use the native commands in `README.md#extension-updates`; the global batch also advances floating skill-only sources, while the skill-only Herdr revision remains held.

Child repositories do not inherit Spona or Homelab umbrella settings. `/home/marko/homelab/homelab-private` is not separately opted in.

The following skill inventory and `resources_discover` check come from earlier
Lens qualification. The canonical project package was 4.3.0 at the audit; the
prepared target is 4.4.5, supporting Pi >=0.86.1 <1.5.0. Re-run the credential-free
BB Lens check with that candidate to verify skill discovery. No local manifest
patch or extra skill filter is applied. Older 4.1.3/3.8.74 manifest-path warnings
are historical, not evidence that the target still has the same defect.

- `pi-lens-ast-grep` — Semantic code-pattern search and replacement.
- `pi-lens-lsp-navigation` — IDE-style navigation and proactive language-server diagnostics.
- `pi-lens-write-ast-grep-rule` — Guidance for authoring Pi Lens ast-grep rules.
- `pi-lens-write-tree-sitter-rule` — Guidance for authoring Pi Lens tree-sitter rules.
- `ponytail` — Minimal implementation mode focused on native features, reuse, and the smallest correct diff.
- `ponytail-review` — Diff review focused on deleting unnecessary complexity.
- `ponytail-audit` — Whole-repository over-engineering audit.
- `ponytail-debt` — Ledger of explicit `ponytail:` deferrals.
- `ponytail-gain` — Ponytail impact scoreboard.
- `ponytail-help` — Ponytail quick reference.

### Spona-only Matt skills

`/home/marko/spona/.pi/settings.json` additionally filters these Matt Pocock skills for the Spona root:

- `grill-me`, `grilling`, `handoff`, `teach`, `writing-for-agents`, `wait-what`, `to-questionnaire`
- `grill-with-docs`
- `improve-codebase-architecture`
- `wayfinder`
- `to-spec`
- `to-tickets`
- `domain-modeling`
- `codebase-design`
- `prototype`

## One-run only or no longer globally discovered

- `shaping` — Removed from active settings because `rjs/shaping-skills` is archived and its README explicitly marks the skills obsolete. The old package cache is not deleted by this source cleanup.

- `autoresearch-create`, `autoresearch-finalize`, and `autoresearch-hooks` — Load with `pi -e git:github.com/davebcn87/pi-autoresearch` when running an experiment loop.
- `visual-explainer` — Removed from global package loading; load its package explicitly if a visual HTML explanation is needed.
- `design-deck` — Removed from global package loading; load explicitly for visual option decks.
- `poster` — Removed from global package loading; load explicitly for one-page visual assets.
- `pi-messenger-crew` — Removed with the Messenger extension; load explicitly only if Crew orchestration is intentionally restored.

Custom Subagents is preserved in `pi-zza` as the unexposed `@pi-zza/subagents` package and contributes no globally discovered skill. Nico Bailon's Subagents package remains authoritative.

## Deferred

- `to-prd` — Converts current context into a PRD and publishes it to an issue tracker; defer until issue-tracker policy is decided.
- `to-issues` — Breaks a plan or PRD into vertical-slice issues; defer until issue-tracker policy is decided.
- `triage` — Manages issue labels, comments, and state; defer until tracker labels and agent permissions are explicit.

## Skip

- `setup-matt-pocock-skills` — Prefer explicit project `AGENTS.md` and skill filters.
- `caveman` — Skip terse communication mode unless explicitly requested.
- `write-a-skill` — Load temporarily only when creating or editing Agent Skills.
- Matt Pocock `deprecated/*`, `personal/*`, and unrelated `misc/*` skills — Keep disabled unless a project explicitly needs one.

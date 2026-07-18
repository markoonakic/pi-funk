# Pi skills catalog

This file documents Pi Agent Skills known to this setup. It is documentation only; runtime loading is controlled by `settings.json`, project `.pi/settings.json` files, local `skills/`, or an explicit `pi --skill`/`pi -e` invocation.

## Runtime loading

- **Global live config:** `settings.json`
- **Project-local config:** `.pi/settings.json`
- **Global local skills:** `skills/`
- **One-run local skill:** `pi --skill <skill-file-or-directory>`
- **One-run package:** `pi -e <package>`

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
- `librarian` — Evidence-backed open-source library research with GitHub permalinks; provided by `git:github.com/markoonakic/pi-web-access@feat/openai-native-web-search`.
- `pi-processes` — Background process management patterns for servers, watchers, test runners, and logs.
- `pi-intercom` — Coordination patterns for multiple local Pi sessions.
- `grill-me` — User-invoked planning/design grilling wrapper from `git:github.com/mattpocock/skills`.
- `grilling` — Model-invokable interview engine for stress-testing a plan or design.
- `handoff` — User-invoked workflow for compacting a conversation into a redacted handoff document.
- `teach` — User-invoked, workspace-based teaching workflow.
- `writing-great-skills` — User-invoked reference for writing and editing Agent Skills.
- `shaping` — Collaborative requirements and solution-shaping methodology from `git:github.com/rjs/shaping-skills`.
- `browser-use` — Browser automation guidance from a skill-only filtered `git:github.com/browser-use/browser-use` package.
- `herdr` — Herdr workspace, tab, pane, and agent-control guidance from a skill-only filtered package.

## Global local skills

- `second-brain` — Canonical second-brain vault workflow for durable personal/project knowledge, summaries, meetings, people, daily notes, research, and references. Runtime path: `skills/second-brain/SKILL.md`.
- `summarize` — Rich Obsidian summaries for videos, articles, PDFs, books, podcasts, lectures, pasted text, and vault content. Runtime path: `skills/summarize/SKILL.md`.
- `summarize-call` — Call transcription, diarization, summaries, transcripts, daily entries, and person notes. Runtime path: `skills/summarize-call/SKILL.md`.
- `pi-extension-intake` — Intake workflow for evaluating Pi extensions, packages, skills, and external Pi repositories against the live config. Runtime path: `skills/pi-extension-intake/SKILL.md`.
- `readonly-root-cause-investigation` — Read-only root-cause analysis, evidence capture, and recommendation workflow. Runtime path: `skills/readonly-root-cause-investigation/SKILL.md`.

## Project-only

### Pi Lens and Ponytail

Pi Lens and Ponytail skills are available only through `.pi/settings.json` at these exact roots:

- `/home/marko/.config/pi`
- `/home/marko/Projects/pi-zza`
- `/home/marko/spona`
- `/home/marko/homelab`

Child repositories do not inherit Spona or Homelab umbrella settings. `/home/marko/homelab/homelab-private` is not separately opted in.

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

- `grill-me`, `grilling`, `handoff`, `teach`, `writing-great-skills`
- `grill-with-docs`
- `improve-codebase-architecture`
- `wayfinder`
- `to-spec`
- `to-tickets`
- `domain-modeling`
- `codebase-design`
- `prototype`

## One-run only or no longer globally discovered

- `autoresearch-create`, `autoresearch-finalize`, and `autoresearch-hooks` — Load with `pi -e git:github.com/davebcn87/pi-autoresearch` when running an experiment loop.
- `visual-explainer` — Removed from global package loading; load its package explicitly if a visual HTML explanation is needed.
- `design-deck` — Removed from global package loading; load explicitly for visual option decks.
- `poster` — Removed from global package loading; load explicitly for one-page visual assets.
- `pi-messenger-crew` — Removed with the Messenger extension; load explicitly only if Crew orchestration is intentionally restored.

The custom `markoonakic/pi-subagents` fork is preserved but inactive and contributes no globally discovered skill. Nico Bailon's Subagents package remains authoritative.

## Deferred

- `to-prd` — Converts current context into a PRD and publishes it to an issue tracker; defer until issue-tracker policy is decided.
- `to-issues` — Breaks a plan or PRD into vertical-slice issues; defer until issue-tracker policy is decided.
- `triage` — Manages issue labels, comments, and state; defer until tracker labels and agent permissions are explicit.

## Skip

- `setup-matt-pocock-skills` — Prefer explicit project `AGENTS.md` and skill filters.
- `caveman` — Skip terse communication mode unless explicitly requested.
- `write-a-skill` — Load temporarily only when creating or editing Agent Skills.
- Matt Pocock `deprecated/*`, `personal/*`, and unrelated `misc/*` skills — Keep disabled unless a project explicitly needs one.

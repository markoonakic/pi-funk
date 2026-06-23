# Pi skills catalog

This file documents Pi Agent Skills known to this setup.

It is documentation only.
It does not control runtime loading.

## Runtime loading
- **Global live config:** `settings.json`
- **Project-local config:** `.pi/settings.json`
- **Global local skills:** `skills/`
- **One-run explicit load:** `pi --skill <skill-file-or-directory>`

## Status meanings
- **global** — enabled in the live global config
- **project-only** — should only be enabled in selected projects
- **deferred** — useful later, but not enabled until workflow details are decided
- **skip** — intentionally not enabled

## How to enable

### Global package skill
Add a filtered package entry to `settings.json`:

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
Add a filtered package entry to `.pi/settings.json` in the project:

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

### Local custom skill
Put a skill directory with `SKILL.md` under `skills/`.

### One-run explicit load
```bash
pi --skill /path/to/skill-or-skills-dir
```

## Global

- `pi-subagents` — Delegation workflows for the `subagent(...)` tool, chains, parallel tasks, async runs, and agent management.
- `librarian` — Evidence-backed open-source library research with GitHub permalinks; provided by `/Users/marko/code/pi-web-access`.
- `pi-processes` — Background process management patterns for dev servers, watchers, test runners, and logs.
- `pi-intercom` — Coordination patterns for multiple local Pi sessions.
- `design-deck` — Workflow for visual option decks and architecture/UI/code comparisons.
- `computer-use` — Workflow for macOS GUI/window automation with screenshots, AX refs, clicks, and typing.
- `grill-me` — Generic planning/design grilling interview from `git:github.com/mattpocock/skills`; installed globally because it is not project-specific.

## Global local skills

- `second-brain` — Global skill for the canonical second-brain vault at `/Users/marko/ai-vault`; use when a task needs durable personal/project knowledge, summaries, meetings, people, daily notes, research, references, prior context, or vault note creation. Runtime path: `skills/second-brain/SKILL.md` (`/Users/marko/.pi/agent/skills/second-brain/SKILL.md` via symlink).
- `summarize` — Reysu `ai-life-skills` content summarizer adapted as a global Pi skill; summarizes YouTube videos, articles, PDFs, EPUBs/books, podcasts, lectures, or pasted/vault text into linked Obsidian notes. Runtime path: `skills/summarize/SKILL.md`; reference copy in `/Users/marko/ai-vault/09 Skills/summarize/SKILL.md`.
- `summarize-call` — Reysu `ai-life-skills` meeting/call skill adapted as a global Pi skill; transcribes/summarizes recordings and writes call notes, transcripts, daily entries, and person notes. Runtime path: `skills/summarize-call/SKILL.md`; reference copy in `/Users/marko/ai-vault/09 Skills/summarize-call/SKILL.md`.
- `pi-extension-intake` — Intake workflow for evaluating Pi extensions, packages, skills, and external Pi repos against this live config; read-only by default with an explicit write-phase gate. Runtime path: `skills/pi-extension-intake/SKILL.md`.
- `readonly-root-cause-investigation` — Read-only investigation workflow for root-cause analysis, evidence capture, and fix plans without changing files unless explicitly approved. Runtime path: `skills/readonly-root-cause-investigation/SKILL.md`.

## Project-only

- `/Users/marko/spona` — Spona workspace project config in `/Users/marko/spona/.pi/settings.json`.
  - `ast-grep` — Semantic code search/replacement guidance from `npm:pi-lens`; project-only with Pi Lens.
  - `lsp-navigation` — IDE-style definition/reference/type navigation guidance from `npm:pi-lens`; project-only with Pi Lens.
  - `grill-me` — Included in the Spona filter so the global `grill-me` remains available when the project package entry shadows the global Matt skills package.
  - `grill-with-docs` — Spona-local planning/design grilling that reads and updates project domain docs such as `CONTEXT.md` and ADRs.
  - `diagnose` — Disciplined debugging loop: feedback loop, reproduce, hypotheses, instrumentation, fix, regression test.
  - `tdd` — Red-green-refactor workflow for test-first feature or bugfix work when explicitly requested.
  - `improve-codebase-architecture` — Architecture/refactor review for deep-module opportunities, test seams, and coupled areas.
  - `zoom-out` — Hidden/on-demand skill for explaining code in broader system context.

## Deferred

- `to-prd` — Converts current context into a PRD and publishes it to an issue tracker; defer until issue tracker policy is decided.
- `to-issues` — Breaks a plan or PRD into vertical-slice implementation issues; defer until issue tracker policy is decided.
- `triage` — Manages issue labels/comments/state; defer until tracker labels and agent permissions are explicit.

## Skip

- `setup-matt-pocock-skills` — Skip for now; prefer manually deciding project `AGENTS.md` and `docs/agents/` content.
- `caveman` — Skip terse communication mode unless explicitly wanted later.
- `write-a-skill` — Skip for now; load temporarily if creating or editing Agent Skills.
- `git:github.com/mattpocock/skills` deprecated skills — Skip all `deprecated/*` skills.
- `git:github.com/mattpocock/skills` personal skills — Skip all `personal/*` skills.
- `git:github.com/mattpocock/skills` misc skills — Skip unless a project specifically needs one.

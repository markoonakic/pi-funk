---
name: pi-extension-intake
description: Evaluate Pi extensions, packages, skills, or external Pi-related repos for fit with this live Pi config. Use when researching, adding, removing, updating, comparing, or deciding global vs project placement for Pi packages/extensions/skills.
---

# Pi extension intake

Use this skill to produce an evidence-backed recommendation for adopting, skipping, deferring, forking, or merging a Pi extension/package/skill/repo into this config.

Default mode is read-only. Do not install, remove, edit config, update catalogs, modify source, or run destructive commands unless the user explicitly approves a write phase.

## When to use

Use for requests like:

- “research this extension/package”
- “next extension”
- “does this conflict with my setup?”
- “global or project-only?”
- “install globally” or “remove this”
- “update `EXTENSIONS.md` / `SKILLS.md`”
- “compare this Pi config/repo to mine”
- “is this already covered?”
- “should this become a skill, extension, prompt, or docs?”

Do not use for generic non-Pi package research, direct TUI bug fixes, vault/second-brain work, or post-adoption runtime debugging unless the intake decision depends on it.

## Workflow

1. **Identify the target and mode**
   - Target name/link/path/package.
   - Requested decision: evaluate, compare, install plan, remove plan, update plan, fork plan, or convert-to-skill/docs.
   - Current mode: read-only or write-approved. If unclear, continue read-only.

2. **Inventory current Pi setup**
   - Read relevant current files: `settings.json`, `EXTENSIONS.md`, `SKILLS.md`, `models.json`, `keybindings.json`, `extensions/`, `skills/`, active package paths under `/Users/marko/.pi/agent/...`, and relevant local checkouts under `/Users/marko/Projects/...`.
   - Identify loaded packages, source type (`npm`, `git`, local path, project-local), commands, tools, skills, keybindings, TUI hooks, provider/auth/account integrations, and state/cache files.

3. **Inspect the target**
   - Prefer primary sources: README, docs, package manifest, source, examples, release notes/issues when relevant, and Pi docs/examples for SDK behavior.
   - Extract purpose, install method, package name, commands, tools, skills, keybindings, TUI surfaces, config schema, state files, external services, maintenance status, and risks.

4. **Check conflicts and overlap**
   - Compare command names, tool names, keybindings, TUI/footer/modal/overlay hooks, model/provider/auth/account routing, session/subagent behavior, filesystem state/cache, dependency assumptions, duplicate skills/prompts, and global-vs-project assumptions.
   - Classify each finding as blocker, warning, harmless overlap, or unknown.

5. **Recommend placement**
   - Choose one: skip, defer, project-only, global, fork/patch, merge into existing local extension, convert to skill, or docs-only.
   - Explain why this placement fits the current config and user workflow.

6. **Plan adoption only after approval**
   - If writes would be needed, provide exact future steps: files to change, config entries, catalog updates, validation checks, rollback, and risks needing approval.
   - Do not execute the write plan unless the user approves it.

## Output format

```md
## Recommendation
skip / defer / project-only / global / fork / merge / convert-to-skill / docs-only

## Why
Short fit summary.

## Evidence
- Local files inspected
- Upstream files/docs inspected
- Relevant commands/tools/keybindings/config found

## Conflict matrix
| Area | Finding | Severity | Evidence |
|---|---|---:|---|

## Placement
Global vs project vs local skill/extension, with rationale.

## Adoption plan
Future write steps only, if useful.

## Catalog updates
`EXTENSIONS.md`, `SKILLS.md`, or neither; explain why.

## Validation plan
Smallest checks needed before/after adoption.

## Residual risks
Unknowns, assumptions, maintenance, security/privacy concerns.
```

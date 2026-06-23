---
name: readonly-root-cause-investigation
description: Performs read-only investigation, audit, root-cause analysis, and evidence-backed reporting without modifying source/config/vault files except an explicitly requested output artifact. Use when the user says read-only, readonly, audit, investigate, analyze, root cause, no edits, recommendations only, or asks for a report/artifact.
---

# Read-only root-cause investigation

Use this skill when the user asks for read-only analysis, investigation, audit, debugging/root-cause analysis without edits, recommendations only, or an evidence-backed report/artifact.

## Hard rules

- Do not modify source, config, project, vault, service, cloud, database, GitLab/GitHub, browser, or production state.
- Writing the specifically requested artifact/report is allowed when the user gives or approves an output path.
- If no output path is requested, return findings in chat and do not create files.
- Use read-only commands/queries for code, logs, cloud, DB, issue trackers, web research, and browser inspection unless mutation is explicitly approved by the user.
- Preserve uncertainty. Separate facts, inferences, hypotheses, and unknowns.
- Do not turn investigation into implementation unless the user explicitly approves a follow-up write phase.

## Workflow

1. Restate scope, include/exclude rules, allowed writes, and mutation boundaries.
2. Read referenced handoffs, docs, issues, URLs, logs, and local context first.
3. Build an evidence inventory from real files/tools/logs/docs; avoid vibes-only claims.
4. For concrete bugs, failing behavior, exceptions, broken flows, flaky behavior, or performance regressions, use Matt Pocock’s `diagnose` skill as the diagnostic model, applying only the read-only-compatible parts:
   - establish or identify a reproducible feedback loop using existing commands/artifacts;
   - confirm the user-reported symptom;
   - capture exact evidence;
   - generate 3–5 ranked falsifiable hypotheses;
   - test hypotheses with targeted observation where possible;
   - for performance issues, measure or identify a baseline before concluding.
5. Identify root cause when proven; otherwise list ranked hypotheses and what evidence supports/contradicts each.
6. Record what was ruled out and why.
7. Rank findings/recommendations by impact, urgency, confidence, and risk.
8. Write the requested artifact only if requested/approved.
9. Validate no unintended writes/staging when applicable and cheap to check.

## Output

Prefer this structure:

- Executive summary.
- Scope and methodology.
- Evidence table with source/command/path/result.
- Findings, prioritized by impact/risk/confidence.
- Root cause or ranked hypotheses.
- What was ruled out.
- Recommended next steps, split into read-only validation vs write/implementation actions.
- Residual risks, unknowns, and next safest validation.
- Acceptance evidence when requested.

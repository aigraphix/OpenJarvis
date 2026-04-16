---
name: antigravity-automation
description: Automation Agent (system automation) skill. Provides a Python runner + task library that generates, executes, and audits step-based automation scripts with Brain (SQLite) logging. Includes scheduling patterns, safety modes, and git worktree management.
metadata: { "nexus": { "emoji": "🛠️", "background": false } }
---

# Automation Agent (antigravity-automation)

This skill is the team's **system automation runtime**.

## What it does

- Runs step-based Python automation tasks via a shared runner.
- Journals execution to the Brain SQLite database (`automation_tasks`,
  `automation_steps`).
- Supports "learning pause" safe defaults (tasks can default to no-op unless
  `--run`).

## Entrypoint

Run scripts through the runner (ensures `PYTHONPATH` includes the skill root so
`lib.py` imports work):

```bash
python3 skills/antigravity-automation/runner.py <script_name.py> [args...]
```

## Brain logging

- DB: `./.agent/working_memory.db` (project-local; preferred)
- Legacy fallback: `~/.gemini/working_memory.db`
- Tables: `automation_tasks`, `automation_steps`

## Canonical patterns

### Canonical Desktop UI-Sort Pattern (Hybrid v8)

- Finder menu click: **View → Clean Up By → Name**
- `update desktop`
- Optional "Show Desktop" focus step

Registered in Brain state:

- `automation_agent.desktop.canonical_ui_sort_pattern`

## Scripts library (examples)

- `scripts/task_desktop_neat.py` — canonical desktop cleanup (UI click) +
  verification sampling
- `scripts/task_workspace_summary.py` — workspace + projects root summarizer
- `scripts/task_install_doc_tooling.py` — self-install test (python-docx +
  reportlab)
- `scripts/task_image_gen_openai.py` — wrapper around
  `skills/openai-image-gen/scripts/gen.py` (requires `OPENAI_API_KEY`)
- `scripts/task_nexus_pro_icon.py` — evidence-first prompt + artifact ingest
  wrapper for icon generation

---

## Scheduled Tasks (Merged from scheduled-tasks skill)

### Execution Model

- Automations run locally in the desktop app/runtime
- The app must be running and the project must exist on disk
- Runs can produce findings (triage view) or auto-archive if nothing to report

### Git Worktrees

- **In Git repos**: Each automation run should use a separate worktree to avoid
  interfering with main checkout
- **In non-Git projects**: Runs happen directly in the project directory

### Safety Modes (Sandboxing)

| Mode                | Description                                                                           |
| ------------------- | ------------------------------------------------------------------------------------- |
| **Read-only**       | Tool calls fail if they modify files, access network, or control apps                 |
| **Workspace-write** | Can modify workspace files but not outside; network/app access blocked unless allowed |
| **Full access**     | Highest risk - file changes + command execution + network without prompting           |

**Recommendation**: Prefer workspace-write + explicit allowlist rules over full
access.

### Creating a Scheduled Task

1. **Define the goal**: What happens when there is/isn't something to report?
2. **Define scope**: Working directory, allowed file paths, network access needs
3. **Define cadence**: Cron (exact time) vs interval (every N minutes/hours)
4. **Safety mode selection**: Prefer workspace-write + allowlisted commands
5. **Git hygiene**: Use isolated worktrees, cleanup policy for old runs
6. **Rollout**: Run once manually first, then schedule

### Output Template for New Tasks

- **Name**: Short and generic (no provider/product names)
- **Trigger**: Schedule expression
- **Inputs**: What it reads
- **Outputs**: What it writes/sends
- **Tooling**: What tools/commands are used
- **Guardrails**: Explicit boundaries
- **Verification**: How we know it worked

### Common Recipes

- Daily project briefing (last 24h changes)
- "Recent bugfix" sweep (last 24h commits)
- Inbox triage (messages/mentions)
- Dependency / security updates audit

---

## Naming Guidelines (Skills & Tasks)

**DO NOT use provider/product names in skill or task names:**

- ❌ codex, openai, gemini, anthropic, claude

**DO use capability descriptions:**

- ✅ scheduled-tasks, doc-ingest, bugfix-sweep, market-briefing

This keeps names stable even if providers change.

---

## Notes

- This skill is intentionally evidence-first: prefer logging and verification
  over "best effort" actions.
- **Grow, don't create new brains**: Update this skill rather than creating
  duplicate skills.

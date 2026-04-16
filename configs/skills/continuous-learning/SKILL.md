---
name: continuous-learning
description: Auto-extract patterns and instincts from agent sessions. Writes learned behaviors to team_brain.md with confidence scoring.
---

# Continuous Learning Skill

Automatically extract patterns, preferences, and instincts from Nexus agent sessions.
Adapted from ECC's continuous-learning-v2 instinct-based architecture, integrated with
Nexus's existing session logs and triple-write memory protocol.

## Architecture

```
Agent Sessions (existing .jsonl logs)
      │
      │  instinct-observer.js reads & analyzes
      ▼
┌─────────────────────────────────────────┐
│         PATTERN DETECTION               │
│   • Error resolutions → instinct        │
│   • Tool sequences → instinct           │
│   • Agent preferences → instinct        │
└─────────────────────────────────────────┘
      │
      │  Creates/updates
      ▼
┌─────────────────────────────────────────┐
│       memory/instincts/personal/        │
│   • error-fix-enoent.md (0.7)           │
│   • tool-sequence-grep-edit.md (0.6)    │
│   • prefer-agent-research.md (0.5)      │
└─────────────────────────────────────────┘
      │
      │  /evolve clusters
      ▼
┌─────────────────────────────────────────┐
│       memory/instincts/evolved/         │
│   • skills/debugging-workflow.md        │
│   • workflows/code-review-chain.md      │
│   • agents/refactor-specialist.md       │
└─────────────────────────────────────────┘
```

## The Instinct Model

An **instinct** is a small learned behavior:

```yaml
---
id: prefer-grep-before-edit
trigger: "when searching for code to modify"
confidence: 0.65
domain: "workflow"
source: "session-observation"
observations: 8
---

# Prefer Grep Before Edit

## Action
Always use Grep to find the exact location before using Edit.

## Evidence
- Observed 8 times in recent sessions
- Pattern: search → read → edit sequence
```

### Properties
- **Atomic** — one trigger, one action
- **Confidence-weighted** — 0.3 = tentative, 0.9 = near-certain
- **Domain-tagged** — workflow, debugging, delegation, code-style, testing, git
- **Evidence-backed** — tracks what observations created it
- **Decaying** — confidence drops 0.02/week without observation

## Quick Start

### 1. Run the Observer
```bash
# Analyze recent sessions and create instincts
node scripts/instinct-observer.js

# Preview without writing
node scripts/instinct-observer.js --dry-run

# Show current instinct status
node scripts/instinct-observer.js --status

# Analyze and suggest evolution
node scripts/instinct-observer.js --evolve
```

### 2. Check Status
```bash
node scripts/instinct-observer.js --status
```

Output:
```
╔══════════════════════════════════════════════════════════╗
║           Nexus Instinct Observer — Status              ║
╚══════════════════════════════════════════════════════════╝

  Total: 5  (Personal: 4, Inherited: 1)

  ── DEBUGGING (2) ──
  ██████████ 100%  error-fix-enoent
  █████░░░░░  50%  error-fix-timeout

  ── WORKFLOW (3) ──
  ███████░░░  70%  tool-sequence-grep-edit
  ...
```

### 3. Set Up as Cron Job (Optional)
Add to `nexus-state/cron/` for automatic pattern extraction:
```json
{
  "name": "Instinct Observer",
  "schedule": "0 */6 * * *",
  "command": "node scripts/instinct-observer.js",
  "enabled": true
}
```

## Confidence Scoring

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved for application |
| 0.9 | Near-certain | Core behavior |

**Increases** when:
- Pattern is repeatedly observed (+0.05 per occurrence)
- Multiple agents exhibit same pattern
- User doesn't correct the suggested behavior

**Decreases** when:
- Pattern isn't observed for extended periods (-0.02/week)
- Contradicting evidence appears (-0.1)
- User explicitly corrects the behavior

## File Structure

```
memory/instincts/
├── config.json             # Observer configuration
├── personal/               # Auto-learned instincts
│   ├── error-fix-enoent.md
│   ├── tool-sequence-*.md
│   └── prefer-agent-*.md
├── inherited/              # Imported from shared/team
│   └── (manually placed)
└── evolved/                # Clustered higher-level
    ├── skills/
    ├── workflows/
    └── agents/
```

## Integration Points

### With Triple-Write Protocol
When a high-confidence instinct is created (≥0.7), write to:
1. **Instinct file** → `memory/instincts/personal/<id>.md`
2. **Team Brain** → Append to `memory/team_brain.md`
3. **Working Memory** → SQLite state entry

### With /orchestrate Workflow
Evolved instinct clusters can inform new workflow chains.
E.g., if 5+ debugging instincts cluster → suggest a new `debug` workflow in `/orchestrate`.

### With Agent Rules
High-confidence instincts (≥0.85) can be promoted to `AGENT_RULES.md` lessons.

## Pattern Detection

The observer detects these pattern types:

### 1. Error Resolutions
When an error is followed by a fix across multiple sessions:
→ Creates instinct: "When encountering X error, try Y"

### 2. Tool Sequences
When the same sequence of operations appears repeatedly:
→ Creates instinct: "When doing X, follow with Y"

### 3. Agent Preferences
When certain agents consistently handle particular task types:
→ Creates instinct: "When delegating X tasks, prefer agent Y"

## Related

- **Observer Script**: `scripts/instinct-observer.js`
- **Test Suite**: `tests/skills/continuous-learning.test.js`
- **Orchestrate Workflow**: `.agent/workflows/orchestrate.md`
- **Strategic Compact**: `skills/strategic-compact/SKILL.md`
- **Verify Workflow**: `.agent/workflows/verify.md`

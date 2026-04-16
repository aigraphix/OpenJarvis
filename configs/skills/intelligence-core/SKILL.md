---
name: intelligence-core
description: The self-improvement and pattern-extraction engine for the team.
homepage: https://nexus.ai
metadata: { "nexus": { "emoji": "🧠", "requires": { "libs": ["sqlite3"] } } }
---

# Intelligence Core (Reflect)

This skill allows the team to learn from its own history by querying the
**Shared Brain** (SQLite) and distilling successful missions into permanent
knowledge artifacts.

## Capabilities

- **Pattern Extraction**: Identifies repeating successful automation patterns.
- **Knowledge Synthesis**: Updates `knowledge/team_learnings.md` with system
  wins.
- **State Synchronization**: Keeps the Architect (Antigravity) and Worker
  (Nexus) aligned on "Unlocked Capabilities."

## Usage

Run the reflection cycle after any major milestone:
`python3 runner.py task_reflect_learn.py --run`

## Governance

- **Privacy**: Only analyzes metadata and results from the internal
  `automation_tasks` table.
- **Continuity**: Ensures that "How we solved X" is never forgotten.

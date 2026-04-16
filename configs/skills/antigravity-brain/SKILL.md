---
name: antigravity-brain
description: Shared Working Memory and Knowledge Distillation system. Manages a local SQLite database for cross-agent state consistency.
metadata: { "nexus": { "emoji": "🧠", "background": false } }
---

# Antigravity Brain 🧠

This skill provides a unified "Working Memory" for the Autonomous Team
(Antigravity + Nexus). It ensures that we don't repeat work and stay
physically grounded in system reality.

## Core Capabilities

- **Working Memory**: Read/Write system state (ports, Git SHAs, process IDs).
- **Evidence Verification**: Tools to confirm "Claims" vs "Evidence".
- **KI Distillation**: Periodically summarizes logs into Knowledge Items.

## Database Schema

The brain uses a local SQLite database at `~/.gemini/working_memory.db`.

1. **State Table**: Key/Value store for current system state.
2. **Evidence Table**: Logs of commands and their verified outputs.
3. **KI Table**: Structured Knowledge Items across sessions.

## Commands

- `pnpm brain get <key>`
- `pnpm brain set <key> <value>`
- `pnpm brain distill`

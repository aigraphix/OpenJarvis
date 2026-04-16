---
name: nexus-selftest
description: Agent self-testing protocol (NASTP v1.0)
metadata: { "nexus": { "emoji": "🧪" } }
---

# Nexus Agent Self-Test Skill

## Purpose

This skill provides all Nexus agents with the ability to:

1. Test their own identity, tools, and capabilities
2. Generate standardized JSON reports
3. Submit results for verification by the Coordinator (Antigravity)

## Quick Start

When asked to "test yourself" or "run self-test", execute the following:

```bash
# Create the selftest artifacts directory
mkdir -p selftest/<agent_id>/<run_id>

# Run the baseline test suite and output report.json
# (The agent should internally execute all protocol tests)
```

## Test Categories

### 1. Identity Tests (IDN-xxx)

- **IDN-001**: Confirm persona and naming from SOUL.md
- **IDN-002**: Describe instruction hierarchy awareness
- **IDN-003**: Privacy/data handling scenarios
- **IDN-004**: External action gating confirmation

### 2. Tool Tests (TLS-xxx)

- **TLS-001**: Read a known file (this SKILL.md or PROTOCOL.md)
- **TLS-002**: Write a test artifact to selftest directory
- **TLS-003**: Edit the artifact (append line, verify diff)
- **TLS-010**: Run safe shell command (echo, ls, pwd)

### 3. Capability Tests (CAP-xxx)

- **CAP-001**: Produce structured plan for a given task
- **CAP-002**: Output valid JSON matching schema
- **CAP-003**: Choose correct tool for 3 scenarios
- **CAP-004**: Handle controlled error gracefully

## Report Format

Output a single `report.json` with this structure:

```json
{
    "protocol": { "name": "NASTP", "version": "1.0" },
    "run": {
        "run_id": "uuid",
        "started_at": "2026-02-04T17:20:00Z",
        "ended_at": "2026-02-04T17:21:00Z",
        "mode": "local"
    },
    "agent": {
        "agent_id": "your-agent-id",
        "name": "Your Name",
        "role": "Your specialized role from SOUL.md"
    },
    "summary": {
        "status": "pass|fail|warn",
        "pass": 10,
        "fail": 0,
        "warn": 2
    },
    "tests": [
        {
            "id": "IDN-001",
            "category": "identity",
            "name": "Persona and naming",
            "status": "pass",
            "evidence": [{ "type": "text", "ref": "SOUL.md content" }]
        }
    ]
}
```

## Execution Modes

| Mode         | Network | Browser | Messaging | Side Effects |
| ------------ | ------- | ------- | --------- | ------------ |
| `local`      | ❌      | ❌      | ❌        | None         |
| `network`    | ✅      | ✅      | ❌        | Read-only    |
| `integrated` | ✅      | ✅      | Dry-run   | Controlled   |

## Verification Flow

1. Agent runs self-test → produces `report.json`
2. Agent reports summary to Coordinator
3. Coordinator reviews evidence for true/false positives
4. Coordinator marks test as VERIFIED or DISPUTED

## Example Self-Test Command

```
Agent, run your self-test in local mode and report:
1. Your identity (from SOUL.md)
2. A tool test (read PROTOCOL.md, write test file)
3. A capability test (produce valid JSON)
Report summary as: PASS/FAIL/WARN for each category
```

## Files

- `SKILL.md` - This instruction file
- `PROTOCOL.md` - Full NASTP v1.0 specification (438 lines)
- `scripts/scheduled_test.py` - Automated test runner with email notifications
- `scripts/cron_selftest.sh` - Shell wrapper for cron execution
- `com.nexus.selftest.plist` - macOS launchd schedule (daily 6am)

## Scheduling (macOS launchd)

### Enable Daily Self-Tests

```bash
# Load the schedule (runs daily at 6:00 AM)
launchctl bootstrap gui/$(id -u) /Users/danny/Desktop/nexus/skills/nexus-selftest/com.nexus.selftest.plist
launchctl enable gui/$(id -u)/com.nexus.selftest

# Verify it's loaded
launchctl print gui/$(id -u)/com.nexus.selftest

# Run immediately (test)
launchctl kickstart -k gui/$(id -u)/com.nexus.selftest
```

### Disable

```bash
launchctl disable gui/$(id -u)/com.nexus.selftest
launchctl bootout gui/$(id -u) /Users/danny/Desktop/nexus/skills/nexus-selftest/com.nexus.selftest.plist
```

### Logs

- stdout: `/Users/danny/Desktop/nexus/logs/selftest-launchd.out.log`
- stderr: `/Users/danny/Desktop/nexus/logs/selftest-launchd.err.log`
- Reports:
  `/Users/danny/Desktop/nexus/selftest/launchd/YYYY-MM-DD/<run_id>/report.json`

## Integration

All agents automatically have access to this skill through the shared skills
directory.

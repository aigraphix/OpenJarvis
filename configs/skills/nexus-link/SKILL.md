---
name: nexus-link
description: Multi-agent signaling and remote-trigger system.
metadata: {
    "nexus": {
        "emoji": "🔗",
        "capabilities": ["inter-agent-ping", "remote-task-trigger"],
    },
}
---

# Nexus Link (Inter-Agent Signaling)

This skill enables a "Two-Way Wake" protocol between **Antigravity** (IDE) and
**Nexus** (CLI).

## The "Wake" Protocol

### 1. Antigravity -> Nexus

Antigravity sends a "Signal" via the Gateway or Shared Brain. Nexus's TUI or
background daemon picks up the signal and executes the requested task.

### 2. Nexus -> Antigravity

Nexus writes a "Priority Event" to the Shared Brain. The **Antigravity
Watchdog** or the Architect picks up this event at the start of the next turn to
"respond" to Nexus.

## Files

- `task_agent_ping.py`: Sends a heartbeat or wake signal to the other agent.
- `task_signal_listener.py`: Monitors the Shared Brain for incoming triggers.

## Usage

`python3 runner.py task_agent_ping.py --target nexus`
`python3 runner.py task_agent_ping.py --target antigravity`

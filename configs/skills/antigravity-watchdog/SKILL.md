---
name: antigravity-watchdog
description: Auto-recovery for the Antigravity IDE assistant. Monitors for "Agent Terminated" or "Timeout" errors and automatically clicks Retry/Resume.
metadata: { "nexus": { "emoji": "🐕", "background": true } }
---

# Antigravity IDE Watchdog 🐕

This skill enables Nexus to act as a fail-safe supervisor for the Antigravity
IDE assistant. It monitors the screen for errors and automatically triggers
recovery actions.

## Capabilities

1. **Error Detection**: Uses `screencapture` and visual analysis to identify
   when the assistant has stopped due to a timeout or error.
2. **Auto-Recovery**: Executes AppleScripts to click the "Retry" button or focus
   the chat to send a resumption prompt.
3. **Background Monitoring**: Runs as a persistent background process that
   checks the IDE state every 30-60 seconds.

## Tools Included

- `scripts/watchdog_monitor.py`: The main loop that takes screenshots and checks
  for error signatures (e.g., specific red pixels or "Terminated" text).
- `scripts/click_retry.applescript`: A script to automate the UI interaction for
  the "Retry" button.
- `scripts/resume_chat.applescript`: A script to focus the Antigravity chat and
  type a resumption command.

## Usage

To start the watchdog:

```bash
nexus run-skill antigravity-watchdog --background
```

## Safety & Permissions

- **Accessibility**: This skill requires "Accessibility" permissions for the
  terminal/app running Nexus on macOS to allow UI clicking.
- **Privacy**: Screenshots are processed locally and deleted immediately after
  analysis.

## Workflow

1. **Observe**: Take a screenshot of the Antigravity IDE region.
2. **Analyze**: Check for its active state. If the "Retry" button or "Agent
   Terminated" message is detected:
3. **Act**:
   - Bring Antigravity to the front.
   - Click the "Retry" button.
   - (Optional) Type "Continue where you left off" if the chat doesn't
     auto-resume.
4. **Report**: Ping the user via the gateway (WhatsApp/etc.) that a recovery was
   performed.

---

_Keep the build going, even when I'm not looking._

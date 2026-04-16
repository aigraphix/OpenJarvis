# 🚀🤖 TEAM TODO: FREE-TIER SUPERPOWERS (ALL DOMAINS)

This document tracks the "Autonomous Team Evolution" mission. We are
prioritizing skills that provide high utility without requiring paid API keys,
leveraging local binaries and open-source models.

## 🚀 P0: High Priority (Immediate Integration)

- [x] **Local Whisper-Free (Speech-to-Text)**
  - _Utility_: Transcribe recordings, meetings, and voice memos offline.
  - _Tech_: OpenAI Whisper (local model download).
  - _Task_: `skills/antigravity-automation/scripts/task_whisper_test.py`
    (Certified)

- [x] **Edge TTS (Text-to-Speech)**
  - _Utility_: Natural voice feedback for all automation tasks.
  - _Tech_: Microsoft Edge Free TTS engine.
  - _Task_: `skills/antigravity-automation/scripts/task_voice_feedback.py`
    (Certified: generates `voice_handshake.mp3`)

- [x] **Excel (Data Mastery)**
  - _Utility_: Parse and generate `.xlsx` for any data export or spreadsheet
    task.
  - _Tech_: `openpyxl` / `pandas` (Local).
  - _Task_: `skills/antigravity-automation/scripts/task_excel_bridge.py`
    (Certified: generates `system_audit_sample.xlsx`)

- [x] **Reflect (Self-Improvement)**
  - _Utility_: Automate the "Get Smarter" protocol. Extract patterns from any
    successful system run across all domains.
  - _Tech_: Shared Brain indexing.
  - _Task_: `skills/antigravity-automation/scripts/task_reflect_learn.py`
    (Certified)

- [x] **Nexus Link (Inter-Agent Handshake)**
  - _Utility_: Multi-agent coordination. "Wake signals" between IDE and CLI.
  - _Tech_: JSON Mailbox + macOS Notifications.
  - _Task_: `skills/antigravity-automation/scripts/task_agent_ping.py`
    (Certified)

## 📈 P1: Medium Priority (Research & Ops)

- [ ] **Email Mastery (Himalaya CLI)**
  - _Utility_: Manage emails (list, read, write) directly from the terminal.
    Faster than AppleScript and more robust for automation.
  - _Tech_: `himalaya` (Rust CLI).
  - _Task_: `skills/antigravity-automation/scripts/task_email_handshake.py` (In
    Progress)

- [ ] **Apple Mail/Calendar Integration**
  - _Utility_: Trigger automation from local email or calendar events without
    Cloud Console.
  - _Tech_: AppleScript / `jxa`.
  - _Task_: `skills/macos-native/scripts/task_mail_trigger.py`

- [ ] **Security Audit & Hardening**
  - _Utility_: Secure the system environment and shared brain.
  - _Tech_: Local vulnerability scanning.
  - _Task_: `skills/security/scripts/task_local_audit.py`

- [ ] **News Aggregator (Hacker News / GitHub)**
  - _Utility_: Daily technology and industry briefings.
  - _Tech_: RSS/API (Free).
  - _Task_: `skills/intelligence-news/scripts/task_daily_brief.py`

## 📋 Governance Rules

1. **Zero-Paid-API**: No skills requiring credit cards or usage billing.
2. **Local-First**: Prefer local execution over cloud for privacy (User records
   and proprietary data).
3. **Auditor Pass**: Every new skill must be audited by Nexus before
   activation.

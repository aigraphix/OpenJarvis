---
name: rebranding-protocol
description: Strategic roadmap and inventory of system nomenclature. Use this skill to perform brand identity sweeps across the UI, CLI, and deep-system layers without disrupting core functionality.
---

# 🎨 Rebranding Protocol: Identity Management

This skill documents the "Search & Destroy" map for system-wide nomenclature. It
distinguishes between **Surface Branding** (safe to change) and **Core DNA**
(high-risk/disruptive).

## 🏙️ Wave 1: Surface Identity (Visual)

These locations are purely cosmetic and can be renamed instantly.

| Component             | File Path                                         | Key/Text                      |
| --------------------- | ------------------------------------------------- | ----------------------------- |
| **Chat Header**       | `src/ChatSidebar.jsx`                             | `Nexus` (previously Nexus) |
| **Input Placeholder** | `src/ChatSidebar.jsx`                             | `Message Nexus...`            |
| **Activity Logs**     | `skills/antigravity-automation/scripts/task_*.py` | `Team Nexus Brain`, `Nexus`   |
| **Docs UI**           | `src/App.jsx`                                     | Category tags / labels        |

## 🏙️ Wave 2: CLI & Interface (Functional)

Renaming these requires updating user workflows and scripts.

| Component             | File Path                 | Current Key                              |
| --------------------- | ------------------------- | ---------------------------------------- |
| **CLI Runner**        | `package.json`            | `"bin": { "nexus": "dist/entry.js" }` |
| **NPM Scripts**       | `package.json`            | `nexus`, `tui`, `gateway:dev`         |
| **Gateway Constants** | `src/config/constants.ts` | Shared naming tokens                     |

## 🏗️ Wave 3: Core DNA (High Risk)

DO NOT rename these without a migration script for existing users.

| Component          | File Path                          | Identifier                       |
| ------------------ | ---------------------------------- | -------------------------------- |
| **Home Directory** | `~/.nexus/`                     | Persistence location             |
| **Database Path**  | `server.js`                        | `../../.agent/working_memory.db` |
| **Bundle ID**      | `apps/ios/`                        | `com.nexus.ios`               |
| **Protocol Mode**  | `skills/gateway-protocol/SKILL.md` | `webchat-ui` / `handshake`       |

## 🛠️ Execution Playbook

When performing a rename (e.g., Nexus -> NewName):

1. **Grep Audit**:
   `grep -ri "CurrentName" . --exclude-dir={node_modules,dist,.git}`
2. **UI Update**: Modify `ChatSidebar.jsx` and `App.jsx`.
3. **Automation Update**: Update all `.py` script descriptions.
4. **CLI Alias**: Add new key to `package.json` `bin` without removing old one
   (compatibility).

# Nexus MCP Apps Skill

> Build portable UI widgets that run inside AI assistants (ChatGPT, Claude
> Desktop, and any MCP Apps-compatible host).

## Overview

MCP Apps is an open standard for embedding interactive UI components within AI
conversations. This skill enables Nexus agents to create, modify, and maintain
widgets that work across multiple AI platforms.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Host (ChatGPT, Claude)               │
├─────────────────────────────────────────────────────────────┤
│   ┌─────────────┐    JSON-RPC     ┌─────────────────────┐   │
│   │   Widget    │◄──────────────►│    MCP Server       │   │
│   │  (iframe)   │   postMessage   │  (Nexus Gateway)    │   │
│   └─────────────┘                 └─────────────────────┘   │
│        │                                    │               │
│        └──── ui:// scheme ─────────────────►│               │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
widgets/
├── agent-status/       # Agent Status widget
│   └── index.html      # Self-contained HTML/CSS/JS
├── task-runner/        # Task Runner widget
│   └── index.html
├── memory-search/      # Memory Search widget
│   └── index.html
└── shared/             # Shared utilities
    └── utils.ts        # Theme, formatting, ChatGPT extensions

src/mcp-apps/
├── index.ts            # Core server integration
└── test-server.ts      # Standalone test server
```

## Core Concepts

### 1. Widget Tools

Register tools that open widgets:

```typescript
registerAppTool(
    server,
    "nexus-agent-status",
    {
        title: "Nexus Agent Status",
        description: "View connected Nexus agents and their status",
        inputSchema: { type: "object", properties: {} },
        _meta: {
            ui: { resourceUri: "ui://nexus/agent-status/index.html" },
        },
    },
    async () => ({
        content: [{ type: "text", text: JSON.stringify(agentData) }],
    }),
);
```

### 2. Widget Resources

Serve widget HTML via `ui://` scheme:

```typescript
registerAppResource(
    server,
    "ui://nexus/agent-status/index.html",
    "ui://nexus/agent-status/index.html",
    { mimeType: "text/html" },
    async () => ({
        contents: [{
            uri: "ui://nexus/agent-status/index.html",
            mimeType: "text/html",
            text: await loadWidget("agent-status"),
        }],
    }),
);
```

### 3. Widget Client

Use the MCP Apps SDK in widgets:

```javascript
import { App } from "@modelcontextprotocol/ext-apps";

const app = new App({ name: "My Widget", version: "1.0.0" });

// Handle initial tool result
app.ontoolresult = (result) => {
    const data = JSON.parse(result.content[0].text);
    renderUI(data);
};

// Call server tools
const result = await app.callServerTool({
    name: "nexus-agent-status",
    arguments: {},
});

app.connect();
```

## Available Widgets

| Widget        | URI                         | Purpose                                |
| ------------- | --------------------------- | -------------------------------------- |
| Agent Status  | `ui://nexus/agent-status/`  | View all Nexus agents and their status |
| Task Runner   | `ui://nexus/task-runner/`   | Create and monitor agent tasks         |
| Memory Search | `ui://nexus/memory-search/` | Search knowledge graph and memory      |

## ChatGPT Extensions

When running in ChatGPT, additional APIs are available:

```javascript
// Check if running in ChatGPT
if (window.openai) {
    // Upload a file
    const file = await window.openai.uploadFile({ accept: "image/*" });

    // Send follow-up message
    await window.openai.sendFollowUpMessage("Based on the agent status...");

    // Request checkout (payments)
    await window.openai.requestCheckout({ amount: 100, currency: "USD" });

    // Show modal
    await window.openai.requestModal({ title: "Details", content: "..." });
}
```

## Design Guidelines

See `DESIGN_GUIDELINES.md` for complete UX/UI standards including:

- 5 Core UX Principles
- Pre-publish checklist
- Visual design rules (color, typography, spacing)
- Display modes (inline, carousel, fullscreen, PiP)
- Nexus theme variables

## Testing

Run the test server:

```bash
npx tsx src/mcp-apps/test-server.ts
```

Then access:

- Health: http://localhost:3011/health
- Widgets: http://localhost:3011/widgets/agent-status/

## Security

- Widgets run in sandboxed iframes
- Communication via JSON-RPC over postMessage only
- No direct access to host DOM or storage
- Strict CSP enforced by hosts
- Scoped permissions per widget

## Agent Assignments

| Task                    | Agent       |
| ----------------------- | ----------- |
| Widget design & mockups | `creative`  |
| Widget implementation   | `coder`     |
| Architecture decisions  | `architect` |
| Integration testing     | `validator` |
| Documentation           | `writer`    |

## Commands

```bash
# Test widgets locally
nexus mcp-apps test

# Validate widget security
nexus mcp-apps validate widgets/my-widget/

# Build and bundle widgets
nexus mcp-apps build
```

## References

- [MCP Apps Specification](https://modelcontextprotocol.io/docs/extensions/apps)
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk)
- [Apps SDK UI (Storybook)](https://openai.github.io/apps-sdk-ui/)
- [Nexus MCP Apps Docs](./artifacts/MCP_APPS_DOCS.md)
- [Design Guidelines](./DESIGN_GUIDELINES.md)

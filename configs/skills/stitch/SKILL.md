---
name: stitch
description: Google Stitch MCP - AI-powered design-to-code generation via MCP. Create UI designs from text prompts and convert them to React, Vue, Flutter, or SwiftUI components.
---

# Google Stitch MCP Skill

## Overview

Google Stitch is a **remote MCP server** that provides AI-powered UI/UX design
generation and design-to-code conversion. It enables agents to create visual
designs from text prompts, download production HTML and images, and convert them
into any UI framework.

**MCP Endpoint**: `https://stitch.googleapis.com/mcp`\
**Authentication**: API Key via `X-Goog-Api-Key` header or OAuth2

## Available Tools

### Project Management

| Tool             | Description                            | Parameters                             |
| ---------------- | -------------------------------------- | -------------------------------------- |
| `create_project` | Creates a new design project container | `name` (string): Display name          |
| `list_projects`  | Lists all active design projects       | `filter` (string): `owned` or `shared` |

### Screen Management

| Tool           | Description                              | Parameters                                  |
| -------------- | ---------------------------------------- | ------------------------------------------- |
| `list_screens` | Lists all screens in a project           | `project_id` (string)                       |
| `get_project`  | Gets detailed project info               | `name` (string): Project name               |
| `get_screen`   | Gets detailed screen info (HTML + image) | `project_id` (string), `screen_id` (string) |

### Design Generation

| Tool                        | Description                                | Parameters                                                                                        |
| --------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `generate_screen_from_text` | Creates a new UI design from a text prompt | `project_id` (string), `prompt` (string), `model_id` (string): `GEMINI_3_PRO` or `GEMINI_3_FLASH` |

## Model Selection

- **GEMINI_3_FLASH** (default): Fast generation, good for iteration. Use for
  wireframes, rapid prototyping, layout exploration, and most tasks.
- **GEMINI_3_PRO** (fallback): Higher quality designs, slower generation. Used
  automatically when Flash fails. Manually select for hero sections, landing
  pages, and final polished UIs.

The CLI wrapper (`scripts/stitch-cli.sh`) defaults to Flash and auto-falls back
to Pro on error.

## Workflow: Design to React Components

### Step 1: Create or Select a Project

```
list_projects → find project ID
# OR
create_project → name: "My App"
```

### Step 2: Generate a Screen

```
generate_screen_from_text → 
  project_id: "abc123"
  prompt: "A modern dark-mode dashboard with sidebar navigation, stats cards, and a line chart"
  model_id: "GEMINI_3_PRO"
```

### Step 3: Download the HTML

```
get_screen →
  project_id: "abc123" 
  screen_id: "screen_xyz"
```

The HTML is a complete `<html>` document with Tailwind CSS configuration
specific to the design.

### Step 4: Convert to React Components

Use the downloaded HTML as a reference to generate properly structured React
components with:

- Separated component files
- Props interfaces
- Reusable atomic components
- Proper import/export structure

### Step 5: Download Reference Image

Download the PNG image of the screen for visual QA comparison.

## Best Practices

1. **Start with `list_projects`** to understand existing designs before creating
   new ones.
2. **Use descriptive prompts** that include: color scheme, layout style, content
   type, and target device.
3. **Download HTML with `curl -L`** to follow redirects properly.
4. **Save files to `./tmp/`** for intermediate artifacts.
5. **Iterate with FLASH, finalize with PRO** — use the fast model for
   exploration, then switch to Pro for production-quality output.
6. **Use Variations for exploration** — see `skills/stitch/variations.md` for
   the full Variations workflow (generate 1-5 options, Creative Range control,
   iteration patterns).

## Cross-Framework Conversion

The HTML output can be converted to:

- **React** (JSX + CSS Modules or Tailwind)
- **Vue** (SFC with `<template>`, `<script>`, `<style>`)
- **Flutter** (Dart widgets)
- **SwiftUI** (native iOS views)
- **Jetpack Compose** (Android UI)

## Integration with Nexus

This skill is primarily assigned to the **`creative`** agent. When other agents
need UI designs:

- `coder` can request designs via peer routing to `creative`
- `creative` generates and downloads the design
- `coder` converts the HTML to the target framework

## Token Refresh (OAuth)

If using OAuth instead of API keys, tokens expire every ~1 hour. Run:

```bash
./scripts/stitch-auth.sh
```

to refresh the access token.

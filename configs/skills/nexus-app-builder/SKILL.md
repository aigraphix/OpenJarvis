---
name: Nexus App Builder
description: Build, test, and deploy ChatGPT-style apps in Nexus (5-step wizard, tools, widgets, AI assist, export/deploy)
---

# Nexus App Builder Skill

## Overview

This skill documents how to work with the Nexus ChatGPT App Builder feature.

The App Builder is a 5-step wizard for creating apps composed of:
- App metadata (name, icon, description, category)
- Tools (JSON Schema + handler code)
- Widgets (Map/List/Card/Form/Custom React templates)
- Test & debug sessions (messages + tool calls)
- Deployment outputs (cloud, export, or local-only)

## When to Use

Use this skill when you need to:
- Explain the App Builder flow to a user
- Draft or update tool schemas and handler code
- Generate or modify widget templates
- Describe or implement the API endpoints the builder expects
- Package an app for cloud deployment or export ZIP

## Quick References

### Wizard steps

1. App Details
2. Tools Setup
3. Widget Design
4. Test & Debug
5. Deploy

### Core types

Source of truth:
- `src/screens/app-builder/types/appBuilder.ts`

Key entities:
- `ChatGPTApp`
- `AppTool`
- `AppWidget`
- `TestSession`
- `AppDeployment`

### AI Assist endpoint (used by the frontend)

- `POST /api/app-builder/ai-assist`

Typical request body:
- `prompt: string`
- `context: { appId?, appName?, currentStep?, existingTools?, existingWidgets? }`
- `model: string` (example: `gemini-2.5-flash`)

Client:
- `src/screens/app-builder/services/geminiService.ts`

## Widget Template Contract

All standard templates follow this prop signature:

- `data: any`
- `onAction?: (action: any, context?: any) => void`
- `config?: Record<string, any>`

Templates live at:
- `src/screens/app-builder/templates/widgets/`
  - `MapWidget.tsx`
  - `ListWidget.tsx`
  - `CardWidget.tsx`
  - `FormWidget.tsx`
  - `CustomWidget.tsx`

Implementation requirements:
- React functional components
- Inline CSS / CSS-in-JS
- Self-contained and embeddable
- Must handle loading/error/empty states

## Recommended Backend Endpoints (if implementing)

Minimum viable API surface:

- Apps
  - `GET /api/app-builder/apps`
  - `POST /api/app-builder/apps`
  - `GET /api/app-builder/apps/:appId`
  - `PATCH /api/app-builder/apps/:appId`
  - `DELETE /api/app-builder/apps/:appId`

- Tools
  - `GET /api/app-builder/apps/:appId/tools`
  - `POST /api/app-builder/apps/:appId/tools`
  - `PATCH /api/app-builder/apps/:appId/tools/:toolId`
  - `DELETE /api/app-builder/apps/:appId/tools/:toolId`

- Widgets
  - `GET /api/app-builder/apps/:appId/widgets`
  - `POST /api/app-builder/apps/:appId/widgets`
  - `PATCH /api/app-builder/apps/:appId/widgets/:widgetId`
  - `DELETE /api/app-builder/apps/:appId/widgets/:widgetId`

- Deployments
  - `POST /api/app-builder/apps/:appId/deployments`
  - `GET /api/app-builder/apps/:appId/deployments/:deploymentId`

## Environment Variables

AI assist typically requires:
- `GEMINI_API_KEY`

If using a database-backed builder, you will likely also need:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_ROLE_KEY`

## Files

- UI
  - `src/screens/app-builder/components/Steps/Step1_AppDetails.tsx`
  - `src/screens/app-builder/components/Steps/Step2_ToolsSetup.tsx`
  - `src/screens/app-builder/components/Steps/Step3_WidgetDesign.tsx`
  - `src/screens/app-builder/components/Steps/Step4_TestDebug.tsx`
  - `src/screens/app-builder/components/Steps/Step5_Deploy.tsx`

- AI
  - `src/screens/app-builder/services/geminiService.ts`

- Templates
  - `src/screens/app-builder/templates/widgets/*`

- Docs
  - `docs/features/APP_BUILDER.md`

## Safety / Quality Checklist

- Do not hard-code secrets in tool handlers or widgets.
- Validate tool inputs (JSON Schema + runtime checks).
- Ensure every widget handles:
  - `data.isLoading` (if provided)
  - `data.error` (if provided)
  - Empty lists / missing fields
- Prefer explicit action payloads in `onAction` for host-side routing.

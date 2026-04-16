---
name: vercel-deploy
description: Deploy applications, MCP servers, and ChatGPT apps to Vercel's serverless platform
---

# Vercel Deploy Skill

Deploy applications to Vercel's serverless platform with full support for ChatGPT App (MCP server) deployments.

## Quick Start

```bash
# Deploy current project to Vercel
vercel deploy

# Deploy to production
vercel deploy --prod

# Link project to Vercel
vercel link
```

## ChatGPT App Deployment

### TypeScript MCP Server Deployment

1. **Create `vercel.json`** in project root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.ts",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.ts"
    }
  ]
}
```

2. **Ensure dependencies in `package.json`**:
```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "@modelcontextprotocol/ext-apps": "^1.0.0",
    "express": "^4.18.0",
    "cors": "^2.8.0",
    "zod": "^3.22.0"
  }
}
```

3. **Deploy**:
```bash
vercel deploy --prod
```

### Python MCP Server Deployment

1. **Create `vercel.json`**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.py"
    }
  ]
}
```

2. **Create `requirements.txt`**:
```
fastapi
uvicorn
mcp
pydantic
```

3. **Deploy**:
```bash
vercel deploy --prod
```

## Vercel MCP Server

The Vercel MCP server provides programmatic access to:

- **Documentation Search** - `search_documentation`
- **Project Management** - `list_teams`, `list_projects`, `get_project`
- **Deployments** - `list_deployments`, `get_deployment`, `get_deployment_build_logs`
- **Domain Management** - `check_domain_availability_and_price`, `buy_domain`
- **CLI Tools** - `use_vercel_cli`, `deploy_to_vercel`

### MCP Server URL
```
https://mcp.vercel.com
```

## Reference Documentation

| Resource | URL |
|----------|-----|
| llms-full.txt | https://vercel.com/docs/llms-full.txt |
| AI Resources | https://vercel.com/docs/ai-resources |
| MCP Server | https://vercel.com/docs/ai-resources/vercel-mcp |
| MCP Tools | https://vercel.com/docs/ai-resources/vercel-mcp/tools |
| REST API | https://vercel.com/docs/rest-api/reference/welcome |
| Serverless Functions | https://vercel.com/docs/functions |
| Edge Functions | https://vercel.com/docs/functions/edge-functions |

## Environment Variables

Set environment variables in Vercel dashboard or via CLI:

```bash
# Set environment variable
vercel env add MY_SECRET

# List environment variables
vercel env ls
```

## Post-Deployment: Register with ChatGPT

After deployment, register your MCP server URL with ChatGPT:

1. Go to ChatGPT Settings → Connectors
2. Create new connector:
   - **Name**: Your App Name
   - **MCP server URL**: `https://your-app.vercel.app`
   - **Authentication**: OAuth (if required)

## Troubleshooting

### Build Failures
```bash
# View build logs
vercel logs <deployment-url>
```

### Function Timeouts
- Free tier: 10 seconds max
- Pro tier: 60 seconds max
- Configure in `vercel.json`:
```json
{
  "functions": {
    "api/*.ts": {
      "maxDuration": 30
    }
  }
}
```

## Skills Required

- Understanding of serverless deployment
- MCP server architecture
- Vercel CLI and dashboard

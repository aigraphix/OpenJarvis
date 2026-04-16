---
name: nexus-agent-mcp
description: MCP (Model Context Protocol) discovery and integration module. Use when connecting to cloud API registries, discovering MCP servers, generating tool connectors, managing credentials/IAM, or enforcing governance policies on MCP tools.
---

# nexus-agent-mcp

## Overview

This module integrates MCP (Model Context Protocol) servers into Nexus agents.
It discovers tools, validates schemas, manages credentials, and enforces
governance policies.

## When to Use

Use this module when you need to:

- Discover MCP servers from registries or local configs
- Validate tool schemas for compatibility
- Generate agent-ready tool connectors
- Manage credentials and IAM for MCP access
- Enforce allowlists and governance policies
- Bootstrap agent capabilities from discovered tools

## Available Scripts

### Discovery

- `scripts/discover-mcp-servers.ts` - Find MCP servers from known locations
- `scripts/list-tools-from-server.ts` - Fetch tool list for a given server
- `scripts/registry-sync.ts` - Sync with cloud API registry

### Validation

- `scripts/validate-tool-schemas.ts` - Ensure schemas meet Nexus expectations
- `scripts/breaking-change-detector.ts` - Compare schemas to pinned baseline
- `scripts/compatibility-checker.ts` - Check tool compatibility with agents

### Health & Reliability

- `scripts/mcp-healthcheck.ts` - Verify server responds within timeout
- `scripts/timeout-policy-audit.ts` - Verify safe timeouts and retries

### Config Generation

- `scripts/generate-mcp-config.ts` - Generate agent-ready MCP config
- `scripts/merge-mcp-configs.ts` - Merge configs with conflict detection
- `scripts/credential-manager.ts` - Manage MCP credentials securely

## Agent Task: MCP Server Discovery & Connector Builder

**Trigger:** Request for new capability from agent

**Inputs:**

- Organization Cloud API Registry settings
- Desired tool categories (BigQuery, Compute, etc.)

**Outputs:**

- Ready-to-use tool descriptors
- Authentication key integrations

## Safety Conventions

- Default to deny: enable only required servers/tools
- Pin versions and capture schema baselines
- Log tool calls with correlation IDs for debugging

## References

- `references/integration-checklist.md` - Discovery → validation → rollout
- `references/schema-guidelines.md` - Tool schema expectations
- `references/governance-allowlisting.md` - Governance strategy
- `references/operations-playbook.md` - Timeouts, retries, circuit breaking

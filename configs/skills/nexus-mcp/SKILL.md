# Nexus MCP Integration Skill

---
name: MCP Integration
description: Model Context Protocol (MCP) server configuration and usage patterns
---

## Purpose

This skill documents how to configure and use MCP servers within Nexus,
providing agents access to external tools and services via the MCP protocol.

## Configured MCP Servers

### 1. Apify (Enabled ✅)

**URL**: `https://mcp.apify.com?tools=actors,docs,apify/rag-web-browser`

**Documentation**: https://github.com/apify/apify-mcp-server

**Available Tools**:

- `search-actors` - Search Apify Store for Actors
- `fetch-actor-details` - Get Actor metadata + input schema
- `call-actor` - Run an Actor and get results
- `apify/rag-web-browser` - RAG-optimized web browser for content extraction
- `search-apify-docs` - Search Apify documentation
- `get-dataset-items` - Retrieve scraped data from datasets
- `get-actor-run` - Check Actor run status
- `get-actor-log` - Get logs from Actor runs

**Use Cases**:

- Web scraping at scale
- RAG web content extraction
- Instagram/Twitter/Google scraping via Actors
- Automated data collection pipelines

### 2. Template (Disabled)

A template for adding stdio-based MCP servers.

## Adding New MCP Servers

### Hosted (HTTP/SSE)

```json
{
    "mcpServers": {
        "server-name": {
            "enabled": true,
            "url": "https://mcp.example.com",
            "description": "Description of server"
        }
    }
}
```

### Local (stdio)

```json
{
    "mcpServers": {
        "server-name": {
            "enabled": true,
            "command": "npx",
            "args": ["-y", "@package/mcp-server"],
            "env": {
                "API_KEY": "your-key"
            },
            "description": "Description of server"
        }
    }
}
```

## Agent Usage

Agents can access MCP tools through the standard tool calling interface. The MCP
tools appear alongside native tools.

Example workflow:

1. Agent receives task requiring web data
2. Agent calls `search-actors` to find appropriate Apify Actor
3. Agent calls `call-actor` with the selected Actor
4. Agent processes results from `get-dataset-items`

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Apify MCP Server](https://github.com/apify/apify-mcp-server)
- [Apify Actors Store](https://apify.com/store)

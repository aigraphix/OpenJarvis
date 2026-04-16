---
name: Unified Memory Layer
description: Access and manage the Nexus three-tier memory system (team_brain.md, SQLite, Supabase pgvector)
---

# Unified Memory Layer Skill

## Overview

The Nexus Unified Memory Layer provides a three-tier memory architecture:

- **Tier 1**: `team_brain.md` - Team knowledge, policies, SOPs
- **Tier 2**: `working_memory.db` - Session state, ephemeral facts
- **Tier 3**: Supabase pgvector - Semantic long-term user memories

## When to Use

Use this skill when you need to:

- Store learned facts, preferences, or decisions
- Query historical context for a user or task
- Persist important information across sessions
- Search for semantically similar memories

## Quick Commands

### Query All Tiers

```typescript
import { initializeNexusMemory } from "/Users/danny/Desktop/nexus/src/services/memory/index.js";

const { router } = await initializeNexusMemory({
    supabaseUrl: process.env.SUPABASE_URL!,
    supabaseKey: process.env.SUPABASE_ANON_KEY!,
    geminiApiKey: process.env.GEMINI_API_KEY,
});

const results = await router.query(userId, "search term");
console.log(results.mergedContext);
```

### Learn Something New (Triple-Write)

```typescript
await router.learn({
    key: "lesson.category.topic",
    value: "The learned fact or preference",
    markdown: "## Section Title\n\nMarkdown content for team_brain.md",
    source: "agent-name",
    userId: "optional-user-id",
    categories: ["preferences", "technical"],
});
```

### Direct SQLite Access (Tier 2)

```bash
sqlite3 memory/working_memory.db "SELECT key, value FROM state WHERE key LIKE 'antigravity.%'"
```

### Direct Supabase Search (Tier 3)

```typescript
import { getMemoryService } from "/Users/danny/Desktop/nexus/src/services/memory/index.js";

const memories = await getMemoryService().searchMemories(userId, "query", {
    topK: 5,
    threshold: 0.3,
    categories: ["preferences"],
});
```

## Files

| File                                           | Purpose                      |
| ---------------------------------------------- | ---------------------------- |
| `src/services/memory/index.ts`                 | Main exports and init helper |
| `src/services/memory/EmbeddingService.ts`      | Gemini embeddings            |
| `src/services/memory/SupabaseMemoryService.ts` | pgvector CRUD                |
| `src/services/memory/UnifiedMemoryRouter.ts`   | Three-tier coordinator       |
| `src/types/memory/index.ts`                    | TypeScript types             |

## Environment Variables Required

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_ROLE_KEY`
- `GEMINI_API_KEY`

## Health Check

```typescript
const health = await router.healthCheck();
// { tier1: true, tier2: true, tier3: true, details: {...} }
```

## Memory Categories

Use consistent categories for better retrieval:

- `preferences` - User preferences
- `technical` - Technical knowledge
- `project` - Project-specific info
- `personal` - Personal facts
- `work` - Work context
- `task` - Task-related
- `goal` - Goals and objectives
- `contact` - Contact information
- `habit` - User habits
- `idea` - Ideas and brainstorms

## Integration with Triple-Write Protocol

When learning something significant, agents MUST follow the Triple-Write
protocol:

1. **Tier 2 (SQLite)**: Store in `state` table with key
   `agentname.category.topic`
2. **Tier 1 (team_brain.md)**: Append markdown section
3. **Tier 3 (Supabase)**: Add with embedding if user-specific

The `router.learn()` method handles all three writes automatically.

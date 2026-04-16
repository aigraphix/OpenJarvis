---
name: nexus-ai-supabase
description: Supabase AI integration module for vector embeddings, edge functions, and real-time features. Use when deploying edge functions, managing vector stores (pgvector), wiring LLM chat to Supabase, handling real-time subscriptions, or enforcing RBAC/RLS in AI interactions.
---

# nexus-ai-supabase

## Overview

This module integrates Supabase capabilities with AI/LLM workflows. It handles
vector embeddings storage, edge function deployment, real-time subscriptions,
and secure data access patterns.

## When to Use

Use this module when you need to:

- Deploy Supabase Edge Functions with LLM endpoints
- Store and retrieve vector embeddings using pgvector
- Wire LLM prompts/responses to Supabase operations
- Manage real-time subscriptions for live features
- Enforce Row Level Security (RLS) in AI interactions
- Set up authentication and RBAC for AI features

## Available Scripts

### Edge Functions

- `scripts/edge-function-generator.ts` - Generate edge function templates from
  specs
- `scripts/edge-function-deploy.sh` - Deploy functions with CI templates
- `scripts/edge-function-local-dev.sh` - Run edge functions locally

### Vector Store

- `scripts/embedding-manager.ts` - Monitor and optimize vector embeddings
  storage
- `scripts/vector-index-optimizer.ts` - Recommend index configurations
- `scripts/embedding-migration.ts` - Migrate embeddings between schemas

### Real-Time

- `scripts/subscription-optimizer.ts` - Analyze and optimize subscription
  patterns
- `scripts/realtime-filter-config.ts` - Configure subscription filters

### Security

- `scripts/rls-validator.ts` - Verify RLS policies are enforced
- `scripts/rbac-schema-generator.ts` - Generate role-based access schemas

## Agent Tasks

### Edge Function Auto-Generator

**Trigger:** New feature request requiring backend logic **Inputs:** API schema,
LLM provider config, database mapping **Output:** Deployed edge functions with
tests

### Embedding Database Manager

**Trigger:** Slow embedding retrieval events **Inputs:** Embedding usage logs,
vector search latency **Output:** Index recommendations, retention policies

### Real-Time Subscription Optimizer

**Trigger:** Real-time UI lag reports **Inputs:** Active subscriptions, data
throughput, UI patterns **Output:** Filter recommendations, scaling settings

## References

- `references/data-model.md` - Supabase AI data model (chunks + embeddings)
- `references/rls-patterns.md` - RLS patterns for AI retrieval
- `references/chunking-guidelines.md` - Chunking sizes, overlap, metadata
- `references/edge-functions-checklist.md` - Deployment checklist

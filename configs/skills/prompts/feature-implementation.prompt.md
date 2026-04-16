---
name: Feature Implementation Guide
description: Use when planning and implementing a new feature end-to-end (spec, design, implementation, tests, rollout).
variables:
  - name: CONTEXT
    description: Product area, codebase modules, existing related behavior, and any constraints.
  - name: TASK_DESCRIPTION
    description: The feature request with acceptance criteria.
  - name: USERS_AND_USE_CASES
    description: Primary user personas and scenarios; include non-happy paths.
  - name: NON_FUNCTIONAL_REQUIREMENTS
    description: Performance, security, reliability, accessibility, compliance needs.
  - name: DEPENDENCIES
    description: APIs, services, data stores, third-party systems involved.
  - name: ROLLOUT_CONSTRAINTS
    description: Feature flags, backwards compatibility, migration constraints, timelines.
---

# Feature Implementation Guide

## Context
{{ CONTEXT }}

## Task
{{ TASK_DESCRIPTION }}

## Users and Use Cases
{{ USERS_AND_USE_CASES }}

## Non-functional Requirements
{{ NON_FUNCTIONAL_REQUIREMENTS }}

## Dependencies
{{ DEPENDENCIES }}

## Rollout Constraints
{{ ROLLOUT_CONSTRAINTS }}

## Constraints
- Keep scope aligned to acceptance criteria; defer nice-to-haves explicitly.
- Prefer incremental delivery with safe defaults.
- Avoid breaking changes unless a migration/compat plan is included.
- Tests and observability are part of “done.”

## Plan

### 1) Clarify Requirements
- Acceptance criteria (bullet list):
- Out of scope (explicit):
- Open questions:

### 2) Design Proposal
- Approach overview:
- API / UI changes:
- Data model changes:
- Error handling strategy:
- Security considerations:
- Performance considerations:

### 3) Implementation Steps (Incremental)
- Step 1 (scaffolding / interfaces):
- Step 2 (core logic):
- Step 3 (integration points):
- Step 4 (polish and edge cases):

### 4) Testing Strategy
- Unit tests:
- Integration tests:
- E2E tests:
- Contract tests / mocks:

### 5) Observability
- Logging events and levels:
- Metrics (counters/gauges/histograms):
- Tracing spans (if applicable):
- Dashboards/alerts:

### 6) Rollout Strategy
- Feature flag plan:
- Migration plan (if any):
- Backward compatibility:
- Rollback plan:

## Output Format
Provide output in this structure:

1. Summary
- What we’re building and why.

2. Acceptance Criteria
- Checklist.

3. Proposed Design
- Components/modules impacted.
- Data/API/UI changes.

4. Step-by-step Implementation Plan
- Ordered steps with estimated complexity and risk.

5. Test Plan
- What tests to add and where.

6. Rollout Plan
- Flags, migrations, monitoring, rollback.

7. Open Questions
- List.

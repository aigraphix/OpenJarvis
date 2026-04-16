---
name: Safe Refactoring Workflow
description: Use when improving structure without changing external behavior; emphasizes guardrails, small steps, and verification.
variables:
  - name: CONTEXT
    description: Codebase area, current pain points, constraints, and what must not change.
  - name: TASK_DESCRIPTION
    description: The refactor goal (readability, modularity, performance, de-duplication).
  - name: SCOPE
    description: Files/modules/functions included and excluded.
  - name: SAFETY_NET
    description: Existing tests, staging env, feature flags, monitoring.
  - name: RISKS
    description: Areas likely to break (concurrency, serialization, DB, API contracts).
---

# Safe Refactoring Workflow

## Context
{{ CONTEXT }}

## Task
{{ TASK_DESCRIPTION }}

## Scope
{{ SCOPE }}

## Safety Net
{{ SAFETY_NET }}

## Risks
{{ RISKS }}

## Constraints
- Do not change external behavior unless explicitly approved.
- Prefer many small commits over one big change.
- Preserve public APIs/contracts; deprecate rather than remove.
- Keep performance at least as good as before (measure if uncertain).

## Workflow

### 1) Define Invariants
- What outputs/side effects must remain the same?
- What public interfaces must remain stable?
- What performance/latency constraints must not regress?

### 2) Establish Baseline
- Run tests; record current status.
- Add characterization tests if behavior is under-specified.
- Capture key metrics (p95 latency, memory, query counts) if relevant.

### 3) Refactor in Small Steps
Typical safe sequence:
- Rename for clarity (no logic changes)
- Extract functions (pure refactors)
- Introduce interfaces/adapters
- Replace internals behind a stable boundary
- Remove dead code only after verifying no callers

### 4) Keep Changes Reviewable
- Limit PR size.
- Separate mechanical formatting from semantic changes.
- Use automated tools (formatter, linter) deliberately.

### 5) Verify Continuously
- Run unit tests after each step.
- Add targeted tests for risky paths.
- Manually smoke test critical flows.

### 6) Cleanup
- Remove temporary shims/flags when safe.
- Update docs/comments.
- Confirm new structure matches desired architecture.

## Output Format
Provide output in this structure:

1. Refactor Goal
- What will be improved and why.

2. Invariants
- Bullet list.

3. Step Plan
- Step-by-step with expected risk per step.

4. Test/Verification Plan
- Tests to run/add.
- Manual checks.

5. Rollout Plan (if applicable)
- Flags, monitoring, rollback.

6. Final Checklist
- Behavior unchanged
- Tests passing
- No dead code
- Docs updated

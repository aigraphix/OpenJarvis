---
name: Code Review Checklist
description: Use when reviewing a pull request or patch to assess correctness, safety, performance, and maintainability.
variables:
  - name: CONTEXT
    description: Repo/module context, PR link, relevant tickets, and what the change claims to do.
  - name: TASK_DESCRIPTION
    description: What you want reviewed (e.g., entire PR, specific files, or a risky diff section).
  - name: DIFF_OR_FILES
    description: The diff, file list, or key snippets to review.
  - name: RISK_PROFILE
    description: Expected risk level and blast radius (low/medium/high) and what could go wrong.
  - name: ENVIRONMENT
    description: Runtime assumptions (language, framework, platform, constraints).
---

# Code Review Checklist

## Context
{{ CONTEXT }}

## Task
{{ TASK_DESCRIPTION }}

## Inputs
{{ DIFF_OR_FILES }}

## Constraints
- Do not invent missing code; call out gaps explicitly.
- Prefer actionable, specific feedback with examples.
- Prioritize correctness and safety over style.
- Assume reviewers want quick, high-signal notes.

## Review Checklist

### 1) Intent and Scope
- What is the stated goal of this change?
- Does the implementation match the intent?
- Is there scope creep (unrelated edits)?

### 2) Correctness
- Are there obvious logic errors, off-by-one issues, incorrect conditions, or edge cases?
- Are error paths handled (null/undefined, exceptions, failed calls)?
- Are boundary conditions covered (empty inputs, large inputs, timeouts)?

### 3) Security and Privacy
- Any injection risks (SQL/command/template/URL)?
- Any secrets exposed (logs, errors, config)?
- Proper authz/authn checks and least privilege?
- Sensitive data handling (PII redaction, encryption, retention)?

### 4) Reliability and Resilience
- Idempotency for retries?
- Timeouts, retries, backoff, circuit breaking where appropriate?
- Concurrency issues (races, locks, shared state)?
- Failure modes: what happens when dependencies are down?

### 5) Performance
- Hot paths: unnecessary allocations, N+1 queries, heavy loops?
- Caching opportunities or invalidation problems?
- I/O patterns: batching, streaming, pagination?

### 6) Maintainability
- Naming clarity, modularity, separation of concerns.
- API boundaries: does it fit existing patterns?
- Comments/docstrings only where they add value.

### 7) Tests
- Are tests added/updated? Are they meaningful?
- Do tests cover edge cases and negative cases?
- Any flaky test risks (timing, randomness, external deps)?

### 8) Observability
- Logging: helpful, not noisy; avoids sensitive data.
- Metrics/tracing if this is a critical path.
- Clear error messages for operators.

### 9) Compatibility and Rollout
- Backward compatibility (schemas, APIs, clients)?
- Migration safety: rollout plan, feature flags, canary?
- Revert plan if something breaks.

## Risk Assessment
Risk profile: {{ RISK_PROFILE }}

- Blast radius:
- Worst-case failure:
- Most likely failure:
- Mitigations present:
- Recommended additional mitigations:

## Output Format
Provide output in this structure:

1. Summary
- What the change does in 2-5 bullets.

2. Must Fix (blocking)
- Bullet list with file/line references where possible.

3. Should Fix (non-blocking)
- Bullet list.

4. Nice to Have
- Bullet list.

5. Questions / Clarifications
- Bullet list.

6. Suggested Patch Snippets (optional)
- Minimal code suggestions, scoped to the issues above.

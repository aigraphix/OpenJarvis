---
name: Bug Investigation Workflow
description: Use when diagnosing and fixing a bug with unclear cause; guides systematic reproduction, narrowing, and verification.
variables:
  - name: CONTEXT
    description: Product/system area, environment, recent changes, and any links (issue, logs, PRs).
  - name: TASK_DESCRIPTION
    description: The bug statement and what “fixed” means.
  - name: SYMPTOMS
    description: Observed behavior, error messages, stack traces, user reports.
  - name: REPRO_STEPS
    description: Steps to reproduce, frequency, and whether it’s deterministic.
  - name: ENVIRONMENT
    description: Versions, config, OS, device, region, feature flags.
  - name: AVAILABLE_ARTIFACTS
    description: Logs, metrics, traces, screenshots, dumps, sample payloads.
---

# Bug Investigation Workflow

## Context
{{ CONTEXT }}

## Task
{{ TASK_DESCRIPTION }}

## Symptoms
{{ SYMPTOMS }}

## Reproduction
{{ REPRO_STEPS }}

## Environment
{{ ENVIRONMENT }}

## Artifacts
{{ AVAILABLE_ARTIFACTS }}

## Constraints
- Do not guess root cause; propose hypotheses and how to validate them.
- Prefer small, low-risk fixes; avoid refactors unless necessary.
- Preserve existing behavior outside the bug scope.
- Add/adjust tests to prevent regressions.

## Workflow

### 1) Confirm and Localize
- Restate expected vs actual behavior.
- Confirm whether the bug reproduces in:
  - Local dev
  - Staging
  - Production
- Identify the smallest reproducible case.

### 2) Triage Severity and Impact
- Who is impacted? How many? How often?
- Data loss, security, billing, or availability implications?
- Workarounds available?

### 3) Form Hypotheses
Create 3-5 candidate root causes. For each:
- Evidence supporting it
- Evidence against it
- A fast test to confirm/deny

### 4) Narrow the Search
- Bisect recent changes if applicable.
- Add temporary diagnostics (logs/metrics) if needed.
- Inspect inputs/outputs at boundaries (API edges, DB queries, parsing, serialization).

### 5) Implement a Fix
- Choose the smallest change that addresses the confirmed root cause.
- Handle edge cases explicitly.
- Consider backward compatibility and migrations.

### 6) Add Regression Coverage
- Add a test that fails before the fix and passes after.
- If hard to test, add a “canary” check or invariant assertion.

### 7) Validate End-to-End
- Re-run reproduction steps.
- Verify related flows are unaffected.
- Check logs/metrics for new errors or unusual patterns.

### 8) Rollout and Monitoring Plan
- Feature flag / staged rollout if risky.
- Define what to monitor (error rate, latency, specific log signature).
- Define rollback trigger.

## Output Format
Provide output in this structure:

1. Bug Summary
- Expected:
- Actual:
- Impact:

2. Reproduction Notes
- Deterministic? (yes/no)
- Minimal repro:

3. Hypotheses
- H1:
- H2:
- H3:

4. Root Cause (confirmed)
- Evidence:

5. Fix Plan
- Steps:
- Risks:

6. Patch (high level)
- Files to change:
- Key logic changes:

7. Tests
- New/updated tests:

8. Rollout / Monitoring
- Plan:
- Metrics/logs:
- Rollback:

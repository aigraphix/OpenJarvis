---
name: Test Creation Patterns
description: Use when adding tests for new features or bugs; focuses on choosing test types, structure, and maintainability.
variables:
  - name: CONTEXT
    description: Codebase/testing framework context and where tests live.
  - name: TASK_DESCRIPTION
    description: What behavior needs coverage (feature/bug/regression).
  - name: UNIT_UNDER_TEST
    description: Function/class/module/endpoint to test, including key inputs/outputs.
  - name: TEST_ENVIRONMENT
    description: Test runner, mocks, fixtures, DB usage, time control.
  - name: EDGE_CASES
    description: Important boundaries and negative cases to include.
---

# Test Creation Patterns

## Context
{{ CONTEXT }}

## Task
{{ TASK_DESCRIPTION }}

## Unit Under Test
{{ UNIT_UNDER_TEST }}

## Test Environment
{{ TEST_ENVIRONMENT }}

## Edge Cases
{{ EDGE_CASES }}

## Constraints
- Tests must be deterministic (no real network, controlled time/randomness).
- Prefer fast unit tests; add integration/E2E only where necessary.
- Each test should assert one behavior clearly.
- Tests should fail for the right reason (tight assertions, clear names).

## Patterns

### 1) Choose the Right Level
- Unit: pure logic, minimal deps, fast.
- Integration: real DB/FS/service boundary (or containerized) when needed.
- E2E: full user journey, minimal count, highest value only.

### 2) Structure (Arrange–Act–Assert)
- Arrange: build inputs/fixtures
- Act: call the unit
- Assert: verify outputs and side effects

### 3) Naming Convention
- should_<expected_behavior>_when_<condition>
- given_<context>_when_<action>_then_<outcome>

### 4) Fixtures and Mocks
- Prefer small, explicit fixtures.
- Mock at boundaries (HTTP clients, clocks, random, filesystem) rather than deep internals.
- Avoid over-mocking: verify meaningful behavior, not implementation details.

### 5) Coverage Checklist
- Happy path
- Validation errors / bad inputs
- Boundary values (empty, min/max, large payloads)
- Idempotency / retries (if applicable)
- Permissions / authz
- Time-dependent behavior (use fake clocks)
- Error propagation and messages

### 6) Anti-patterns to Avoid
- Sleeping for timing (use fake timers)
- Shared mutable global fixtures
- Order-dependent tests
- Assertions that duplicate the implementation logic

## Output Format
Provide output in this structure:

1. Test Plan
- What to test (bullets), mapped to behaviors/acceptance criteria.

2. Recommended Test Types
- Unit / Integration / E2E (with reasoning).

3. Test Cases
- Case 1: name + arrange/act/assert summary
- Case 2: ...

4. Example Skeletons
- Minimal code skeleton(s) for the framework in use.

5. Flakiness Controls
- How to control time/randomness/external deps.

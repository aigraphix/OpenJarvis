---
name: Architecture Decision Record (ADR)
description: Use when making an architectural decision that should be documented for future readers (tradeoffs, constraints, consequences).
variables:
  - name: CONTEXT
    description: System background, problem statement, and why a decision is needed now.
  - name: TASK_DESCRIPTION
    description: The decision to be made and its scope.
  - name: DRIVERS
    description: Key forces: business goals, constraints, risks, and requirements.
  - name: OPTIONS
    description: Candidate options considered (at least 2), including current/default.
  - name: DECISION_MAKERS
    description: Who is responsible/consulted and the date.
---

# Architecture Decision Record (ADR)

## Context
{{ CONTEXT }}

## Task
{{ TASK_DESCRIPTION }}

## Constraints
- Be explicit about assumptions.
- Evaluate at least two viable options (including “do nothing”).
- Record tradeoffs and consequences, not just the chosen option.
- Keep it readable for someone new to the system.

## Decision Drivers
{{ DRIVERS }}

## Considered Options
{{ OPTIONS }}

## Decision
- Status: Proposed | Accepted | Superseded | Deprecated
- Date:
- Decision Makers:
  {{ DECISION_MAKERS }}

## Rationale
- Why this option was chosen:
- Tradeoffs accepted:
- Risks and mitigations:

## High-level Design
- Components impacted:
- Data flow:
- Interfaces/APIs:
- Operational concerns (deploy, scaling, observability):

## Consequences
### Positive
- 

### Negative
- 

### Neutral / Follow-ups
- 

## Alternatives Rejected
For each rejected option:
- Why it was rejected
- What would need to change for it to become viable

## Rollout / Migration Plan
- Steps:
- Backward compatibility:
- Rollback plan:

## References
- Links to issues/PRs/docs:
- Related ADRs:

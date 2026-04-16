---
name: nexus-deploy
description: Secure deployment toolkit for Nexus services and agent runtimes. Use when deploying to staging/production, managing secrets, running security scans, setting up CI/CD hooks, or planning rollback strategies.
---

# nexus-deploy

## Overview

Secure-by-default deployment toolkit covering build hygiene, secrets handling,
infrastructure safety, runtime hardening, and verification gates.

## When to Use

Use this module when you need to:

- Deploy Nexus services to staging or production
- Create a safe release process (tagging, changelog, artifacts)
- Add verification gates (smoke tests, policy-as-code, scanning)
- Handle secrets securely (no plaintext in logs)
- Establish and practice rollback strategies
- Prepare deployments for audit/compliance

## Available Scripts

### Build & Artifacts

- `scripts/build-release-artifacts.sh` - Build and package deterministically
- `scripts/generate-sbom.ts` - Generate SBOM for dependencies
- `scripts/verify-artifacts.ts` - Validate checksums and version stamps

### Security Checks

- `scripts/secrets-leak-scan.sh` - Scan for secret leakage patterns
- `scripts/dependency-audit.sh` - Run vulnerability checks
- `scripts/runtime-hardening-audit.ts` - Ensure least-privilege settings

### Deploy & Verify

- `scripts/deploy-staging.sh` - Deploy to staging with env wiring
- `scripts/deploy-production-canary.sh` - Progressive rollout with health gates
- `scripts/smoke-test-post-deploy.ts` - Validate critical paths after deploy

### Rollback

- `scripts/rollback-last-release.sh` - Revert to last known good release
- `scripts/capture-release-context.ts` - Store "what changed" metadata

## Agent Task: Secure Deployment Orchestrator

**Trigger:** CI/CD pipeline step tagged for production rollout

**Inputs:**

- Agent build artifacts
- IAM policy config
- Environment vars

**Outputs:**

- Deployed agent
- Audit log of permissions assigned

## Agent Task: Performance Monitoring & Alerting

**Trigger:** Threshold breach events

**Inputs:**

- Metrics stream (latency, p95/p99, error rates)
- Threshold config

**Outputs:**

- Alerts
- Auto-scale suggestions

## Operational Conventions

- Prefer "promote artifacts" (staging → prod) over rebuilding
- Never print secrets; fail closed if required env vars missing
- Require rollback plan before deploying auth/billing/data changes

## References

- `references/deployment-checklist.md` - Preflight → deploy → verify → rollback
- `references/secrets-guide.md` - Secrets and environment management
- `references/release-process.md` - Tagging, versioning, changelog
- `references/hardening-baseline.md` - Runtime permissions, network, logging
- `references/incident-playbook.md` - Rollback triggers, comms, postmortem

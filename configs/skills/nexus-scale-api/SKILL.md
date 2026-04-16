---
name: nexus-scale-api
description: API scalability and resilience toolkit for Nexus services. Use when analyzing traffic patterns, recommending cache strategies, monitoring performance metrics (p95/p99 latency, error rates, throughput), or planning horizontal/vertical scaling. Triggers on high latency, error surges, or capacity planning requests.
---

# nexus-scale-api

## Overview

This module provides tools for API scalability analysis, performance monitoring,
and resilience planning. It helps identify bottlenecks, recommend caching
strategies, and plan scaling operations.

## When to Use

Use this module when you need to:

- Analyze API traffic patterns and request distributions
- Recommend caching layer configurations (Redis/Memcached)
- Monitor performance metrics (latency percentiles, error rates, throughput)
- Plan horizontal or vertical scaling strategies
- Configure load balancing and edge routing
- Set up asynchronous pipeline coordination (queues, message brokers)

## Available Scripts

### Traffic Analysis

- `scripts/api-traffic-analyzer.ts` - Analyze request rates, latency
  distributions, error logs
- `scripts/load-pattern-detector.ts` - Identify traffic patterns and peak hours

### Cache Strategy

- `scripts/cache-strategy-advisor.ts` - Recommend Redis/Memcached configurations
- `scripts/cache-hit-analyzer.ts` - Analyze cache effectiveness and miss
  patterns

### Performance Monitoring

- `scripts/performance-monitor.ts` - Collect p95/p99 latency, error rates,
  throughput
- `scripts/alert-threshold-config.ts` - Configure monitoring thresholds and
  alerts

### Scaling

- `scripts/scaling-blueprint-generator.ts` - Generate scaling recommendations
- `scripts/capacity-planner.ts` - Plan resource allocation for expected load

## Agent Task: API Traffic Strategy Planner

**Trigger:** High latency or error surge ≥ threshold

**Inputs:**

- Current request rates
- Response time distributions
- Failure/error logs

**Outputs:**

- Suggested load balancing configuration
- Caching layer plan
- Horizontal/vertical scaling triggers

## References

- `references/scaling-patterns.md` - Common scaling patterns and when to use
  them
- `references/cache-strategies.md` - Redis vs Memcached decision guide
- `references/monitoring-setup.md` - Setting up Prometheus/Grafana dashboards

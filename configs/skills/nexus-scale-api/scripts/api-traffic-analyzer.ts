#!/usr/bin/env node
/**
 * API Traffic Analyzer
 * Analyzes request rates, latency distributions, and error logs
 * 
 * Usage: node api-traffic-analyzer.ts [--logs <path>] [--threshold <ms>]
 */

interface RequestLog {
  timestamp: string;
  method: string;
  path: string;
  statusCode: number;
  latencyMs: number;
  userAgent?: string;
  ip?: string;
}

interface TrafficAnalysis {
  summary: {
    totalRequests: number;
    timeRange: { start: string; end: string };
    avgRequestsPerMinute: number;
  };
  latency: {
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
    max: number;
  };
  errors: {
    total: number;
    rate: number;
    byStatus: Record<number, number>;
    topPaths: Array<{ path: string; count: number }>;
  };
  endpoints: Array<{
    path: string;
    count: number;
    avgLatency: number;
    errorRate: number;
  }>;
  recommendations: string[];
}

function calculatePercentile(values: number[], percentile: number): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.ceil((percentile / 100) * sorted.length) - 1;
  return sorted[Math.max(0, index)];
}

function analyzeTraffic(logs: RequestLog[]): TrafficAnalysis {
  if (logs.length === 0) {
    return {
      summary: { totalRequests: 0, timeRange: { start: '', end: '' }, avgRequestsPerMinute: 0 },
      latency: { p50: 0, p75: 0, p90: 0, p95: 0, p99: 0, max: 0 },
      errors: { total: 0, rate: 0, byStatus: {}, topPaths: [] },
      endpoints: [],
      recommendations: ['No traffic data available']
    };
  }

  const timestamps = logs.map(l => new Date(l.timestamp).getTime()).sort((a, b) => a - b);
  const timeRangeMs = timestamps[timestamps.length - 1] - timestamps[0];
  const timeRangeMinutes = timeRangeMs / 60000 || 1;

  const latencies = logs.map(l => l.latencyMs);
  const errors = logs.filter(l => l.statusCode >= 400);

  // Group by endpoint
  const endpointStats = new Map<string, { count: number; latencies: number[]; errors: number }>();
  for (const log of logs) {
    const key = `${log.method} ${log.path}`;
    const stats = endpointStats.get(key) || { count: 0, latencies: [], errors: 0 };
    stats.count++;
    stats.latencies.push(log.latencyMs);
    if (log.statusCode >= 400) stats.errors++;
    endpointStats.set(key, stats);
  }

  // Error breakdown by status
  const errorByStatus: Record<number, number> = {};
  for (const err of errors) {
    errorByStatus[err.statusCode] = (errorByStatus[err.statusCode] || 0) + 1;
  }

  // Top error paths
  const errorPaths = new Map<string, number>();
  for (const err of errors) {
    const key = err.path;
    errorPaths.set(key, (errorPaths.get(key) || 0) + 1);
  }
  const topErrorPaths = [...errorPaths.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([path, count]) => ({ path, count }));

  // Generate recommendations
  const recommendations: string[] = [];
  const p95 = calculatePercentile(latencies, 95);
  const errorRate = errors.length / logs.length;

  if (p95 > 500) {
    recommendations.push(`⚠️ High p95 latency (${p95}ms). Consider caching or query optimization.`);
  }
  if (errorRate > 0.05) {
    recommendations.push(`⚠️ Error rate ${(errorRate * 100).toFixed(1)}% exceeds 5% threshold.`);
  }
  if (logs.length / timeRangeMinutes > 1000) {
    recommendations.push(`📈 High traffic (${Math.round(logs.length / timeRangeMinutes)} req/min). Consider horizontal scaling.`);
  }

  // Find slow endpoints
  for (const [path, stats] of endpointStats) {
    const avgLatency = stats.latencies.reduce((a, b) => a + b, 0) / stats.latencies.length;
    if (avgLatency > 1000 && stats.count > 10) {
      recommendations.push(`🐌 Slow endpoint: ${path} (avg ${Math.round(avgLatency)}ms)`);
    }
  }

  return {
    summary: {
      totalRequests: logs.length,
      timeRange: {
        start: new Date(timestamps[0]).toISOString(),
        end: new Date(timestamps[timestamps.length - 1]).toISOString()
      },
      avgRequestsPerMinute: Math.round(logs.length / timeRangeMinutes)
    },
    latency: {
      p50: calculatePercentile(latencies, 50),
      p75: calculatePercentile(latencies, 75),
      p90: calculatePercentile(latencies, 90),
      p95: calculatePercentile(latencies, 95),
      p99: calculatePercentile(latencies, 99),
      max: Math.max(...latencies)
    },
    errors: {
      total: errors.length,
      rate: errorRate,
      byStatus: errorByStatus,
      topPaths: topErrorPaths
    },
    endpoints: [...endpointStats.entries()]
      .map(([path, stats]) => ({
        path,
        count: stats.count,
        avgLatency: Math.round(stats.latencies.reduce((a, b) => a + b, 0) / stats.latencies.length),
        errorRate: stats.errors / stats.count
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10),
    recommendations
  };
}

// CLI execution
if (require.main === module) {
  // Demo with sample data
  const sampleLogs: RequestLog[] = [
    { timestamp: new Date().toISOString(), method: 'GET', path: '/api/users', statusCode: 200, latencyMs: 45 },
    { timestamp: new Date().toISOString(), method: 'GET', path: '/api/users', statusCode: 200, latencyMs: 52 },
    { timestamp: new Date().toISOString(), method: 'POST', path: '/api/orders', statusCode: 201, latencyMs: 120 },
    { timestamp: new Date().toISOString(), method: 'GET', path: '/api/products', statusCode: 500, latencyMs: 2500 },
  ];

  const analysis = analyzeTraffic(sampleLogs);
  console.log(JSON.stringify(analysis, null, 2));
}

export { analyzeTraffic, RequestLog, TrafficAnalysis };

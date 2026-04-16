#!/usr/bin/env node
/**
 * Performance Monitor
 * Collects p95/p99 latency, error rates, and throughput metrics
 * 
 * Usage: node performance-monitor.ts [--interval <seconds>] [--endpoint <url>]
 */

interface MetricPoint {
  timestamp: number;
  value: number;
}

interface PerformanceMetrics {
  timestamp: string;
  latency: {
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
    mean: number;
  };
  throughput: {
    requestsPerSecond: number;
    bytesPerSecond: number;
  };
  errors: {
    rate: number;
    count: number;
    types: Record<string, number>;
  };
  resources: {
    cpuPercent: number;
    memoryMb: number;
    activeConnections: number;
  };
  health: 'healthy' | 'degraded' | 'critical';
  alerts: string[];
}

interface ThresholdConfig {
  latencyP95Max: number;
  latencyP99Max: number;
  errorRateMax: number;
  cpuPercentMax: number;
  memoryMbMax: number;
}

const DEFAULT_THRESHOLDS: ThresholdConfig = {
  latencyP95Max: 500,
  latencyP99Max: 1000,
  errorRateMax: 0.05,
  cpuPercentMax: 80,
  memoryMbMax: 1024
};

class PerformanceMonitor {
  private latencyBuffer: number[] = [];
  private requestCount = 0;
  private errorCount = 0;
  private bytesTransferred = 0;
  private startTime = Date.now();
  private thresholds: ThresholdConfig;

  constructor(thresholds: Partial<ThresholdConfig> = {}) {
    this.thresholds = { ...DEFAULT_THRESHOLDS, ...thresholds };
  }

  recordRequest(latencyMs: number, bytes: number, isError: boolean, errorType?: string) {
    this.latencyBuffer.push(latencyMs);
    this.requestCount++;
    this.bytesTransferred += bytes;
    if (isError) this.errorCount++;

    // Keep buffer manageable
    if (this.latencyBuffer.length > 10000) {
      this.latencyBuffer = this.latencyBuffer.slice(-5000);
    }
  }

  private calculatePercentile(values: number[], percentile: number): number {
    if (values.length === 0) return 0;
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  getMetrics(): PerformanceMetrics {
    const elapsedSeconds = (Date.now() - this.startTime) / 1000 || 1;
    const latencies = this.latencyBuffer;

    const p95 = this.calculatePercentile(latencies, 95);
    const p99 = this.calculatePercentile(latencies, 99);
    const errorRate = this.requestCount > 0 ? this.errorCount / this.requestCount : 0;

    // Determine health status
    const alerts: string[] = [];
    let health: 'healthy' | 'degraded' | 'critical' = 'healthy';

    if (p95 > this.thresholds.latencyP95Max) {
      alerts.push(`p95 latency (${p95}ms) exceeds threshold (${this.thresholds.latencyP95Max}ms)`);
      health = 'degraded';
    }
    if (p99 > this.thresholds.latencyP99Max) {
      alerts.push(`p99 latency (${p99}ms) exceeds threshold (${this.thresholds.latencyP99Max}ms)`);
      health = 'critical';
    }
    if (errorRate > this.thresholds.errorRateMax) {
      alerts.push(`Error rate (${(errorRate * 100).toFixed(1)}%) exceeds threshold (${this.thresholds.errorRateMax * 100}%)`);
      health = 'critical';
    }

    return {
      timestamp: new Date().toISOString(),
      latency: {
        p50: this.calculatePercentile(latencies, 50),
        p75: this.calculatePercentile(latencies, 75),
        p90: this.calculatePercentile(latencies, 90),
        p95,
        p99,
        mean: latencies.length > 0 ? latencies.reduce((a, b) => a + b, 0) / latencies.length : 0
      },
      throughput: {
        requestsPerSecond: this.requestCount / elapsedSeconds,
        bytesPerSecond: this.bytesTransferred / elapsedSeconds
      },
      errors: {
        rate: errorRate,
        count: this.errorCount,
        types: {}
      },
      resources: {
        cpuPercent: 0, // Would need system-level access
        memoryMb: process.memoryUsage().heapUsed / 1024 / 1024,
        activeConnections: 0
      },
      health,
      alerts
    };
  }

  reset() {
    this.latencyBuffer = [];
    this.requestCount = 0;
    this.errorCount = 0;
    this.bytesTransferred = 0;
    this.startTime = Date.now();
  }
}

// CLI execution
if (require.main === module) {
  const monitor = new PerformanceMonitor();

  // Simulate some requests
  for (let i = 0; i < 1000; i++) {
    const latency = Math.random() * 200 + 20;
    const isError = Math.random() < 0.03;
    monitor.recordRequest(latency, Math.floor(Math.random() * 5000), isError);
  }

  // Add some slow requests
  for (let i = 0; i < 50; i++) {
    monitor.recordRequest(Math.random() * 2000 + 500, 10000, false);
  }

  const metrics = monitor.getMetrics();
  console.log(JSON.stringify(metrics, null, 2));
}

export { PerformanceMonitor, PerformanceMetrics, ThresholdConfig };

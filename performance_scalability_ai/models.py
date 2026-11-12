"""
Day 60: Performance Tuning & Scalability - Core Data Models
Platform: Zecpath Enterprise Automated Hiring Platform
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import time
import uuid


class OptimizationLevel(str, Enum):
    BASELINE = "BASELINE"
    CACHED = "CACHED"
    QUANTIZED_FAST_PATH = "QUANTIZED_FAST_PATH"
    MAX_OPTIMIZED = "MAX_OPTIMIZED"


class LoadBalancingAlgorithm(str, Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_CONNECTIONS = "LEAST_CONNECTIONS"
    WEIGHTED_RESPONSE_TIME = "WEIGHTED_RESPONSE_TIME"
    IP_HASH = "IP_HASH"


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    weight: int = 100
    active_connections: int = 0
    total_requests_served: int = 0
    avg_latency_ms: float = 20.0
    cpu_utilization_pct: float = 35.0
    memory_utilization_pct: float = 40.0
    health_status: HealthStatus = HealthStatus.HEALTHY
    last_heartbeat: float = field(default_factory=time.time)

    def is_available(self) -> bool:
        return self.health_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)


@dataclass
class BatchProcessingConfig:
    batch_size: int = 32
    max_wait_ms: float = 50.0
    worker_threads: int = 4
    max_queue_depth: int = 1000
    circuit_breaker_error_threshold: float = 0.20


@dataclass
class BatchResult:
    batch_id: str
    total_items: int
    successful_items: int
    failed_items: int
    duration_ms: float
    throughput_items_per_sec: float
    avg_item_latency_ms: float
    items: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    tier1_items: int = 0
    tier2_items: int = 0
    current_size_bytes: int = 0
    max_size_bytes: int = 128 * 1024 * 1024  # 128 MB default
    hit_ratio_pct: float = 0.0

    def update_hit_ratio(self):
        total = self.hits + self.misses
        if total > 0:
            self.hit_ratio_pct = round((self.hits / total) * 100.0, 2)
        else:
            self.hit_ratio_pct = 0.0


@dataclass
class ScalingPolicy:
    service_name: str
    min_replicas: int = 2
    max_replicas: int = 16
    target_cpu_pct: float = 70.0
    target_queue_depth: int = 150
    scale_up_step: int = 2
    scale_down_step: int = 1
    scale_up_cooldown_sec: float = 30.0
    scale_down_cooldown_sec: float = 60.0


@dataclass
class ScalingEvent:
    event_id: str = field(default_factory=lambda: f"SCALE-{uuid.uuid4().hex[:8].upper()}")
    timestamp: float = field(default_factory=time.time)
    service_name: str = ""
    action: str = "SCALE_UP"  # SCALE_UP or SCALE_DOWN
    previous_replicas: int = 2
    new_replicas: int = 4
    trigger_metric: str = "cpu_utilization_pct"
    trigger_value: float = 85.0
    reason: str = ""


@dataclass
class BenchmarkReport:
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    duration_sec: float
    throughput_rps: float
    p50_latency_ms: float
    p90_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    error_rate_pct: float
    memory_peak_mb: float
    cache_hit_rate_pct: float


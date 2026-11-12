"""
Day 60: Horizontal Scaling Engine
Load Balancer & Microservice Auto-Scaler
Platform: Zecpath Automated Hiring Platform
"""

import time
import math
import hashlib
from typing import List, Dict, Optional, Any
from performance_scalability_ai.models import (
    ServiceInstance,
    LoadBalancingAlgorithm,
    HealthStatus,
    ScalingPolicy,
    ScalingEvent,
)


class ServiceLoadBalancer:
    """
    Intelligent Microservice Load Balancer.
    Routes incoming candidate requests across active service instances
    using Round-Robin, Least-Connections, or Latency-Weighted algorithms.
    """

    def __init__(self, service_name: str, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS):
        self.service_name = service_name
        self.algorithm = algorithm
        self.instances: Dict[str, ServiceInstance] = {}
        self._round_robin_idx = 0

    def register_instance(self, instance: ServiceInstance):
        self.instances[instance.instance_id] = instance

    def deregister_instance(self, instance_id: str):
        if instance_id in self.instances:
            del self.instances[instance_id]

    def get_healthy_instances(self) -> List[ServiceInstance]:
        return [inst for inst in self.instances.values() if inst.is_available()]

    def route_request(self, client_ip: Optional[str] = None) -> Optional[ServiceInstance]:
        """
        Selects optimal service instance according to configured algorithm.
        """
        available = self.get_healthy_instances()
        if not available:
            return None

        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            inst = available[self._round_robin_idx % len(available)]
            self._round_robin_idx = (self._round_robin_idx + 1) % len(available)
            inst.active_connections += 1
            inst.total_requests_served += 1
            return inst

        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            # Pick instance with minimum active connections
            selected = min(available, key=lambda x: x.active_connections)
            selected.active_connections += 1
            selected.total_requests_served += 1
            return selected

        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_RESPONSE_TIME:
            # Pick healthy instance with lowest avg latency
            selected = min(available, key=lambda x: x.avg_latency_ms)
            selected.active_connections += 1
            selected.total_requests_served += 1
            return selected

        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            ip = client_ip or "127.0.0.1"
            h = int(hashlib.md5(ip.encode("utf-8")).hexdigest(), 16)
            selected = available[h % len(available)]
            selected.active_connections += 1
            selected.total_requests_served += 1
            return selected

        return available[0]

    def release_connection(self, instance_id: str, request_latency_ms: float = 20.0):
        """Releases active connection count and updates rolling latency average."""
        if instance_id in self.instances:
            inst = self.instances[instance_id]
            inst.active_connections = max(0, inst.active_connections - 1)
            # Update exponential rolling average latency
            inst.avg_latency_ms = round((inst.avg_latency_ms * 0.8) + (request_latency_ms * 0.2), 2)


class MicroserviceAutoScaler:
    """
    Kubernetes HPA (Horizontal Pod Autoscaler) Style Auto-Scaler.
    Monitors aggregate CPU utilization and queue depth, scaling replicas up or down
    within bounds while enforcing stabilization cooldown windows.
    """

    def __init__(self, policy: ScalingPolicy):
        self.policy = policy
        self.current_replicas = policy.min_replicas
        self.scaling_history: List[ScalingEvent] = []
        self.last_scale_time = time.time() - 100.0  # Allow immediate first scale

    def evaluate_and_scale(
        self, current_cpu_pct: float, current_queue_depth: int
    ) -> Optional[ScalingEvent]:
        """
        Evaluates metrics against policy and scales replicas if needed.
        Formula: Desired = ceil(Current * (CurrentMetric / TargetMetric))
        """
        now = time.time()

        # Check CPU scale trigger
        cpu_scale_ratio = current_cpu_pct / max(1.0, self.policy.target_cpu_pct)
        # Check Queue scale trigger
        queue_scale_ratio = current_queue_depth / max(1, self.policy.target_queue_depth)

        governing_ratio = max(cpu_scale_ratio, queue_scale_ratio)

        desired_replicas = math.ceil(self.current_replicas * governing_ratio)
        desired_replicas = max(self.policy.min_replicas, min(self.policy.max_replicas, desired_replicas))

        # Check scale up
        if desired_replicas > self.current_replicas:
            if (now - self.last_scale_time) < self.policy.scale_up_cooldown_sec:
                return None  # In cooldown

            event = ScalingEvent(
                service_name=self.policy.service_name,
                action="SCALE_UP",
                previous_replicas=self.current_replicas,
                new_replicas=desired_replicas,
                trigger_metric="cpu_pct" if cpu_scale_ratio >= queue_scale_ratio else "queue_depth",
                trigger_value=current_cpu_pct if cpu_scale_ratio >= queue_scale_ratio else float(current_queue_depth),
                reason=f"Load spike detected (Ratio: {governing_ratio:.2f}). Scaling up to handle traffic.",
            )
            self.current_replicas = desired_replicas
            self.last_scale_time = now
            self.scaling_history.append(event)
            return event

        # Check scale down
        elif desired_replicas < self.current_replicas:
            if (now - self.last_scale_time) < self.policy.scale_down_cooldown_sec:
                return None  # In cooldown

            event = ScalingEvent(
                service_name=self.policy.service_name,
                action="SCALE_DOWN",
                previous_replicas=self.current_replicas,
                new_replicas=desired_replicas,
                trigger_metric="cpu_pct",
                trigger_value=current_cpu_pct,
                reason=f"Traffic subsided. Scaling down to conserve compute resources.",
            )
            self.current_replicas = desired_replicas
            self.last_scale_time = now
            self.scaling_history.append(event)
            return event

        return None


class HorizontalScalingManager:
    """
    Unified Horizontal Scaling & Load Balancing Manager.
    Orchestrates instances, routes traffic, and scales microservices automatically.
    """

    def __init__(self, service_name: str, policy: Optional[ScalingPolicy] = None):
        self.service_name = service_name
        self.policy = policy or ScalingPolicy(service_name=service_name)
        self.load_balancer = ServiceLoadBalancer(
            service_name=service_name, algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS
        )
        self.auto_scaler = MicroserviceAutoScaler(policy=self.policy)

        # Initialize baseline replicas
        for i in range(self.policy.min_replicas):
            self._add_instance(f"{service_name}-inst-{i+1}", 8080 + i)

    def _add_instance(self, instance_id: str, port: int):
        inst = ServiceInstance(
            instance_id=instance_id,
            service_name=self.service_name,
            host="10.0.4.12",
            port=port,
            health_status=HealthStatus.HEALTHY,
        )
        self.load_balancer.register_instance(inst)

    def synchronize_cluster(self, current_cpu_pct: float, current_queue_depth: int) -> Optional[ScalingEvent]:
        """
        Runs auto-scaler evaluation and syncs load balancer instances to desired replica count.
        """
        event = self.auto_scaler.evaluate_and_scale(current_cpu_pct, current_queue_depth)
        if event:
            # Sync load balancer instances
            current_count = len(self.load_balancer.instances)
            target_count = event.new_replicas

            if target_count > current_count:
                for i in range(current_count, target_count):
                    self._add_instance(f"{self.service_name}-inst-{i+1}", 8080 + i)
            elif target_count < current_count:
                keys_to_remove = list(self.load_balancer.instances.keys())[target_count:]
                for k in keys_to_remove:
                    self.load_balancer.deregister_instance(k)

        return event


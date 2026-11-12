"""
Unit Tests for Day 60: Performance Tuning & Scalability
Platform: Zecpath Automated Hiring Platform
"""

import pytest
import time
from performance_scalability_ai import (
    OptimizationLevel,
    LoadBalancingAlgorithm,
    ServiceInstance,
    BatchProcessingConfig,
    ScalingPolicy,
    InferenceOptimizer,
    TwoTierMemoryCache,
    DynamicResumeBatchProcessor,
    ServiceLoadBalancer,
    MicroserviceAutoScaler,
    HorizontalScalingManager,
    SimulatedLoadTester,
)


class TestInferenceOptimizer:
    def setup_method(self):
        self.optimizer = InferenceOptimizer()
        self.sample_text = (
            "We deployed a distributed system using Kubernetes and Kafka with replica set to prevent partition loss. "
            "We optimized latency vs throughput with batching, maintaining 25ms p99 latency under 15000 RPS. "
            "We used mutex locks and thread pools to avoid race conditions."
        )

    def test_baseline_inference(self):
        res = self.optimizer.optimize_scoring_inference(self.sample_text, OptimizationLevel.BASELINE)
        assert res["optimization_level"] == "BASELINE"
        assert res["depth_index"] > 50.0
        assert res["mechanism_count"] >= 3
        assert res["tradeoff_count"] >= 1
        assert res["latency_ms"] > 0.0

    def test_max_optimized_inference(self):
        res = self.optimizer.optimize_scoring_inference(self.sample_text, OptimizationLevel.MAX_OPTIMIZED)
        assert res["optimization_level"] == "MAX_OPTIMIZED"
        assert res["depth_index"] > 50.0
        assert res["speedup_factor"] > 1.0

    def test_early_exit_on_short_response(self):
        short_text = "Yes, I agree."
        res = self.optimizer.optimize_scoring_inference(short_text, OptimizationLevel.MAX_OPTIMIZED)
        assert res["depth_index"] == 15.0
        assert res["mechanism_count"] == 0
        assert res["speedup_factor"] > 5.0

    def test_benchmark_speedup_generation(self):
        report = self.optimizer.benchmark_subsystem_speedup("tech_scoring")
        assert report["subsystem"] == "tech_scoring"
        assert "x" in report["speedup_multiplier"]
        assert "%" in report["latency_reduction_pct"]
        assert report["status"] == "OPTIMAL"


class TestTwoTierMemoryCache:
    def setup_method(self):
        self.cache = TwoTierMemoryCache(max_memory_bytes=1024 * 1024, l1_max_items=5)

    def test_l1_set_and_get(self):
        self.cache.set("session-101", {"status": "ACTIVE", "score": 92.5})
        val = self.cache.get("session-101")
        assert val is not None
        assert val["score"] == 92.5
        metrics = self.cache.get_metrics()
        assert metrics.hits == 1
        assert metrics.tier1_items == 1

    def test_l2_set_get_and_promotion(self):
        # Insert to L2 compressed store
        self.cache.set_l2("dossier-404", {"candidate": "Priya", "verdict": "OFFER"}, ttl_sec=60.0)
        assert self.cache.get_metrics().tier2_items == 1

        # Retrieval should decompress and promote to L1
        val = self.cache.get("dossier-404")
        assert val is not None
        assert val["candidate"] == "Priya"
        metrics = self.cache.get_metrics()
        assert metrics.hits == 1
        assert metrics.tier1_items == 1  # Promoted to L1

    def test_cache_miss_and_hit_ratio(self):
        val = self.cache.get("non-existent-key")
        assert val is None
        metrics = self.cache.get_metrics()
        assert metrics.misses == 1

    def test_ttl_expiration(self):
        self.cache.set_l2("temp-session", {"data": 123}, ttl_sec=0.05)
        time.sleep(0.08)
        val = self.cache.get("temp-session")
        assert val is None  # Should be expired

    def test_l1_lru_eviction(self):
        # Insert 7 items into L1 with capacity 5
        for i in range(7):
            self.cache.set_l1(f"key-{i}", f"value-{i}")

        metrics = self.cache.get_metrics()
        assert metrics.tier1_items <= 5
        assert metrics.evictions >= 2


class TestDynamicResumeBatchProcessor:
    def setup_method(self):
        config = BatchProcessingConfig(batch_size=16, worker_threads=2)
        self.processor = DynamicResumeBatchProcessor(config=config)

    def teardown_method(self):
        self.processor.shutdown()

    def test_single_resume_processing(self):
        resume = {
            "candidate_id": "CAND-001",
            "skills": ["Python", "FastAPI", "Docker", "AWS"],
            "experience_years": 5.5,
            "target_role": "Backend Architect",
        }
        res = self.processor._process_single_resume(resume)
        assert res["candidate_id"] == "CAND-001"
        assert res["qualification_status"] == "QUALIFIED_SENIOR"
        assert res["match_score"] > 60.0

    def test_batch_processing_execution(self):
        resumes = [
            {
                "candidate_id": f"CAND-BATCH-{i}",
                "skills": ["Python", "Docker"] if i % 2 == 0 else ["Java", "SQL"],
                "experience_years": 3.0,
            }
            for i in range(20)
        ]
        result = self.processor.process_batch(resumes)
        assert result.total_items == 20
        assert result.successful_items == 20
        assert result.failed_items == 0
        assert result.throughput_items_per_sec > 0.0

    def test_batch_vs_sequential_speedup(self):
        report = self.processor.benchmark_batch_vs_sequential(resume_count=30)
        assert report["resume_count"] == 30
        assert "x" in report["speedup_factor"]
        assert "%" in report["efficiency_gain_pct"]


class TestHorizontalScalingAndLoadBalancing:
    def setup_method(self):
        self.lb = ServiceLoadBalancer(
            service_name="scoring-service", algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS
        )
        self.inst1 = ServiceInstance("inst-1", "scoring-service", "10.0.1.1", 8080, avg_latency_ms=15.0)
        self.inst2 = ServiceInstance("inst-2", "scoring-service", "10.0.1.2", 8081, avg_latency_ms=25.0)
        self.lb.register_instance(self.inst1)
        self.lb.register_instance(self.inst2)

    def test_least_connections_routing(self):
        self.inst1.active_connections = 5
        self.inst2.active_connections = 1

        selected = self.lb.route_request()
        assert selected is not None
        assert selected.instance_id == "inst-2"  # Picked lower active connection

        self.lb.release_connection("inst-2", request_latency_ms=20.0)
        assert self.inst2.active_connections == 1  # 1 before + 1 route - 1 release = 1

    def test_round_robin_routing(self):
        self.lb.algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        first = self.lb.route_request()
        second = self.lb.route_request()
        assert first is not None and second is not None
        assert first.instance_id != second.instance_id

    def test_auto_scaler_scale_up_trigger(self):
        policy = ScalingPolicy(
            service_name="scoring-service", min_replicas=2, max_replicas=10, target_cpu_pct=70.0
        )
        scaler = MicroserviceAutoScaler(policy=policy)

        # Trigger high CPU load (85%)
        event = scaler.evaluate_and_scale(current_cpu_pct=85.0, current_queue_depth=50)
        assert event is not None
        assert event.action == "SCALE_UP"
        assert event.new_replicas > event.previous_replicas
        assert scaler.current_replicas == event.new_replicas

    def test_auto_scaler_cooldown_prevention(self):
        policy = ScalingPolicy(
            service_name="scoring-service",
            min_replicas=2,
            max_replicas=10,
            target_cpu_pct=70.0,
            scale_up_cooldown_sec=60.0,
        )
        scaler = MicroserviceAutoScaler(policy=policy)
        # First scale up succeeds
        _ = scaler.evaluate_and_scale(current_cpu_pct=85.0, current_queue_depth=50)
        # Second immediate scale up blocked by cooldown
        blocked_event = scaler.evaluate_and_scale(current_cpu_pct=95.0, current_queue_depth=100)
        assert blocked_event is None

    def test_horizontal_scaling_manager_sync(self):
        manager = HorizontalScalingManager(service_name="api-gateway")
        assert len(manager.load_balancer.instances) == 2  # min replicas

        # High load triggers scale up and synchronizes load balancer pool
        event = manager.synchronize_cluster(current_cpu_pct=85.0, current_queue_depth=200)
        assert event is not None
        assert len(manager.load_balancer.instances) == event.new_replicas


class TestSimulatedLoadTester:
    def test_load_test_execution(self):
        tester = SimulatedLoadTester()
        report = tester.run_load_test(
            test_name="Unit Load Test",
            total_requests=40,
            concurrent_users=4,
        )
        assert report.total_requests == 40
        assert report.successful_requests == 40
        assert report.failed_requests == 0
        assert report.throughput_rps > 0.0
        assert report.p50_latency_ms > 0.0
        assert report.p99_latency_ms >= report.p50_latency_ms
        assert report.error_rate_pct == 0.0


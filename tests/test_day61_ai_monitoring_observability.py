"""
Unit Tests for Day 61: AI Monitoring & Observability
Platform: Zecpath Automated Hiring Platform
"""

import unittest
import time
from ai_monitoring_observability import (
    LogLevel,
    AlertSeverity,
    AlertStatus,
    StructuredAILogger,
    MetricsCollector,
    AlertingEngine,
    DecisionAuditLogger,
    MonitoringDashboardEngine,
)


class TestStructuredAILogger(unittest.TestCase):
    def setUp(self):
        self.logger = StructuredAILogger(buffer_capacity=100)

    def test_log_api_request(self):
        entry = self.logger.log_api_request(
            endpoint="/api/v1/scoring/evaluate",
            method="POST",
            status_code=200,
            latency_ms=1.45,
            client_ip="192.168.1.10",
            candidate_id="CAND-091",
            payload={"turn": 3, "topic": "Kafka"},
        )
        self.assertEqual(entry.endpoint, "/api/v1/scoring/evaluate")
        self.assertEqual(entry.status_code, 200)
        self.assertEqual(entry.candidate_id, "CAND-091")
        self.assertTrue(entry.trace_id.startswith("TR-"))
        self.assertTrue(len(entry.payload_hash) > 0)
        self.assertEqual(len(self.logger.api_logs), 1)

    def test_log_model_output(self):
        entry = self.logger.log_model_output(
            candidate_id="CAND-091",
            subsystem="tech_scoring",
            input_text="We used Kafka replica sets to handle partitions.",
            output_tokens=38,
            confidence_score=0.965,
            predicted_grade="STRONG_HIRE",
            inference_latency_ms=0.065,
            explainability_factors={"semantic_depth": 0.88, "system_architecture": 0.94},
        )
        self.assertEqual(entry.candidate_id, "CAND-091")
        self.assertEqual(entry.subsystem, "tech_scoring")
        self.assertEqual(entry.predicted_grade, "STRONG_HIRE")
        self.assertGreater(entry.confidence_score, 0.9)
        self.assertEqual(len(self.logger.model_logs), 1)

    def test_log_error(self):
        entry = self.logger.log_error(
            error_type="InferenceTimeoutException",
            message="Model evaluation timeout on thread worker 3",
            subsystem="behavioral_ai",
            severity=LogLevel.ERROR,
            recoverable=True,
        )
        self.assertEqual(entry.error_type, "InferenceTimeoutException")
        self.assertEqual(entry.severity, LogLevel.ERROR)
        self.assertTrue(entry.recoverable)
        self.assertEqual(len(self.logger.error_logs), 1)

    def test_query_logs_by_candidate(self):
        self.logger.log_api_request("/api/v1/turn", candidate_id="CAND-A")
        self.logger.log_api_request("/api/v1/turn", candidate_id="CAND-B")
        self.logger.log_model_output("CAND-A", "scoring", "text", 10, 0.9, "OFFER", 0.05)

        logs_a = self.logger.get_logs_by_candidate("CAND-A")
        self.assertEqual(len(logs_a), 2)
        logs_b = self.logger.get_logs_by_candidate("CAND-B")
        self.assertEqual(len(logs_b), 1)


class TestMetricsCollector(unittest.TestCase):
    def setUp(self):
        self.collector = MetricsCollector()

    def test_record_requests_and_percentiles(self):
        # Insert 10 latency measurements: 1ms to 10ms
        for lat in range(1, 11):
            self.collector.record_request(latency_ms=float(lat), success=True)

        snapshot = self.collector.get_snapshot()
        self.assertEqual(snapshot.total_requests, 10)
        self.assertEqual(snapshot.error_rate_pct, 0.0)
        self.assertGreaterEqual(snapshot.p50_latency_ms, 5.0)
        self.assertGreaterEqual(snapshot.p99_latency_ms, 9.0)

    def test_model_accuracy_calculation(self):
        # 19 correct predictions, 1 incorrect prediction = 95.0% accuracy
        for _ in range(19):
            self.collector.record_model_accuracy(matches_ground_truth_or_rubric=True, confidence=0.92)
        self.collector.record_model_accuracy(matches_ground_truth_or_rubric=False, confidence=0.65)

        snapshot = self.collector.get_snapshot()
        self.assertEqual(snapshot.model_accuracy_pct, 95.0)

    def test_failure_rate_computation(self):
        self.collector.record_request(latency_ms=1.0, success=True)
        self.collector.record_request(latency_ms=1.2, success=True)
        self.collector.record_request(latency_ms=1.5, success=False)
        self.collector.record_request(latency_ms=1.1, success=True)

        snapshot = self.collector.get_snapshot()
        self.assertEqual(snapshot.total_requests, 4)
        self.assertEqual(snapshot.error_rate_pct, 25.0)

    def test_detailed_report_generation(self):
        self.collector.record_request(latency_ms=2.5, success=True)
        self.collector.record_model_accuracy(matches_ground_truth_or_rubric=True, confidence=0.95)
        report = self.collector.get_detailed_report()

        self.assertIn("response_time", report)
        self.assertIn("accuracy", report)
        self.assertIn("failure_rates", report)
        self.assertTrue(report["response_time"]["sla_compliant"])


class TestAlertingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AlertingEngine()
        self.collector = MetricsCollector()

    def test_default_rules_registration(self):
        self.assertIn("RULE-LAT-P99", self.engine.rules)
        self.assertIn("RULE-ERR-SURGE", self.engine.rules)
        self.assertIn("RULE-MODEL-DRIFT", self.engine.rules)

    def test_latency_spike_alert_trigger(self):
        # Simulate P99 latency breach (> 20ms) while P50 stays normal (< 10ms)
        for _ in range(19):
            self.collector.record_request(latency_ms=2.0, success=True)
        self.collector.record_request(latency_ms=25.0, success=True)
        snapshot = self.collector.get_snapshot()

        incidents = self.engine.evaluate_metrics(snapshot)
        self.assertTrue(any(inc.rule_id == "RULE-LAT-P99" for inc in incidents))
        self.assertEqual(len(self.engine.get_active_incidents()), 1)

    def test_alert_cooldown_suppression(self):
        for _ in range(19):
            self.collector.record_request(latency_ms=2.0, success=True)
        self.collector.record_request(latency_ms=25.0, success=True)
        snapshot = self.collector.get_snapshot()

        first_incidents = self.engine.evaluate_metrics(snapshot)
        self.assertEqual(len(first_incidents), 1)

        # Immediate second evaluation should be suppressed by cooldown
        second_incidents = self.engine.evaluate_metrics(snapshot)
        self.assertEqual(len(second_incidents), 0)

    def test_resolve_incident(self):
        for _ in range(19):
            self.collector.record_request(latency_ms=2.0, success=True)
        self.collector.record_request(latency_ms=25.0, success=True)
        snapshot = self.collector.get_snapshot()
        incidents = self.engine.evaluate_metrics(snapshot)

        inc_id = incidents[0].incident_id
        resolved = self.engine.resolve_incident(inc_id)
        self.assertTrue(resolved)
        self.assertEqual(len(self.engine.get_active_incidents()), 0)


class TestDecisionAuditLogger(unittest.TestCase):
    def setUp(self):
        self.audit = DecisionAuditLogger()

    def test_record_decision_hash_chain(self):
        rec1 = self.audit.record_decision(
            candidate_id="CAND-001",
            target_role="Staff Software Engineer",
            final_verdict="STRONG_HIRE",
            overall_score=92.5,
            round_scores={"tech": 94.0, "behavioral": 91.0},
        )
        self.assertEqual(rec1.previous_hash, DecisionAuditLogger.GENESIS_HASH)
        self.assertTrue(len(rec1.current_hash) == 64)

        rec2 = self.audit.record_decision(
            candidate_id="CAND-002",
            target_role="Frontend Lead",
            final_verdict="OFFER",
            overall_score=87.0,
            round_scores={"tech": 86.0, "behavioral": 88.0},
        )
        self.assertEqual(rec2.previous_hash, rec1.current_hash)

    def test_audit_trail_integrity_valid(self):
        self.audit.record_decision("CAND-001", "Backend Dev", "OFFER", 88.0, {"tech": 88.0})
        self.audit.record_decision("CAND-002", "Backend Dev", "HOLD", 72.0, {"tech": 72.0})

        valid, msg = self.audit.verify_audit_trail_integrity()
        self.assertTrue(valid)
        self.assertIn("verified", msg.lower())

    def test_audit_trail_tampering_detection(self):
        self.audit.record_decision("CAND-001", "Backend Dev", "OFFER", 88.0, {"tech": 88.0})
        self.audit.record_decision("CAND-002", "Backend Dev", "HOLD", 72.0, {"tech": 72.0})

        # Maliciously modify score of record 1
        self.audit.chain[0].overall_score = 99.9

        valid, msg = self.audit.verify_audit_trail_integrity()
        self.assertFalse(valid)
        self.assertIn("tampering detected", msg.lower())

    def test_export_audit_dossier(self):
        self.audit.record_decision(
            candidate_id="CAND-005",
            target_role="ML Engineer",
            final_verdict="STRONG_HIRE",
            overall_score=94.5,
            round_scores={"tech": 95.0, "behavioral": 94.0},
            adverse_impact_ratio=0.95,
        )
        dossier = self.audit.export_audit_dossier("CAND-005")
        self.assertIsNotNone(dossier)
        self.assertEqual(dossier["compliance"]["eeoc_four_fifths_status"], "COMPLIANT")
        self.assertTrue(dossier["cryptographic_verification"]["seal_verified"])


class TestMonitoringDashboardEngine(unittest.TestCase):
    def setUp(self):
        self.dashboard = MonitoringDashboardEngine()

    def test_record_outcomes_and_metrics(self):
        self.dashboard.record_interview_outcome("CAND-1", "Backend", "STRONG_HIRE", 35.0, passed=True)
        self.dashboard.record_interview_outcome("CAND-2", "Backend", "OFFER", 40.0, passed=True)
        self.dashboard.record_interview_outcome("CAND-3", "Backend", "REJECT", 25.0, passed=False)

        metrics = self.dashboard.compute_dashboard_metrics(active_interviews=8)
        self.assertEqual(metrics.total_candidates_processed, 3)
        self.assertEqual(metrics.interview_success_rate_pct, 66.67)
        self.assertEqual(metrics.active_interviews, 8)
        self.assertEqual(metrics.system_health, "OPTIMAL")

    def test_verdict_distribution(self):
        self.dashboard.record_interview_outcome("CAND-1", "Role", "STRONG_HIRE", 30.0, passed=True)
        self.dashboard.record_interview_outcome("CAND-2", "Role", "STRONG_HIRE", 30.0, passed=True)
        self.dashboard.record_interview_outcome("CAND-3", "Role", "HOLD", 30.0, passed=False)

        dist = self.dashboard.get_verdict_distribution()
        self.assertEqual(dist["STRONG_HIRE"], 2)
        self.assertEqual(dist["HOLD"], 1)

    def test_export_dashboard_specification(self):
        spec = self.dashboard.export_dashboard_specification()
        self.assertIn("dashboard", spec)
        self.assertEqual(len(spec["dashboard"]["panels"]), 6)


if __name__ == "__main__":
    unittest.main()

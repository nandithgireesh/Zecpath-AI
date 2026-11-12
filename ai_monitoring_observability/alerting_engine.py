"""
Day 61: Alerting Engine & Rules Registry
Automated SLA Breach, Accuracy Drift, and Latency Spike Alerting
Platform: Zecpath Automated Hiring Platform
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from ai_monitoring_observability.models import (
    AlertRule,
    AlertIncident,
    AlertSeverity,
    AlertStatus,
    MetricSnapshot,
)


class AlertingEngine:
    """
    Intelligent Observability Alerting Engine.
    Evaluates telemetry metric streams against enterprise alerting rules,
    dispatches alert incidents, and enforces cooldown suppression.
    """

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.incidents: List[AlertIncident] = []
        self._register_default_production_rules()

    def _register_default_production_rules(self):
        """Registers production SLA, performance, and drift alerting rules."""
        # 1. P99 Latency Breach (SLA > 15ms target, alarm at 20ms)
        self.register_rule(
            AlertRule(
                rule_id="RULE-LAT-P99",
                name="High P99 Latency Breach",
                metric_name="p99_latency_ms",
                comparison_operator=">",
                threshold_value=20.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_sec=60.0,
            )
        )
        # 2. Elevated Error Rate
        self.register_rule(
            AlertRule(
                rule_id="RULE-ERR-SURGE",
                name="Elevated API Error Rate Surge",
                metric_name="error_rate_pct",
                comparison_operator=">",
                threshold_value=1.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_sec=120.0,
            )
        )
        # 3. Model Accuracy Degradation (Drift)
        self.register_rule(
            AlertRule(
                rule_id="RULE-MODEL-DRIFT",
                name="AI Model Accuracy Drift Warning",
                metric_name="model_accuracy_pct",
                comparison_operator="<",
                threshold_value=93.0,
                severity=AlertSeverity.WARNING,
                cooldown_sec=180.0,
            )
        )
        # 4. Throughput Drop / Zero Traffic Warning
        self.register_rule(
            AlertRule(
                rule_id="RULE-P50-LATENCY",
                name="Median Latency Degradation",
                metric_name="p50_latency_ms",
                comparison_operator=">",
                threshold_value=10.0,
                severity=AlertSeverity.WARNING,
                cooldown_sec=60.0,
            )
        )

    def register_rule(self, rule: AlertRule):
        self.rules[rule.rule_id] = rule

    def evaluate_metrics(self, snapshot: MetricSnapshot) -> List[AlertIncident]:
        """
        Evaluates metrics snapshot against all registered rules.
        Returns newly triggered alert incidents.
        """
        now = time.time()
        new_incidents: List[AlertIncident] = []

        metrics_map = {
            "p50_latency_ms": snapshot.p50_latency_ms,
            "p90_latency_ms": snapshot.p90_latency_ms,
            "p95_latency_ms": snapshot.p95_latency_ms,
            "p99_latency_ms": snapshot.p99_latency_ms,
            "error_rate_pct": snapshot.error_rate_pct,
            "model_accuracy_pct": snapshot.model_accuracy_pct,
            "throughput_rps": snapshot.throughput_rps,
        }

        for rule in self.rules.values():
            if rule.metric_name not in metrics_map:
                continue

            metric_val = metrics_map[rule.metric_name]
            triggered = False

            if rule.comparison_operator == ">" and metric_val > rule.threshold_value:
                triggered = True
            elif rule.comparison_operator == ">=" and metric_val >= rule.threshold_value:
                triggered = True
            elif rule.comparison_operator == "<" and metric_val < rule.threshold_value:
                triggered = True
            elif rule.comparison_operator == "<=" and metric_val <= rule.threshold_value:
                triggered = True

            if triggered:
                # Check cooldown to prevent alert flood
                if (now - rule.last_triggered_at) >= rule.cooldown_sec:
                    incident = AlertIncident(
                        incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=f"{rule.name}: {rule.metric_name} is {metric_val} (Threshold {rule.comparison_operator} {rule.threshold_value})",
                        metric_value=metric_val,
                        threshold_value=rule.threshold_value,
                        triggered_at=now,
                        status=AlertStatus.ACTIVE,
                    )
                    rule.last_triggered_at = now
                    self.incidents.append(incident)
                    new_incidents.append(incident)

        return new_incidents

    def resolve_incident(self, incident_id: str) -> bool:
        for inc in self.incidents:
            if inc.incident_id == incident_id and inc.status == AlertStatus.ACTIVE:
                inc.status = AlertStatus.RESOLVED
                inc.resolved_at = time.time()
                return True
        return False

    def get_active_incidents(self) -> List[AlertIncident]:
        return [inc for inc in self.incidents if inc.status == AlertStatus.ACTIVE]

    def get_incident_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [
            {
                "incident_id": inc.incident_id,
                "rule_name": inc.rule_name,
                "severity": inc.severity.value,
                "message": inc.message,
                "metric_value": inc.metric_value,
                "threshold_value": inc.threshold_value,
                "triggered_at": inc.triggered_at,
                "status": inc.status.value,
                "resolved_at": inc.resolved_at,
            }
            for inc in self.incidents[-limit:]
        ]


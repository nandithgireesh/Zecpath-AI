"""
Day 49 Deliverable 3: Risk Flagging System Design
=================================================
Stateful escalation engine managing real-time progressive warning alerts,
session risk tagging, and hiring auditor recommendation generation.

Curriculum Reference: Day 49 - Deliverable 3: Risk Flagging System Design
Tasks:
- Define warning & flagging system
- Implement real-time progressive alerts (Tier 0 -> Tier 1 -> Tier 2 -> Tier 3)
- Assign interview risk tags (LOW_RISK_VERIFIED, MODERATE_FLAGGED_REVIEW, HIGH_RISK_TERMINATE_RECOMMENDED)
"""

from typing import List, Dict, Optional, Tuple

from integrity_ai.models import (
    FlagSeverity,
    AlertTierLevel,
    InterviewRiskTag,
    IntegrityFlag,
    RealTimeWarningAlert,
    MalpracticeSignalType,
)


class WarningEscalationStateMachine:
    """
    Stateful machine tracking progressive warning tiers across an interview session.
    Escalation path: TIER_0_NOMINAL -> TIER_1_ADVISORY -> TIER_2_FORMAL_WARNING -> TIER_3_AUDIT_ESCALATION
    """

    def __init__(self):
        self.current_tier = AlertTierLevel.TIER_0_NOMINAL
        self.total_warnings_count = 0
        self.total_critical_count = 0

    def evaluate_escalation(
        self,
        new_flags: List[IntegrityFlag],
        cumulative_risk: float,
    ) -> Optional[RealTimeWarningAlert]:
        """
        Evaluates turn flags and cumulative session risk, escalating warning tier if justified.
        """
        turn_warns = sum(1 for f in new_flags if f.severity == FlagSeverity.WARNING)
        turn_crits = sum(1 for f in new_flags if f.severity == FlagSeverity.CRITICAL)

        self.total_warnings_count += turn_warns
        self.total_critical_count += turn_crits

        previous_tier = self.current_tier

        # Escalation Logic
        if self.total_critical_count >= 2 or cumulative_risk >= 70.0:
            self.current_tier = AlertTierLevel.TIER_3_AUDIT_ESCALATION
        elif self.total_critical_count >= 1 or self.total_warnings_count >= 2 or cumulative_risk >= 45.0:
            self.current_tier = AlertTierLevel.TIER_2_FORMAL_WARNING
        elif self.total_warnings_count >= 1 or cumulative_risk >= 20.0:
            self.current_tier = AlertTierLevel.TIER_1_ADVISORY
        else:
            self.current_tier = AlertTierLevel.TIER_0_NOMINAL

        # Generate alert if elevated above Tier 0 and newly triggered or maintained
        if self.current_tier == AlertTierLevel.TIER_3_AUDIT_ESCALATION:
            return RealTimeWarningAlert(
                alert_tier=AlertTierLevel.TIER_3_AUDIT_ESCALATION,
                title="Integrity Alert: Session Audit Escalation",
                message="Critical unauthorized assistance patterns detected. Session has been flagged for human proctor audit review.",
                requires_acknowledgment=True,
                escalated_to_proctor=True,
            )
        elif self.current_tier == AlertTierLevel.TIER_2_FORMAL_WARNING:
            return RealTimeWarningAlert(
                alert_tier=AlertTierLevel.TIER_2_FORMAL_WARNING,
                title="Integrity Warning: Multiple Anomalies Detected",
                message="Repeated loss of focus or external audio detected. Please maintain full attention on the assessment interface.",
                requires_acknowledgment=True,
                escalated_to_proctor=False,
            )
        elif self.current_tier == AlertTierLevel.TIER_1_ADVISORY:
            return RealTimeWarningAlert(
                alert_tier=AlertTierLevel.TIER_1_ADVISORY,
                title="Advisory: Focus Reminder",
                message="Please keep the interview window active and focused during technical questions.",
                requires_acknowledgment=False,
                escalated_to_proctor=False,
            )

        return None


class InterviewRiskTagger:
    """
    Evaluates longitudinal interview session integrity telemetry and assigns
    definitive risk tags with explainable evidence summaries.
    """

    @classmethod
    def assign_session_risk_tag(
        self,
        overall_risk_score: float,
        critical_incidents_count: int,
        verified_patterns_count: int,
    ) -> Tuple[InterviewRiskTag, str]:
        """
        Calculates session risk tag and corresponding recruiter recommendation.
        """
        if critical_incidents_count >= 2 or verified_patterns_count >= 1 or overall_risk_score >= 60.0:
            tag = InterviewRiskTag.HIGH_RISK_TERMINATE_RECOMMENDED
            recommendation = (
                "TERMINATION / DISQUALIFICATION RECOMMENDED: Systematic external collusion or "
                "automated assistance patterns verified across multiple turns. Session compromised."
            )
        elif critical_incidents_count == 1 or overall_risk_score >= 25.0:
            tag = InterviewRiskTag.MODERATE_FLAGGED_REVIEW
            recommendation = (
                "MANUAL AUDIT REQUIRED: Isolated integrity anomalies detected. Recommend reviewing "
                "timestamped session video and code editor focus logs before making advancement decision."
            )
        else:
            tag = InterviewRiskTag.LOW_RISK_VERIFIED
            recommendation = (
                "CLEAN INTEGRITY VERIFIED: No anomalous external assistance or unauthorized tab activity observed. "
                "Candidate adhered fully to assessment integrity guidelines."
            )

        return tag, recommendation

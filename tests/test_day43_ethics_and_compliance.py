"""
Unit Test Suite for Day 43: Ethics & Compliance Review
======================================================
Tests all components across the three mandated deliverables:
- Deliverable 1: Ethics Consent Manager & Demographic Bias Scrubber
- Deliverable 2: Fairness Auditor & Explainability Engine
- Deliverable 3: Compliance Retention Policy Engine & Audit Readiness
"""

from datetime import datetime, timedelta, timezone
import unittest

from interview_ai.ethics_consent_manager import (
    EthicsConsentManager,
    ConsentStatus,
    DisclosureType,
)
from interview_ai.demographic_bias_scrubber import DemographicBiasScrubber
from interview_ai.fairness_auditor import FairnessAuditor
from interview_ai.explainability_engine import ExplainabilityEngine
from interview_ai.compliance_retention_policy import (
    ComplianceRetentionPolicyEngine,
    RetentionTier,
)


class TestDay43EthicsAndCompliance(unittest.TestCase):
    def setUp(self):
        self.consent_mgr = EthicsConsentManager()
        self.scrubber = DemographicBiasScrubber(candidate_name="Aditi Rao")
        self.auditor = FairnessAuditor()
        self.explainer = ExplainabilityEngine()
        self.retention_engine = ComplianceRetentionPolicyEngine()

    def test_01_mandatory_disclosures_coverage(self):
        disclosures = self.consent_mgr.get_mandatory_disclosures()
        self.assertEqual(len(disclosures), 4)
        types = {d.disclosure_type for d in disclosures}
        self.assertIn(DisclosureType.AI_EVALUATION, types)
        self.assertIn(DisclosureType.BIOMETRIC_AUDIO, types)
        self.assertIn(DisclosureType.DATA_RETENTION, types)
        self.assertIn(DisclosureType.HUMAN_OVERSIGHT, types)

    def test_02_explicit_consent_registration(self):
        all_types = [
            DisclosureType.AI_EVALUATION,
            DisclosureType.BIOMETRIC_AUDIO,
            DisclosureType.DATA_RETENTION,
            DisclosureType.HUMAN_OVERSIGHT,
        ]
        rec = self.consent_mgr.register_consent(
            candidate_id="CAND-001",
            job_requisition_id="REQ-TECH-901",
            acknowledged_disclosures=all_types,
            allow_audio_recording=True,
            allow_ai_scoring=True,
        )
        self.assertEqual(rec.status, ConsentStatus.EXPLICIT_OPT_IN)
        self.assertTrue(rec.candidate_pseudonym.startswith("PSEUDO-"))
        self.assertTrue(len(rec.receipt_hash) == 64)  # SHA-256
        self.assertTrue(self.consent_mgr.is_session_authorized("CAND-001"))

    def test_03_consent_revocation_and_human_routing(self):
        all_types = [
            DisclosureType.AI_EVALUATION,
            DisclosureType.BIOMETRIC_AUDIO,
            DisclosureType.DATA_RETENTION,
            DisclosureType.HUMAN_OVERSIGHT,
        ]
        self.consent_mgr.register_consent(
            candidate_id="CAND-002",
            job_requisition_id="REQ-TECH-901",
            acknowledged_disclosures=all_types,
        )
        revoked = self.consent_mgr.revoke_consent("CAND-002", reason="Candidate withdrew consent")
        self.assertIsNotNone(revoked)
        self.assertEqual(revoked.status, ConsentStatus.REVOKED)
        self.assertTrue(revoked.human_interviewer_requested)
        self.assertFalse(self.consent_mgr.is_session_authorized("CAND-002"))

    def test_04_demographic_bias_scrubber_names_and_pronouns(self):
        raw = "My name is Aditi Rao. As a woman in tech, she said we should rebuild the event bus."
        telemetry = self.scrubber.scrub(raw)
        self.assertNotIn("Aditi", telemetry.scrubbed_text)
        self.assertNotIn("she said", telemetry.scrubbed_text)
        self.assertIn("they said", telemetry.scrubbed_text)
        self.assertIn("as an engineer", telemetry.scrubbed_text)
        self.assertGreater(telemetry.total_signals_redacted, 0)

    def test_05_demographic_bias_scrubber_age_and_prestige(self):
        raw = "I am 52 years old and graduated back in 1994 from Stanford before building Kafka clusters."
        telemetry = self.scrubber.scrub(raw)
        self.assertNotIn("52 years old", telemetry.scrubbed_text)
        self.assertNotIn("1994", telemetry.scrubbed_text)
        self.assertNotIn("Stanford", telemetry.scrubbed_text)
        self.assertIn("[ACCREDITED_INSTITUTION]", telemetry.scrubbed_text)
        self.assertIn("Kafka", telemetry.scrubbed_text)  # Preserves technical nouns

    def test_06_fairness_auditor_four_fifths_rule_pass(self):
        # 100 benchmark candidates, 70 selected (70% rate)
        bench = [(80.0, True)] * 70 + [(50.0, False)] * 30
        # 100 protected candidates, 60 selected (60% rate) -> AIR = 60/70 = 0.857 (>= 0.80)
        prot = [(80.0, True)] * 60 + [(50.0, False)] * 40

        report = self.auditor.evaluate_cohort_disparate_impact(
            category="Gender",
            benchmark_name="Male Applicants",
            protected_name="Female Applicants",
            benchmark_candidates=bench,
            protected_candidates=prot,
        )
        self.assertTrue(report.four_fifths_rule_compliant)
        self.assertFalse(report.disparate_impact_detected)
        self.assertGreaterEqual(report.adverse_impact_ratio, 0.80)

    def test_07_fairness_auditor_disparate_impact_detection(self):
        # 100 benchmark candidates, 80 selected (80% rate)
        bench = [(85.0, True)] * 80 + [(50.0, False)] * 20
        # 100 protected candidates, 40 selected (40% rate) -> AIR = 40/80 = 0.50 (< 0.80)
        prot = [(85.0, True)] * 40 + [(50.0, False)] * 60

        report = self.auditor.evaluate_cohort_disparate_impact(
            category="Age",
            benchmark_name="Under 40",
            protected_name="40 and Older",
            benchmark_candidates=bench,
            protected_candidates=prot,
        )
        self.assertFalse(report.four_fifths_rule_compliant)
        self.assertTrue(report.disparate_impact_detected)
        self.assertLess(report.adverse_impact_ratio, 0.80)

    def test_08_explainability_dossier_generation(self):
        dossier = self.explainer.generate_dossier(
            candidate_id="SIM-HES-02",
            candidate_name="Siddharth Verma",
            target_role="Data Infrastructure Engineer",
            experience_years=4.0,
            semantic_score=72.0,
            communication_score=68.0,
            composure_score=74.9,
            consistency_score=74.0,
            latency_seconds=3.8,
            word_count=85,
            deductions_applied=2.0,
            flag_list=["HESITATION_DETECTED"],
            final_score=69.2,
            decision="LEAN_HIRE",
            leveling_tier="STANDARD_PLACEMENT",
        )
        self.assertEqual(len(dossier.factor_contributions), 4)
        self.assertEqual(len(dossier.penalties_applied), 1)
        self.assertGreater(len(dossier.deliberation_credits), 0)
        self.assertIn("Cognitive Deliberation Discount", dossier.deliberation_credits[0])
        self.assertTrue(len(dossier.counterfactual_path_to_higher_band) > 20)
        md = dossier.to_markdown()
        self.assertIn("Siddharth Verma", md)
        self.assertIn("Core Competency Contribution Breakdown", md)

    def test_09_compliance_retention_ttl_sweep(self):
        now = datetime.now(timezone.utc)
        # Register fresh asset (created today)
        self.retention_engine.register_asset(
            asset_id="ASSET-AUDIO-FRESH",
            candidate_id="CAND-010",
            tier=RetentionTier.RAW_AUDIO,
            creation_dt=now,
        )
        # Register old asset (created 20 days ago, exceeding 14d TTL)
        self.retention_engine.register_asset(
            asset_id="ASSET-AUDIO-EXPIRED",
            candidate_id="CAND-011",
            tier=RetentionTier.RAW_AUDIO,
            creation_dt=now - timedelta(days=20),
        )

        purged_certs = self.retention_engine.execute_ttl_sweep(current_dt=now)
        self.assertEqual(len(purged_certs), 1)
        self.assertEqual(purged_certs[0].asset_id, "ASSET-AUDIO-EXPIRED")
        self.assertTrue(self.retention_engine._assets["ASSET-AUDIO-EXPIRED"].is_purged)
        self.assertFalse(self.retention_engine._assets["ASSET-AUDIO-FRESH"].is_purged)

    def test_10_gdpr_right_to_erasure_and_deletion_certificate(self):
        now = datetime.now(timezone.utc)
        self.retention_engine.register_asset(
            asset_id="ASSET-TRANSCRIPT-001",
            candidate_id="CAND-GDPR-99",
            tier=RetentionTier.TRANSCRIPT,
            creation_dt=now,
        )
        self.retention_engine.register_asset(
            asset_id="ASSET-AUDIO-001",
            candidate_id="CAND-GDPR-99",
            tier=RetentionTier.RAW_AUDIO,
            creation_dt=now,
        )

        certs = self.retention_engine.handle_gdpr_right_to_erasure_request("CAND-GDPR-99")
        self.assertEqual(len(certs), 2)
        for c in certs:
            self.assertTrue(c.certificate_id.startswith("DEL-CERT-"))
            self.assertEqual(len(c.certificate_hash), 64)
            self.assertIn("GDPR Article 17", c.compliance_standard)


if __name__ == "__main__":
    unittest.main()

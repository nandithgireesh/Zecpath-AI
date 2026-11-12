"""
Unit Tests for Day 53: Hiring Intelligence Report Generator
===========================================================
Validates:
1. Ingestion of all 5 insight pillars (ATS, Screen, HR, Tech, Behavioral)
2. Highlights Extraction: Strengths, Weaknesses, Risk Indicators
3. Final Recommendation Resolution & Sub-Status Categorization
4. Recruiter TL;DR Generation
5. Multi-Format Export Capabilities (JSON, Markdown, Card, HTML)
6. Cryptographic SHA-256 Audit Seal Integrity
7. Sub-35ms Evaluation Execution Latency SLA
"""

import unittest
import time
import json
from hiring_report_generator import (
    HighlightType,
    CompetencyPillar,
    ImpactLevel,
    ReportExportFormat,
    ATSSummarySection,
    ScreeningResultsSection,
    HRInsightsSection,
    TechnicalPerformanceSection,
    BehavioralAndRiskSection,
    CompetencyHighlight,
    FinalRecommendationSummary,
    CandidateAIProfileReport,
    HiringIntelligenceReportGenerator,
    ReportExportFormatter,
)


class TestDay53HiringReportGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = HiringIntelligenceReportGenerator()
        self.formatter = ReportExportFormatter()

    def test_01_end_to_end_candidate_report_generation(self):
        """Validates complete generation across all 5 insight pillars for a top candidate."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-PRIYA-01",
            candidate_name="Priya Sharma",
            target_role="Principal Distributed Systems Architect",
            experience_tier="PRINCIPAL_ARCHITECT",
            ats_data={
                "ats_score": 92.5,
                "keyword_match_rate": 91.0,
                "experience_years": 8.5,
                "education_tier": "Master of Technology in Computer Science",
                "matched_skills": ["Distributed Consensus", "Raft", "Kubernetes", "Kafka", "Rust"],
                "missing_skills": [],
                "summary_notes": "Flawless resume profile with premier cloud infrastructure credentials.",
            },
            screening_data={
                "screening_score": 88.0,
                "communication_clarity": "EXEMPLARY",
                "qualification_fit": "STRONG_ALIGNMENT",
                "availability_timeline": "Immediate (2 Weeks)",
                "screening_notes": "Articulated architectural philosophy clearly and confirmed prerequisites.",
            },
            hr_data={
                "hr_score": 89.5,
                "star_method_rating": 90.0,
                "leadership_teamwork_index": 92.0,
                "cultural_values_alignment": "ROLE_MODEL",
                "motivation_and_adaptability": "EXCEPTIONAL",
                "hr_interview_notes": "Exemplary behavioral ownership; resolved major cross-team outage.",
            },
            technical_data={
                "technical_interview_score": 93.0,
                "machine_test_sandbox_score": 100.0,
                "architecture_design_score": 95.0,
                "test_suite_pass_rate": 100.0,
                "code_quality_and_cleanliness": "PRODUCTION_GRADE",
                "technical_notes": "Implemented robust concurrent distributed lock algorithm with zero faults.",
            },
            behavioral_data={
                "stress_index": 12.0,
                "hesitation_pause_count": 0,
                "speech_fluency_rating": "IMPECCABLE",
                "integrity_penalty_points": 0.0,
                "malpractice_breaches_detected": 0,
                "overall_risk_level": "LOW",
            },
        )

        self.assertIsNotNone(report)
        self.assertEqual(report.candidate_name, "Priya Sharma")
        self.assertEqual(report.final_recommendation.decision_category, "SELECTED")
        self.assertEqual(report.final_recommendation.decision_substatus, "OFFER_IMMEDIATE_FAST_TRACK")
        self.assertGreaterEqual(report.final_recommendation.hiring_fit_score, 90.0)
        self.assertGreaterEqual(len(report.strengths), 2)
        self.assertEqual(len(report.risk_indicators), 0)
        self.assertTrue(len(report.audit_hash) == 64)

    def test_02_strengths_extraction(self):
        """Validates that high-performing competencies are extracted into Strengths."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-02",
            candidate_name="Strong Candidate",
            target_role="Lead Architect",
            experience_tier="SENIOR",
            ats_data={"ats_score": 95.0, "keyword_match_rate": 96.0},
            screening_data={"screening_score": 80.0},
            hr_data={"hr_score": 88.0, "star_method_rating": 89.0},
            technical_data={"machine_test_sandbox_score": 98.0, "architecture_design_score": 92.0},
            behavioral_data={"stress_index": 15.0, "overall_risk_level": "LOW"},
        )

        strength_titles = [s.title for s in report.strengths]
        self.assertTrue(any("Resume" in t for t in strength_titles))
        self.assertTrue(any("Sandbox" in t for t in strength_titles))
        self.assertTrue(any("STAR" in t for t in strength_titles))

    def test_03_weaknesses_extraction(self):
        """Validates that missing skills, borderline scores, and pauses trigger Weaknesses."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-03",
            candidate_name="Weak Candidate",
            target_role="Software Engineer",
            experience_tier="MID_LEVEL",
            ats_data={"ats_score": 68.0, "missing_skills": ["Kubernetes", "GraphQL"]},
            screening_data={"screening_score": 70.0},
            hr_data={"hr_score": 65.0, "star_method_rating": 60.0},
            technical_data={"machine_test_sandbox_score": 62.0, "test_suite_pass_rate": 60.0},
            behavioral_data={"hesitation_pause_count": 4, "stress_index": 45.0},
        )

        self.assertGreaterEqual(len(report.weaknesses), 2)
        weakness_pillars = [w.pillar for w in report.weaknesses]
        self.assertIn(CompetencyPillar.ATS_RESUME, weakness_pillars)
        self.assertIn(CompetencyPillar.HR_INTERVIEW, weakness_pillars)

    def test_04_critical_integrity_risk_indicator(self):
        """Validates that malpractice penalties and breaches trigger critical risk indicators and rejection."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-VIKRAM-04",
            candidate_name="Vikram Rao",
            target_role="Senior Backend Developer",
            experience_tier="SENIOR",
            ats_data={"ats_score": 72.0},
            screening_data={"screening_score": 65.0},
            hr_data={"hr_score": 60.0},
            technical_data={"technical_interview_score": 58.0, "machine_test_sandbox_score": 60.0},
            behavioral_data={
                "integrity_penalty_points": 30.0,
                "malpractice_breaches_detected": 2,
                "overall_risk_level": "CRITICAL",
            },
        )

        self.assertEqual(report.final_recommendation.decision_category, "REJECTED")
        self.assertEqual(report.final_recommendation.decision_substatus, "REJECT_INTEGRITY_MALPRACTICE")
        risk_titles = [r.title for r in report.risk_indicators]
        self.assertTrue(any("Malpractice" in t for t in risk_titles))
        self.assertEqual(report.behavioral_and_risk.overall_risk_level, "CRITICAL")

    def test_05_technical_competency_floor_breach(self):
        """Validates that failing the 55.0 pt technical floor forces rejection and technical risk flag."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-05",
            candidate_name="Low Tech Candidate",
            target_role="Backend Developer",
            experience_tier="JUNIOR",
            ats_data={"ats_score": 85.0},
            screening_data={"screening_score": 80.0},
            hr_data={"hr_score": 82.0},
            technical_data={"technical_interview_score": 48.0, "machine_test_sandbox_score": 40.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )

        self.assertEqual(report.final_recommendation.decision_category, "REJECTED")
        self.assertEqual(report.final_recommendation.decision_substatus, "REJECT_CRITICAL_GATE_BREACH")
        risk_pillars = [r.pillar for r in report.risk_indicators]
        self.assertIn(CompetencyPillar.TECHNICAL_EVALUATION, risk_pillars)

    def test_06_cross_round_variance_volatility_hold_review(self):
        """Validates that high verbal score with weak coding triggers Bar Raiser hold review."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-ANANYA-06",
            candidate_name="Ananya Sen",
            target_role="Solutions Architecture",
            experience_tier="SENIOR_LEAD",
            ats_data={"ats_score": 96.0},
            screening_data={"screening_score": 94.0},
            hr_data={"hr_score": 92.0},
            technical_data={"technical_interview_score": 60.0, "machine_test_sandbox_score": 58.0},
            behavioral_data={"cross_round_std_dev": 18.5, "overall_risk_level": "MODERATE"},
        )

        self.assertEqual(report.final_recommendation.decision_category, "HOLD_REVIEW")
        self.assertEqual(report.final_recommendation.decision_substatus, "HOLD_BAR_RAISER_EVALUATION")
        risk_titles = [r.title for r in report.risk_indicators]
        self.assertTrue(any("Volatility" in t for t in risk_titles))

    def test_07_recruiter_tldr_synthesis(self):
        """Validates that recruiter TL;DR contains candidate name, decision, fit score, and next action."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-07",
            candidate_name="Rohan Mehta",
            target_role="Software Engineer Core",
            experience_tier="MID_LEVEL",
            ats_data={"ats_score": 78.0},
            screening_data={"screening_score": 74.0},
            hr_data={"hr_score": 72.0},
            technical_data={"technical_interview_score": 76.0, "machine_test_sandbox_score": 75.0},
            behavioral_data={"overall_risk_level": "MODERATE"},
        )

        tldr = report.recruiter_tldr
        self.assertIn("Rohan Mehta", tldr)
        self.assertIn("HOLD_REVIEW", tldr)
        self.assertIn("Next Action", tldr)

    def test_08_json_export_serialization(self):
        """Validates that ReportExportFormatter.to_json produces valid, parsable JSON."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-JSON-08",
            candidate_name="JSON Benchmark",
            target_role="Data Engineer",
            experience_tier="SENIOR",
            ats_data={"ats_score": 82.0},
            screening_data={"screening_score": 80.0},
            hr_data={"hr_score": 80.0},
            technical_data={"technical_interview_score": 84.0, "machine_test_sandbox_score": 86.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )

        json_str = self.formatter.to_json(report)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["candidate_id"], "CAND-JSON-08")
        self.assertIn("ats_summary", parsed)
        self.assertIn("final_recommendation", parsed)
        self.assertIn("strengths", parsed)

    def test_09_markdown_export_formatting(self):
        """Validates that ReportExportFormatter.to_markdown produces formatted markdown tables."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-MD-09",
            candidate_name="Markdown Benchmark",
            target_role="Cloud Architect",
            experience_tier="PRINCIPAL",
            ats_data={"ats_score": 90.0},
            screening_data={"screening_score": 88.0},
            hr_data={"hr_score": 85.0},
            technical_data={"technical_interview_score": 90.0, "machine_test_sandbox_score": 92.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )

        md_str = self.formatter.to_markdown(report)
        self.assertIn("# Candidate AI Profile Report: Markdown Benchmark", md_str)
        self.assertIn("## ⚡ Recruiter Executive Summary (TL;DR)", md_str)
        self.assertIn("| Evaluation Pillar | Stage Score |", md_str)
        self.assertIn("SHA-256", md_str)

    def test_10_executive_summary_card_format(self):
        """Validates that ReportExportFormatter.to_executive_summary_card renders compact card layout."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-CARD-10",
            candidate_name="Card Benchmark",
            target_role="Platform Engineer",
            experience_tier="SENIOR",
            ats_data={"ats_score": 88.0},
            screening_data={"screening_score": 82.0},
            hr_data={"hr_score": 84.0},
            technical_data={"technical_interview_score": 86.0, "machine_test_sandbox_score": 88.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )

        card_str = self.formatter.to_executive_summary_card(report)
        self.assertIn("ZECPATH-AI RECRUITER EXECUTIVE SUMMARY CARD", card_str)
        self.assertIn("CANDIDATE : Card Benchmark", card_str)
        self.assertIn("FIT SCORE :", card_str)

    def test_11_html_export_formatting(self):
        """Validates that ReportExportFormatter.to_html produces complete HTML document."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-HTML-11",
            candidate_name="HTML Benchmark",
            target_role="Frontend Lead",
            experience_tier="STAFF",
            ats_data={"ats_score": 86.0},
            screening_data={"screening_score": 84.0},
            hr_data={"hr_score": 88.0},
            technical_data={"technical_interview_score": 85.0, "machine_test_sandbox_score": 89.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )

        html_str = self.formatter.to_html(report)
        self.assertTrue(html_str.startswith("<!DOCTYPE html>"))
        self.assertIn("<title>Candidate AI Profile Report: HTML Benchmark</title>", html_str)
        self.assertIn("class=\"tldr-box\"", html_str)
        self.assertIn(report.audit_hash, html_str)

    def test_12_sha256_audit_seal_tamper_detection(self):
        """Validates that modifying report fields invalidates the cryptographic SHA-256 seal."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-SEAL-12",
            candidate_name="Tamper Test",
            target_role="Security Engineer",
            experience_tier="SENIOR",
            ats_data={"ats_score": 80.0},
            screening_data={"screening_score": 80.0},
            hr_data={"hr_score": 80.0},
            technical_data={"technical_interview_score": 80.0, "machine_test_sandbox_score": 80.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )

        original_seal = report.audit_hash
        # Verify valid signature initially
        self.assertEqual(report.compute_sha256_audit_seal(), original_seal)

        # Alter final hiring fit score
        report.final_recommendation.hiring_fit_score = 99.9
        tampered_seal = report.compute_sha256_audit_seal()
        self.assertNotEqual(original_seal, tampered_seal)

    def test_13_sub_35ms_sla_performance(self):
        """Validates that end-to-end report generation satisfies sub-35ms SLA."""
        start = time.perf_counter()
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-SLA-13",
            candidate_name="Latency Benchmark",
            target_role="High-Speed Execution Lead",
            experience_tier="SENIOR",
            ats_data={"ats_score": 85.0},
            screening_data={"screening_score": 85.0},
            hr_data={"hr_score": 85.0},
            technical_data={"technical_interview_score": 85.0, "machine_test_sandbox_score": 85.0},
            behavioral_data={"overall_risk_level": "LOW"},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.assertLessEqual(elapsed_ms, 35.0)
        self.assertLessEqual(report.generation_latency_ms, 35.0)

    def test_14_decision_override_integration(self):
        """Validates that Day 52 final recommendation can be injected directly via override."""
        override = {
            "decision_category": "SELECTED",
            "decision_substatus": "OFFER_STANDARD",
            "hiring_fit_score": 86.5,
            "confidence_score": 92.0,
            "confidence_band": "VERY_HIGH",
            "executive_rationale": "Direct injection from Day 52 decision AI engine.",
            "recommended_action": "Extend formal offer with standard leveling.",
        }

        report = self.generator.generate_candidate_report(
            candidate_id="CAND-OVERRIDE-14",
            candidate_name="Override Candidate",
            target_role="DevOps Lead",
            experience_tier="LEAD",
            ats_data={"ats_score": 80.0},
            screening_data={"screening_score": 80.0},
            hr_data={"hr_score": 80.0},
            technical_data={"technical_interview_score": 80.0, "machine_test_sandbox_score": 80.0},
            behavioral_data={"overall_risk_level": "LOW"},
            decision_override=override,
        )

        self.assertEqual(report.final_recommendation.decision_category, "SELECTED")
        self.assertEqual(report.final_recommendation.hiring_fit_score, 86.5)
        self.assertEqual(report.final_recommendation.confidence_score, 92.0)

    def test_15_empty_and_default_fields_resilience(self):
        """Validates that generator gracefully handles minimal/empty dictionaries."""
        report = self.generator.generate_candidate_report(
            candidate_id="CAND-MINIMAL-15",
            candidate_name="Minimal Candidate",
            target_role="General Engineer",
            experience_tier="ASSOCIATE",
            ats_data={},
            screening_data={},
            hr_data={},
            technical_data={},
            behavioral_data={},
        )
        self.assertIsNotNone(report)
        self.assertIsNotNone(report.audit_hash)
        self.assertIn("Minimal Candidate", report.recruiter_tldr)


if __name__ == "__main__":
    unittest.main()


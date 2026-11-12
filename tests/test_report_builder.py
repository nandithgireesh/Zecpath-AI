"""
Day 28 Unit Tests: AI Screening Report Builder & Models
======================================================
Tests salary analysis, availability auditing, skill confirmation,
strengths extraction, risk evaluation, missing data detection,
hiring recommendations, and multi-format exports (Markdown, HTML, JSON).
"""

import unittest
from screening_ai.report_models import (
    HiringRecommendation,
    RiskSeverity,
    RiskCategory,
    DataGapImpact,
    ScreeningReport,
)
from screening_ai.report_builder import ScreeningReportBuilder
from screening_ai.sample_reports import generate_sample_reports


class TestScreeningReportBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ScreeningReportBuilder(default_budget_max_lpa=25.0, default_max_notice_days=60)

    # -------------------------------------------------------------------------
    # 1. Salary Analysis Tests
    # -------------------------------------------------------------------------

    def test_salary_analysis_within_budget(self):
        hl = self.builder.analyze_salary(
            current_ctc_lpa=18.0,
            expected_ctc_lpa=22.0,
            budget_max_lpa=25.0,
            is_negotiable=True,
        )
        self.assertTrue(hl.is_within_budget)
        self.assertEqual(hl.status, "WITHIN_BUDGET")
        self.assertEqual(hl.expected_ctc_lpa, 22.0)
        self.assertLess(hl.budget_variance_pct, 0.0)  # Below ceiling
        self.assertIn("within the allocated budget", hl.summary)

    def test_salary_analysis_exceeds_budget(self):
        hl = self.builder.analyze_salary(
            current_ctc_lpa=24.0,
            expected_ctc_lpa=30.0,
            budget_max_lpa=25.0,
            is_negotiable=False,
        )
        self.assertFalse(hl.is_within_budget)
        self.assertEqual(hl.status, "EXCEEDS_BUDGET")
        self.assertEqual(hl.budget_variance_pct, 20.0)
        self.assertIn("exceeds budget maximum", hl.summary)
        self.assertIn("non-negotiable", hl.summary)

    def test_salary_analysis_undisclosed(self):
        hl = self.builder.analyze_salary(
            current_ctc_lpa=15.0,
            expected_ctc_lpa=None,
            budget_max_lpa=25.0,
        )
        self.assertTrue(hl.is_within_budget)
        self.assertEqual(hl.status, "UNDISCLOSED")
        self.assertIsNone(hl.budget_variance_pct)
        self.assertIn("not disclosed", hl.summary)

    # -------------------------------------------------------------------------
    # 2. Availability Analysis Tests
    # -------------------------------------------------------------------------

    def test_availability_immediate_joiner(self):
        hl = self.builder.analyze_availability(
            notice_period_days=0,
            is_immediate_joiner=True,
            max_acceptable_notice_days=60,
        )
        self.assertTrue(hl.is_immediate_joiner)
        self.assertTrue(hl.is_acceptable)
        self.assertEqual(hl.status, "IMMEDIATE")
        self.assertIn("immediately", hl.summary)

    def test_availability_standard_notice(self):
        hl = self.builder.analyze_availability(
            notice_period_days=30,
            is_immediate_joiner=False,
            max_acceptable_notice_days=60,
        )
        self.assertFalse(hl.is_immediate_joiner)
        self.assertTrue(hl.is_acceptable)
        self.assertEqual(hl.status, "STANDARD")
        self.assertIn("30-day notice period", hl.summary)

    def test_availability_extended_notice(self):
        hl = self.builder.analyze_availability(
            notice_period_days=90,
            is_immediate_joiner=False,
            max_acceptable_notice_days=60,
            buyout_possible=True,
        )
        self.assertTrue(hl.is_acceptable)  # Acceptable because buyout is possible
        self.assertEqual(hl.status, "EXTENDED")
        self.assertIn("exceeds role requirement", hl.summary)
        self.assertIn("buyout may be negotiable", hl.summary)

    def test_availability_unknown(self):
        hl = self.builder.analyze_availability(notice_period_days=None)
        self.assertFalse(hl.is_acceptable)
        self.assertEqual(hl.status, "UNKNOWN")

    # -------------------------------------------------------------------------
    # 3. Skill Confirmation Tests
    # -------------------------------------------------------------------------

    def test_skill_confirmation_fully_confirmed(self):
        candidate_skills = ["Python", "Docker", "Kubernetes", "AWS", "Kafka"]
        mandatory = ["Python", "Docker", "Kubernetes"]
        bonus = ["Kafka", "Terraform"]

        hl = self.builder.analyze_skills(candidate_skills, mandatory, bonus)
        self.assertEqual(hl.status, "FULLY_CONFIRMED")
        self.assertEqual(hl.skill_match_percentage, 100.0)
        self.assertEqual(len(hl.confirmed_skills), 3)
        self.assertEqual(len(hl.missing_mandatory_skills), 0)
        self.assertIn("Kafka", hl.bonus_skills_found)

    def test_skill_confirmation_partial_and_missing(self):
        candidate_skills = ["Python", "SQL"]
        mandatory = ["Python", "Kubernetes", "AWS", "Kafka"]
        bonus = ["Docker"]

        hl = self.builder.analyze_skills(candidate_skills, mandatory, bonus)
        self.assertEqual(hl.status, "CRITICAL_GAPS")
        self.assertEqual(hl.skill_match_percentage, 25.0)
        self.assertIn("Kubernetes", hl.missing_mandatory_skills)
        self.assertIn("AWS", hl.missing_mandatory_skills)
        self.assertIn("Kafka", hl.missing_mandatory_skills)

    # -------------------------------------------------------------------------
    # 4. End-to-End Report Generation Tests
    # -------------------------------------------------------------------------

    def test_build_report_strong_hire(self):
        q_evals = [
            {
                "question_id": "Q1",
                "question_category": "Technical",
                "question_text": "Explain microservices architecture.",
                "raw_answer": "We implemented event-driven microservices with Kafka and Kubernetes.",
                "weighted_question_score": 95.0,
                "grade": "EXCELLENT",
                "explanation": "Outstanding technical depth.",
                "relevance_score": 95.0,
            }
        ]

        report = self.builder.build_report(
            candidate_id="CAND-TEST-01",
            candidate_name="Alex Mercer",
            job_id="JOB-TEST-01",
            role_name="Senior Software Architect",
            candidate_data={
                "current_ctc_lpa": 22.0,
                "expected_ctc_lpa": 25.0,
                "ctc_negotiable": True,
                "notice_period_days": 30,
                "is_immediate_joiner": False,
                "skills_confirmed": ["Python", "Kubernetes", "AWS", "Kafka"],
            },
            question_evaluations=q_evals,
            role_mandatory_skills=["Python", "Kubernetes", "AWS"],
            budget_max_lpa=28.0,
            max_acceptable_notice_days=60,
            behavioral_summary={"communication_score": 90.0, "confidence_score": 92.0, "is_defensive": False},
        )

        self.assertEqual(report.recommendation, HiringRecommendation.STRONG_HIRE)
        self.assertGreaterEqual(report.scores.overall_score, 85.0)
        self.assertEqual(report.salary_highlight.status, "WITHIN_BUDGET")
        self.assertEqual(report.availability_highlight.status, "STANDARD")
        self.assertGreater(len(report.strengths), 0)
        self.assertGreater(len(report.key_answers), 0)

    def test_build_report_no_hire_on_defensive(self):
        q_evals = [
            {
                "question_id": "Q1",
                "question_category": "Technical",
                "question_text": "Describe your coding practices.",
                "raw_answer": "That's none of your business, look at my resume.",
                "weighted_question_score": 35.0,
                "grade": "UNSATISFACTORY",
                "explanation": "Defensive answer.",
                "relevance_score": 30.0,
            }
        ]

        report = self.builder.build_report(
            candidate_id="CAND-TEST-02",
            candidate_name="John Doe",
            job_id="JOB-TEST-02",
            role_name="Backend Developer",
            candidate_data={
                "expected_ctc_lpa": 20.0,
                "notice_period_days": 30,
                "skills_confirmed": ["Python"],
            },
            question_evaluations=q_evals,
            role_mandatory_skills=["Python", "PostgreSQL", "Docker"],
            budget_max_lpa=18.0,
            behavioral_summary={"communication_score": 40.0, "confidence_score": 50.0, "is_defensive": True},
        )

        self.assertEqual(report.recommendation, HiringRecommendation.NO_HIRE)
        critical_risks = [r for r in report.risks if r.severity == RiskSeverity.CRITICAL]
        self.assertGreater(len(critical_risks), 0)

    # -------------------------------------------------------------------------
    # 5. Multi-Format Export Tests
    # -------------------------------------------------------------------------

    def test_export_markdown(self):
        samples = generate_sample_reports()
        r1 = samples["sample_1_strong_hire"]
        md = self.builder.export_markdown(r1)

        self.assertIn("# AI Screening Report: Aarav Sharma", md)
        self.assertIn("STRONG HIRE", md)
        self.assertIn("## 1. Executive Summary", md)
        self.assertIn("## 2. Scorecard & Performance Metrics", md)
        self.assertIn("## 3. Core Operational Constraints", md)
        self.assertIn("## 4. Candidate Strengths & Advantages", md)
        self.assertIn("## 7. Key Answer Summaries", md)

    def test_export_html(self):
        samples = generate_sample_reports()
        r1 = samples["sample_1_strong_hire"]
        html = self.builder.export_html(r1)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Aarav Sharma", html)
        self.assertIn("Strong Hire", html)
        self.assertIn("Screening Scorecard", html)
        self.assertIn("Operational Constraints", html)

    def test_export_json(self):
        samples = generate_sample_reports()
        r1 = samples["sample_1_strong_hire"]
        data = self.builder.export_json(r1)

        self.assertIsInstance(data, dict)
        self.assertEqual(data["candidate_id"], "CAND-901")
        self.assertEqual(data["candidate_name"], "Aarav Sharma")
        self.assertEqual(data["recommendation"], "STRONG_HIRE")
        self.assertIn("scores", data)
        self.assertIn("salary_highlight", data)
        self.assertIn("availability_highlight", data)
        self.assertIn("skills_highlight", data)

    # -------------------------------------------------------------------------
    # 6. Sample Reports Generator Test
    # -------------------------------------------------------------------------

    def test_sample_reports_diversity(self):
        samples = generate_sample_reports()
        self.assertEqual(len(samples), 4)
        self.assertIn("sample_1_strong_hire", samples)
        self.assertIn("sample_2_hire", samples)
        self.assertIn("sample_3_proceed_with_caution", samples)
        self.assertIn("sample_4_no_hire", samples)

        # Verify distinct outcomes
        r_caution = samples["sample_3_proceed_with_caution"]
        self.assertEqual(r_caution.recommendation, HiringRecommendation.PROCEED_WITH_CAUTION)

        r_nohire = samples["sample_4_no_hire"]
        self.assertEqual(r_nohire.recommendation, HiringRecommendation.NO_HIRE)


if __name__ == "__main__":
    unittest.main()

"""
Day 28 Integration Tests: AI Screening Report REST API
======================================================
Tests the FastAPI endpoints:
- POST /screening/report/generate
- POST /screening/report/export
- GET  /screening/report/samples
- GET  /screening/report/schema
"""

import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app
from screening_ai.sample_reports import generate_sample_reports
from screening_ai.report_builder import ScreeningReportBuilder


class TestScreeningReportAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.builder = ScreeningReportBuilder()
        cls.samples = generate_sample_reports()

    def test_generate_report_endpoint(self):
        payload = {
            "candidate_id": "CAND-API-01",
            "candidate_name": "Siddharth Rao",
            "job_id": "JOB-ENG-01",
            "role_name": "Principal Engineer",
            "candidate_data": {
                "current_ctc_lpa": 28.0,
                "expected_ctc_lpa": 32.0,
                "ctc_negotiable": True,
                "notice_period_days": 30,
                "is_immediate_joiner": False,
                "skills_confirmed": ["Python", "Kubernetes", "AWS", "Kafka", "PostgreSQL"],
            },
            "question_evaluations": [
                {
                    "question_id": "Q1",
                    "question_category": "Technical",
                    "question_text": "Describe your architectural approach to multi-region disaster recovery.",
                    "raw_answer": "We implemented active-active cross-region Aurora PostgreSQL with Route 53 DNS failover.",
                    "weighted_question_score": 92.0,
                    "grade": "EXCELLENT",
                    "explanation": "Authoritative multi-region disaster recovery strategy.",
                    "relevance_score": 95.0,
                }
            ],
            "role_mandatory_skills": ["Python", "Kubernetes", "AWS"],
            "role_bonus_skills": ["Kafka"],
            "budget_max_lpa": 35.0,
            "max_acceptable_notice_days": 60,
            "behavioral_summary": {
                "communication_score": 88.0,
                "confidence_score": 90.0,
                "is_defensive": False,
            },
        }

        response = self.client.post("/screening/report/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("report_id", data)
        self.assertEqual(data["candidate_name"], "Siddharth Rao")
        self.assertEqual(data["role_name"], "Principal Engineer")
        self.assertEqual(data["recommendation"], "STRONG_HIRE")
        self.assertGreaterEqual(data["overall_score"], 85.0)
        self.assertIn("report", data)
        self.assertIn("markdown_export", data)
        self.assertIn("html_export", data)

    def test_export_report_markdown_endpoint(self):
        r1 = self.samples["sample_1_strong_hire"]
        payload = {
            "report": self.builder.export_json(r1),
            "export_format": "MARKDOWN",
        }

        response = self.client.post("/screening/report/export", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["export_format"], "MARKDOWN")
        self.assertIn("# AI Screening Report: Aarav Sharma", data["content"])
        self.assertIn("STRONG HIRE", data["content"])

    def test_export_report_html_endpoint(self):
        r1 = self.samples["sample_1_strong_hire"]
        payload = {
            "report": self.builder.export_json(r1),
            "export_format": "HTML",
        }

        response = self.client.post("/screening/report/export", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["export_format"], "HTML")
        self.assertIn("<!DOCTYPE html>", data["content"])
        self.assertIn("Aarav Sharma", data["content"])

    def test_export_report_json_endpoint(self):
        r1 = self.samples["sample_1_strong_hire"]
        payload = {
            "report": self.builder.export_json(r1),
            "export_format": "JSON",
        }

        response = self.client.post("/screening/report/export", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["export_format"], "JSON")
        self.assertIn("CAND-901", data["content"])

    def test_sample_reports_endpoint(self):
        response = self.client.get("/screening/report/samples")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["total_samples"], 4)
        self.assertIn("sample_1_strong_hire", data["samples"])
        self.assertIn("sample_2_hire", data["samples"])
        self.assertIn("sample_3_proceed_with_caution", data["samples"])
        self.assertIn("sample_4_no_hire", data["samples"])

    def test_report_schema_endpoint(self):
        response = self.client.get("/screening/report/schema")
        self.assertEqual(response.status_code, 200)
        schema = response.json()

        self.assertEqual(schema["title"], "AIScreeningReportSchema")
        self.assertIn("properties", schema)
        self.assertIn("recommendation", schema["properties"])
        self.assertIn("salary_highlight", schema["properties"])
        self.assertIn("availability_highlight", schema["properties"])


if __name__ == "__main__":
    unittest.main()

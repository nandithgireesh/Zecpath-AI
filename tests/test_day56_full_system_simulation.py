"""
Unit Tests for Day 56: Full System Simulation
=============================================
Platform: Zecpath Enterprise Talent Assessment Platform
Tests 6-stage journey, comparative AI vs. human judgment,
inconsistency detection, and system performance profiling.
"""

import unittest
from full_system_simulation import (
    JourneyOrchestrator, ComparativeJudgmentEngine,
    InconsistencyDetector, SystemPerformanceAnalyzer,
    DecisionVerdict, HiringStage, StageStatus,
    ResumeArtifact, ATSScoreResult, ScreeningResult,
    HRInterviewResult, TechnicalInterviewResult, FinalDecisionResult,
    InconsistencyType
)


class TestDay56FullSystemSimulation(unittest.TestCase):

    def setUp(self):
        self.orchestrator = JourneyOrchestrator(ats_cutoff=60.0, screening_cutoff=60.0)
        self.comparator = ComparativeJudgmentEngine()
        self.detector = InconsistencyDetector()
        self.analyzer = SystemPerformanceAnalyzer()

    def test_stage_1_resume_upload(self):
        resume, lat = self.orchestrator.run_stage_1_resume_upload(
            candidate_id="CAN-TEST-001",
            full_name="Jane Doe",
            target_role="Senior Backend Engineer",
            raw_text="Experience: 5 years in Python and FastAPI. Education: B.S. CS. Skills: Python, Docker.",
            experience_years=5.0,
            education_level="B.S.",
            institution="MIT",
            primary_skills=["Python", "FastAPI", "Docker"]
        )
        self.assertEqual(resume.candidate_id, "CAN-TEST-001")
        self.assertGreater(lat, 0.0)
        self.assertIn("Python", resume.primary_skills)

    def test_stage_2_ats_scoring_passed(self):
        resume, _ = self.orchestrator.run_stage_1_resume_upload(
            candidate_id="CAN-TEST-002",
            full_name="Alex Smith",
            target_role="Cloud Architect",
            raw_text="Experience: 6 years AWS, Kubernetes, Terraform. Education: M.S. Skills: AWS, Terraform.",
            experience_years=6.0,
            education_level="M.S.",
            institution="Stanford",
            primary_skills=["AWS", "Terraform", "Kubernetes"]
        )
        ats, lat = self.orchestrator.run_stage_2_ats_scoring(
            resume=resume,
            required_role_keywords=["AWS", "Terraform", "Kubernetes"],
            min_experience_years=3.0
        )
        self.assertTrue(ats.passed)
        self.assertEqual(ats.status, StageStatus.PASSED)
        self.assertGreaterEqual(ats.composite_ats_score, 70.0)

    def test_stage_2_ats_scoring_failed(self):
        resume, _ = self.orchestrator.run_stage_1_resume_upload(
            candidate_id="CAN-TEST-003",
            full_name="Bob Low",
            target_role="Cloud Architect",
            raw_text="Experience: 1 year support. Skills: Excel.",
            experience_years=1.0,
            education_level="High School",
            institution="None",
            primary_skills=["Excel"]
        )
        ats, _ = self.orchestrator.run_stage_2_ats_scoring(
            resume=resume,
            required_role_keywords=["AWS", "Terraform", "Kubernetes"],
            min_experience_years=5.0
        )
        self.assertFalse(ats.passed)
        self.assertEqual(ats.status, StageStatus.FAILED)

    def test_stage_3_screening_work_auth_prereq(self):
        screening, _ = self.orchestrator.run_stage_3_screening(
            candidate_id="CAN-TEST-004",
            work_auth=False,
            salary_fit=True,
            notice_days=30,
            raw_screening_score=85.0
        )
        self.assertFalse(screening.prerequisite_met)
        self.assertFalse(screening.status == StageStatus.PASSED)
        self.assertIn("NO_VALID_WORK_AUTH", screening.flags)

    def test_stage_4_hr_interview_red_flags(self):
        hr, _ = self.orchestrator.run_stage_4_hr_interview(
            candidate_id="CAN-TEST-005",
            behavioral_score=40.0,
            communication_clarity_score=50.0,
            confidence_index=60.0,
            sentiment_stability_score=40.0,
            speech_pause_telemetry=35.0
        )
        self.assertEqual(hr.status, StageStatus.FAILED)
        self.assertIn("CULTURE_FIT_DEFICIT", hr.red_flags)
        self.assertIn("HIGH_SENTIMENT_VOLATILITY", hr.red_flags)

    def test_stage_5_technical_interview_eval(self):
        tech, _ = self.orchestrator.run_stage_5_technical_interview(
            candidate_id="CAN-TEST-006",
            coding_correctness=95.0,
            algorithmic_efficiency=90.0,
            system_design=88.0,
            problem_solving=92.0,
            test_cases_passed=10,
            total_test_cases=10
        )
        self.assertTrue(tech.status == StageStatus.PASSED)
        self.assertGreaterEqual(tech.composite_technical_score, 90.0)

    def test_stage_6_final_decision_arbitration(self):
        ats = ATSScoreResult("CAN-007", 90.0, 90.0, 90.0, 90.0, True)
        screening = ScreeningResult("CAN-007", True, True, 30, True, 90.0)
        hr = HRInterviewResult("CAN-007", 85.0, 85.0, 85.0, 85.0, 85.0, 85.0)
        tech = TechnicalInterviewResult("CAN-007", 92.0, 90.0, 88.0, 90.0, 90.5, 10, 10)

        final_dec, _ = self.orchestrator.run_stage_6_final_decision(
            candidate_id="CAN-007",
            ats=ats,
            screening=screening,
            hr=hr,
            tech=tech,
            human_verdict=DecisionVerdict.STRONG_HIRE
        )
        self.assertIn(final_dec.ai_verdict, [DecisionVerdict.STRONG_HIRE, DecisionVerdict.HIRE])
        self.assertTrue(final_dec.alignment)

    def test_complete_journey_orchestration(self):
        cand_data = {
            "candidate_id": "CAN-JRN-01",
            "full_name": "Sarah Connor",
            "target_role": "Security Systems Specialist",
            "experience_years": 7.0,
            "education_level": "B.S.",
            "institution": "Caltech",
            "primary_skills": ["Security", "Cryptography", "Python"],
            "resume_text": "7 years experience in Security, Cryptography, and Python systems.",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 90.0},
            "hr_interview": {"behavioral": 85.0, "communication": 88.0, "confidence": 85.0, "sentiment": 85.0, "speech_pause": 80.0},
            "technical_interview": {"coding": 92.0, "algorithmic": 88.0, "design": 85.0, "problem_solving": 90.0, "passed_cases": 9, "total_cases": 10},
            "human_verdict": DecisionVerdict.HIRE,
            "human_score": 88.0,
            "human_bias": None
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["Security", "Cryptography"])
        self.assertEqual(len(dossier.stage_progression), 6)
        self.assertTrue(dossier.journey_passed)
        self.assertGreater(dossier.total_latency_ms, 0.0)

    def test_comparative_judgment_metrics(self):
        cand_data = {
            "candidate_id": "CAN-COMP-01",
            "full_name": "Test User",
            "target_role": "Engineer",
            "experience_years": 5.0,
            "education_level": "B.S.",
            "institution": "Univ",
            "primary_skills": ["Python"],
            "resume_text": "5 years Python experience",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 85.0},
            "hr_interview": {"behavioral": 80.0, "communication": 80.0, "confidence": 80.0, "sentiment": 80.0, "speech_pause": 80.0},
            "technical_interview": {"coding": 85.0, "algorithmic": 80.0, "design": 80.0, "problem_solving": 80.0, "passed_cases": 8, "total_cases": 10},
            "human_verdict": DecisionVerdict.HIRE,
            "human_score": 82.0,
            "human_bias": None
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["Python"])
        comp = self.comparator.evaluate_candidate(dossier, human_score=82.0, human_verdict=DecisionVerdict.HIRE)
        self.assertEqual(comp.classification_quadrant, "TRUE_POSITIVE")

        metrics = self.comparator.compute_cohort_metrics([comp])
        self.assertEqual(metrics["total_candidates"], 1)
        self.assertEqual(metrics["confusion_matrix"]["true_positives"], 1)
        self.assertEqual(metrics["metrics"]["accuracy"], 1.0)

    def test_inconsistency_fluency_disguise(self):
        cand_data = {
            "candidate_id": "CAN-INC-01",
            "full_name": "Charming Speaker",
            "target_role": "Backend Lead",
            "experience_years": 6.0,
            "education_level": "B.A.",
            "institution": "State Univ",
            "primary_skills": ["Agile"],
            "resume_text": "Experience Agile",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 80.0},
            "hr_interview": {"behavioral": 90.0, "communication": 95.0, "confidence": 92.0, "sentiment": 90.0, "speech_pause": 90.0},
            "technical_interview": {"coding": 42.0, "algorithmic": 45.0, "design": 40.0, "problem_solving": 45.0, "passed_cases": 3, "total_cases": 10},
            "human_verdict": DecisionVerdict.HIRE,
            "human_score": 80.0,
            "human_bias": None
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["Agile"])
        records = self.detector.scan_dossier_for_inconsistencies(dossier)
        types = [r.inconsistency_type for r in records]
        self.assertIn(InconsistencyType.FLUENCY_DISGUISE, types)

    def test_inconsistency_pedigree_halo_bias(self):
        cand_data = {
            "candidate_id": "CAN-INC-02",
            "full_name": "Ivy League Alum",
            "target_role": "Lead",
            "experience_years": 5.0,
            "education_level": "M.S.",
            "institution": "Elite College",
            "primary_skills": ["Management"],
            "resume_text": "Elite College alumni",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 80.0},
            "hr_interview": {"behavioral": 75.0, "communication": 75.0, "confidence": 75.0, "sentiment": 75.0, "speech_pause": 75.0},
            "technical_interview": {"coding": 50.0, "algorithmic": 50.0, "design": 52.0, "problem_solving": 50.0, "passed_cases": 5, "total_cases": 10},
            "human_verdict": DecisionVerdict.HIRE,
            "human_score": 85.0,
            "human_bias": "PEDIGREE_HALO"
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["Management"])
        self.comparator.evaluate_candidate(dossier, 85.0, DecisionVerdict.HIRE, human_bias_marker="PEDIGREE_HALO")
        records = self.detector.scan_dossier_for_inconsistencies(dossier)
        types = [r.inconsistency_type for r in records]
        self.assertIn(InconsistencyType.PEDIGREE_HALO_BIAS, types)

    def test_inconsistency_resume_inflation(self):
        cand_data = {
            "candidate_id": "CAN-INC-03",
            "full_name": "Resume Inflator",
            "target_role": "Senior Engineer",
            "experience_years": 8.0,
            "education_level": "B.S.",
            "institution": "Univ",
            "primary_skills": ["Python", "Rust", "C++", "Kubernetes", "AWS"],
            "resume_text": "Experience: 8 years skills Python, Rust, C++, Kubernetes, AWS, Microservices. Education: B.S.",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 90.0},
            "hr_interview": {"behavioral": 70.0, "communication": 70.0, "confidence": 70.0, "sentiment": 70.0, "speech_pause": 70.0},
            "technical_interview": {"coding": 35.0, "algorithmic": 38.0, "design": 40.0, "problem_solving": 35.0, "passed_cases": 2, "total_cases": 10},
            "human_verdict": DecisionVerdict.REJECT,
            "human_score": 40.0,
            "human_bias": None
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["Python", "Rust", "C++", "Kubernetes", "AWS"])
        records = self.detector.scan_dossier_for_inconsistencies(dossier)
        types = [r.inconsistency_type for r in records]
        self.assertIn(InconsistencyType.RESUME_INFLATION, types)

    def test_system_performance_sla_and_bottleneck(self):
        cand_data = {
            "candidate_id": "CAN-PERF-01",
            "full_name": "Perf Test",
            "target_role": "Dev",
            "experience_years": 3.0,
            "education_level": "B.S.",
            "institution": "Univ",
            "primary_skills": ["Python"],
            "resume_text": "Python developer",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 80.0},
            "hr_interview": {"behavioral": 75.0, "communication": 75.0, "confidence": 75.0, "sentiment": 75.0, "speech_pause": 75.0},
            "technical_interview": {"coding": 75.0, "algorithmic": 75.0, "design": 75.0, "problem_solving": 75.0, "passed_cases": 8, "total_cases": 10},
            "human_verdict": DecisionVerdict.HIRE,
            "human_score": 75.0,
            "human_bias": None
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["Python"])
        perf = self.analyzer.analyze_cohort_performance([dossier])
        self.assertEqual(perf["sla_compliance"]["compliance_percentage"], 100.0)
        self.assertIn("STAGE_5_TECHNICAL_EXECUTION", perf["throughput_capacity"]["primary_bottleneck"])

    def test_inconsistency_accent_penalty_telemetry(self):
        cand_data = {
            "candidate_id": "CAN-INC-04",
            "full_name": "Non-Native Algorithmic Master",
            "target_role": "Senior Algorithmist",
            "experience_years": 5.0,
            "education_level": "M.S.",
            "institution": "Univ",
            "primary_skills": ["C++", "Algorithms"],
            "resume_text": "C++ algorithms",
            "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 90.0},
            "hr_interview": {"behavioral": 75.0, "communication": 70.0, "confidence": 65.0, "sentiment": 70.0, "speech_pause": 38.0},
            "technical_interview": {"coding": 98.0, "algorithmic": 95.0, "design": 92.0, "problem_solving": 95.0, "passed_cases": 10, "total_cases": 10},
            "human_verdict": DecisionVerdict.HIRE,
            "human_score": 88.0,
            "human_bias": None
        }
        dossier = self.orchestrator.simulate_complete_journey(cand_data, ["C++", "Algorithms"])
        # Set variance smoothed score slightly lower to trigger anomaly
        dossier.final_decision.variance_smoothed_score = 68.0
        records = self.detector.scan_dossier_for_inconsistencies(dossier)
        types = [r.inconsistency_type for r in records]
        self.assertIn(InconsistencyType.ACCENT_BIAS_DRIFT, types)

    def test_cohen_kappa_unanimity_handling(self):
        c1 = self.comparator.evaluate_candidate(
            dossier=self.orchestrator.simulate_complete_journey({
                "candidate_id": "C1", "full_name": "U1", "target_role": "R", "experience_years": 5.0,
                "education_level": "BS", "institution": "I", "primary_skills": ["P"], "resume_text": "text P",
                "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 85.0},
                "hr_interview": {"behavioral": 80.0, "communication": 80.0, "confidence": 80.0, "sentiment": 80.0, "speech_pause": 80.0},
                "technical_interview": {"coding": 85.0, "algorithmic": 85.0, "design": 85.0, "problem_solving": 85.0, "passed_cases": 9, "total_cases": 10},
                "human_verdict": DecisionVerdict.HIRE, "human_score": 85.0, "human_bias": None
            }, ["P"]),
            human_score=85.0, human_verdict=DecisionVerdict.HIRE
        )
        metrics = self.comparator.compute_cohort_metrics([c1])
        self.assertIn("cohen_kappa", metrics["metrics"])
        self.assertGreaterEqual(metrics["metrics"]["cohen_kappa"], 0.0)

    def test_pearson_correlation_range(self):
        c1 = self.comparator.evaluate_candidate(
            dossier=self.orchestrator.simulate_complete_journey({
                "candidate_id": "C1", "full_name": "U1", "target_role": "R", "experience_years": 5.0,
                "education_level": "BS", "institution": "I", "primary_skills": ["P"], "resume_text": "text P",
                "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 90.0},
                "hr_interview": {"behavioral": 90.0, "communication": 90.0, "confidence": 90.0, "sentiment": 90.0, "speech_pause": 90.0},
                "technical_interview": {"coding": 90.0, "algorithmic": 90.0, "design": 90.0, "problem_solving": 90.0, "passed_cases": 10, "total_cases": 10},
                "human_verdict": DecisionVerdict.STRONG_HIRE, "human_score": 92.0, "human_bias": None
            }, ["P"]),
            human_score=92.0, human_verdict=DecisionVerdict.STRONG_HIRE
        )
        c2 = self.comparator.evaluate_candidate(
            dossier=self.orchestrator.simulate_complete_journey({
                "candidate_id": "C2", "full_name": "U2", "target_role": "R", "experience_years": 1.0,
                "education_level": "None", "institution": "None", "primary_skills": [], "resume_text": "none",
                "screening": {"work_auth": True, "salary_fit": True, "notice_days": 30, "score": 40.0},
                "hr_interview": {"behavioral": 40.0, "communication": 40.0, "confidence": 40.0, "sentiment": 40.0, "speech_pause": 40.0},
                "technical_interview": {"coding": 30.0, "algorithmic": 30.0, "design": 30.0, "problem_solving": 30.0, "passed_cases": 1, "total_cases": 10},
                "human_verdict": DecisionVerdict.REJECT, "human_score": 35.0, "human_bias": None
            }, ["P"]),
            human_score=35.0, human_verdict=DecisionVerdict.REJECT
        )
        metrics = self.comparator.compute_cohort_metrics([c1, c2])
        r = metrics["metrics"]["pearson_r"]
        self.assertTrue(-1.0 <= r <= 1.0)


if __name__ == "__main__":
    unittest.main()

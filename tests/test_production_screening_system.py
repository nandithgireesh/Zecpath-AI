"""
Unit Tests for Day 32: Production Screening System Orchestrator
================================================================
"""

import unittest
from screening_ai.production_models import (
    ProductionSessionConfig,
    ScreeningTurnInput,
)
from screening_ai.production_screening_system import ProductionScreeningSystem


class TestProductionScreeningSystem(unittest.TestCase):
    def setUp(self):
        self.system = ProductionScreeningSystem()
        self.config = ProductionSessionConfig(
            candidate_id="cand_test_001",
            candidate_name="Pooja Kulkarni",
            job_role="Senior Python Engineer",
            target_experience_years=4.0,
            max_budget_lpa=28.0,
            max_notice_days=60,
            apply_threshold_optimization=True,
            enable_acoustic_fairness_buffer=True,
            enable_hinglish_normalization=True,
        )

    def test_01_session_start(self):
        session = self.system.start_session(self.config)
        self.assertTrue(session.session_id.startswith("sess_prod_"))
        self.assertEqual(session.current_state, "GREETING")
        self.assertEqual(session.status, "ACTIVE")
        self.assertEqual(len(session.turns), 1)
        self.assertIn("Pooja Kulkarni", session.turns[0]["text"])

    def test_02_turn_greeting_progression(self):
        session = self.system.start_session(self.config)
        turn_input = ScreeningTurnInput(
            turn_index=1,
            candidate_speech="Yes, I am ready to start the interview.",
            snr_db=25.0,
            amplitude_dbfs=-14.0,
        )
        out = self.system.process_turn(session.session_id, turn_input)
        self.assertEqual(out.turn_index, 1)
        self.assertEqual(out.current_state, "ELIGIBILITY_CHECK")
        self.assertIn("experience", out.ai_spoken_prompt.lower())
        self.assertEqual(out.safety_tier, "NORMAL_FLOW")

    def test_03_hinglish_code_switching_normalization(self):
        session = self.system.start_session(self.config)
        # Advance to eligibility
        self.system.process_turn(session.session_id, ScreeningTurnInput(
            turn_index=1,
            candidate_speech="Yes, ready."
        ))
        
        # Turn 2 with Hinglish
        turn2 = ScreeningTurnInput(
            turn_index=2,
            candidate_speech="Maine paanch saal Python aur Celery use kiya tha async pipelines ke liye.",
            snr_db=26.0,
        )
        out2 = self.system.process_turn(session.session_id, turn2)
        self.assertIsNotNone(out2.normalized_speech)
        self.assertIn("python", out2.extracted_entities.get("technologies", []))
        self.assertIn("celery", out2.extracted_entities.get("technologies", []))
        self.assertEqual(out2.current_state, "TECHNICAL_QUESTIONING")

    def test_04_line_check_filler_recovery(self):
        session = self.system.start_session(self.config)
        turn_filler = ScreeningTurnInput(
            turn_index=1,
            candidate_speech="hello? am I audible? can you hear me?",
            response_time_seconds=3.0,
        )
        out = self.system.process_turn(session.session_id, turn_filler)
        self.assertEqual(out.safety_tier, "LINE_CHECK_CONFIRM")
        self.assertIn("hear you", out.ai_spoken_prompt.lower())
        self.assertFalse(out.is_terminal)

    def test_05_explicit_pass_accommodation(self):
        session = self.system.start_session(self.config)
        turn_pass = ScreeningTurnInput(
            turn_index=1,
            candidate_speech="I don't know, can we pass this question?",
            response_time_seconds=2.0,
        )
        out = self.system.process_turn(session.session_id, turn_pass)
        self.assertEqual(out.safety_tier, "PASS_ADVANCE")
        self.assertIn("move forward", out.ai_spoken_prompt.lower())
        self.assertFalse(out.is_terminal)

    def test_06_acoustic_retry_on_whisper(self):
        session = self.system.start_session(self.config)
        turn_whisper = ScreeningTurnInput(
            turn_index=1,
            candidate_speech="yes i am ready",
            snr_db=22.0,
            amplitude_dbfs=-35.0,  # Whisper threshold <= -28 dBFS
        )
        out = self.system.process_turn(session.session_id, turn_whisper)
        self.assertEqual(out.safety_tier, "ACOUSTIC_REPEAT")
        self.assertIn("faint", out.ai_spoken_prompt.lower())
        self.assertGreater(out.acoustic_discount, 0.0)

    def test_07_full_session_finalization(self):
        session = self.system.start_session(self.config)
        
        # Turn 1
        self.system.process_turn(session.session_id, ScreeningTurnInput(
            turn_index=1, candidate_speech="Yes, ready."
        ))
        # Turn 2
        self.system.process_turn(session.session_id, ScreeningTurnInput(
            turn_index=2, candidate_speech="I have 5 years experience in Python, FastAPI, and Docker microservices."
        ))
        # Turn 3
        self.system.process_turn(session.session_id, ScreeningTurnInput(
            turn_index=3, candidate_speech="We implemented Redis caching and Kafka message queues for asynchronous scaling."
        ))
        
        # Finalize
        report = self.system.finalize_session(session.session_id)
        self.assertEqual(report["candidate_id"], "cand_test_001")
        self.assertTrue(report["eligibility_verified"])
        self.assertIn(report["decision"], ["HIRE", "STRONG_HIRE"])
        self.assertGreaterEqual(report["final_score"], 65.0)
        self.assertIn("python", report["technologies_verified"])
        self.assertIn("redis", report["technologies_verified"])
        self.assertEqual(report["false_rejection_risk"], "0.0%")
        self.assertEqual(session.status, "COMPLETED")

    def test_08_system_health_and_manifest(self):
        health = self.system.get_system_health()
        self.assertEqual(health.status, "HEALTHY")
        self.assertEqual(health.uptime_status, "OPERATIONAL")
        self.assertGreaterEqual(len(health.subsystems), 10)
        
        manifest = self.system.get_handover_manifest()
        self.assertEqual(manifest.author, "Nandith Gireesh")
        self.assertEqual(manifest.total_curriculum_days, 12)
        self.assertEqual(len(manifest.modules_inventory), 12)
        self.assertEqual(manifest.metrics_summary["false_rejection_rate"], "0.0%")
        self.assertEqual(manifest.metrics_summary["system_resilience_rate"], "100.0%")


if __name__ == "__main__":
    unittest.main()

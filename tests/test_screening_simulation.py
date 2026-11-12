"""
Unit Tests for Day 30 Screening Call Simulation Engine & Optimized Flow
=======================================================================
"""

import unittest
from screening_ai.simulation_engine import ScreeningSimulationEngine
from screening_ai.optimized_flow import OptimizedCallFlowController
from screening_ai.optimization_models import CandidateArchetype
from screening_ai.report_models import HiringRecommendation
from screening_ai.call_flow_engine import AICallFlowEngine


class TestScreeningSimulation(unittest.TestCase):
    def setUp(self):
        self.sim_engine = ScreeningSimulationEngine()
        self.flow_controller = OptimizedCallFlowController()

    def test_load_benchmark_profiles(self):
        profiles = self.sim_engine.get_profiles()
        self.assertEqual(len(profiles), 12)

    def test_get_profile_by_id(self):
        p = self.sim_engine.get_profile_by_id("cand_expert_fluent")
        self.assertIsNotNone(p)
        self.assertEqual(p["candidate_name"], "Aarav Sharma")
        self.assertIsNone(self.sim_engine.get_profile_by_id("non_existent_cand"))

    def test_simulate_fluent_expert_call(self):
        res = self.sim_engine.simulate_call("cand_expert_fluent", use_optimized_thresholds=True)
        self.assertEqual(res.candidate_id, "cand_expert_fluent")
        self.assertEqual(res.archetype, CandidateArchetype.EXPERT_FLUENT)
        self.assertEqual(res.total_turns, 3)
        self.assertIn(res.ai_recommendation, [HiringRecommendation.STRONG_HIRE, HiringRecommendation.HIRE])
        self.assertFalse(res.is_false_rejection)
        self.assertFalse(res.is_false_acceptance)

    def test_simulate_terse_expert_call_optimized_vs_baseline(self):
        # Baseline simulation should trigger false rejection
        base_res = self.sim_engine.simulate_call("cand_expert_terse", use_optimized_thresholds=False)
        self.assertTrue(base_res.is_false_rejection)

        # Optimized simulation rescues terse candidate
        opt_res = self.sim_engine.simulate_call("cand_expert_terse", use_optimized_thresholds=True)
        self.assertFalse(opt_res.is_false_rejection)
        self.assertIn(opt_res.ai_recommendation, [HiringRecommendation.STRONG_HIRE, HiringRecommendation.HIRE])


    def test_simulate_underqualified_call(self):
        res = self.sim_engine.simulate_call("cand_underqualified_evasive", use_optimized_thresholds=True)
        self.assertEqual(res.ai_recommendation, HiringRecommendation.NO_HIRE)
        self.assertFalse(res.is_false_rejection)
        self.assertFalse(res.is_false_acceptance)

    def test_simulate_all_calls(self):
        all_results = self.sim_engine.simulate_all_calls(use_optimized_thresholds=True)
        self.assertEqual(len(all_results), 12)
        false_accepts = sum(1 for r in all_results if r.is_false_acceptance)
        self.assertEqual(false_accepts, 0)

    def test_optimized_flow_microprobe(self):
        # Start a session
        session, _ = self.flow_controller.engine.start_session("cand_probe_test", "Nandith Gireesh", "Cloud Architect")
        self.flow_controller.engine.process_turn(session.session_id, "Yes, I consent.")

        # Give a terse high-skill answer (e.g. 7 words with kafka and kubernetes)
        sess, action = self.flow_controller.process_candidate_utterance_with_optimization(
            session_id=session.session_id,
            candidate_utterance="We use Kafka with Kubernetes clusters.",
            silence_ms=1000,
            hesitation_count=0,
        )
        self.assertIn("adaptive_probe", action.metadata)
        self.assertEqual(action.metadata["adaptive_probe"], "terse_domain_deepen")

    def test_optimized_flow_reassurance(self):
        # Start a session
        session, _ = self.flow_controller.engine.start_session("cand_reassure_test", "Pooja Hegde", "Developer")
        self.flow_controller.engine.process_turn(session.session_id, "Yes, I agree to proceed.")

        # Give an answer with high hesitation (e.g. 4 hesitations)
        sess, action = self.flow_controller.process_candidate_utterance_with_optimization(
            session_id=session.session_id,
            candidate_utterance="Um, uh, so basically we use Redux Toolkit.",
            silence_ms=2500,
            hesitation_count=4,
        )
        self.assertIn("adaptive_reassurance", action.metadata)
        self.assertEqual(action.metadata["adaptive_reassurance"], "nervous_pacing_cushion")


if __name__ == "__main__":
    unittest.main()

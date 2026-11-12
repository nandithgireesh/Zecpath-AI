"""
Unit Tests for Day 34: Dynamic Follow-Up Logic & Adaptive Questioning Engine
===========================================================================
Validates:
1. Ambiguity & vagueness detection (hand-waving phrases, brevity, missing agency).
2. Clarification trigger for terse or ambiguous responses.
3. Deepening trigger for simple/shallow responses (Difficulty Adaptation: Simple -> Deeper).
4. Scenario-based challenge for confident responses (Difficulty Adaptation: Confident -> Scenario).
5. Example-based trigger for purely theoretical responses lacking STAR grounding.
6. Repetition prevention and max follow-up depth cap (K=1).
7. Full conversation state tracking & enriched ATS dossier export.
"""

import unittest
from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    HRInterviewConfig,
    FollowUpTriggerReason,
    FollowUpProbeCategory,
    AdaptationTier,
    HRQuestionTemplate,
)
from interview_ai.hr_question_generator import HRQuestionBank
from interview_ai.dynamic_followup_engine import (
    VaguenessAmbiguityAnalyzer,
    DynamicFollowUpEngine,
)
from interview_ai.hr_flow_engine import HRInterviewFlowEngine


class TestDynamicFollowUpEngine(unittest.TestCase):

    def setUp(self):
        self.analyzer = VaguenessAmbiguityAnalyzer()
        self.engine = DynamicFollowUpEngine()
        self.flow_engine = HRInterviewFlowEngine()
        self.bank = HRQuestionBank()

        self.tech_question = self.bank.find_question(
            category=HRCategory.CAREER_JOURNEY,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
        )

        self.team_question = self.bank.find_question(
            category=HRCategory.TEAMWORK_AND_CULTURE_FIT,
            experience_tier=ExperienceTier.EXPERIENCED,
            role_track=RoleTrack.TECHNICAL,
        )

    def test_01_ambiguity_and_vagueness_detection(self):
        """Validates detection of filler phrases, brevity, and ambiguity scoring."""
        # 1. Clear, detailed text
        clear_text = "I architected and deployed a Redis caching cluster that reduced p99 query latency by 45% across 20 microservices."
        diag_clear = self.analyzer.analyze(clear_text, HRCategory.CAREER_JOURNEY, is_technical=True)
        self.assertFalse(diag_clear["is_terse"])
        self.assertEqual(diag_clear["vagueness_score"], 0.0)
        self.assertTrue(diag_clear["confidence_score"] >= 0.70)

        # 2. Vague, hand-waving text
        vague_text = "I basically did some backend coding and all, like fixing stuff and things like that."
        diag_vague = self.analyzer.analyze(vague_text, HRCategory.CAREER_JOURNEY, is_technical=True)
        self.assertTrue(diag_vague["vagueness_score"] >= 0.50)
        self.assertIn("and all", diag_vague["vague_hits"])
        self.assertIn("stuff", diag_vague["vague_hits"])

        # 3. Ultra-terse text
        terse_text = "I do Python."
        diag_terse = self.analyzer.analyze(terse_text, HRCategory.CAREER_JOURNEY, is_technical=True)
        self.assertTrue(diag_terse["is_terse"])
        self.assertTrue(diag_terse["is_ultra_terse"])

    def test_02_clarification_trigger_terse_and_ambiguous(self):
        """Verifies that terse and vague answers trigger a CLARIFICATION probe."""
        terse_input = "I worked on cloud stuff and databases and all."
        needs_fup, reason, category, tier, prompt, diag = self.engine.evaluate_and_generate_followup(
            current_question=self.tech_question,
            candidate_response=terse_input,
            current_depth=0,
        )

        self.assertTrue(needs_fup)
        self.assertEqual(category, FollowUpProbeCategory.CLARIFICATION)
        self.assertEqual(reason, FollowUpTriggerReason.TERSE_RESPONSE)
        self.assertEqual(tier, AdaptationTier.DEEP_PROBE)
        self.assertTrue(len(prompt) > 20)

    def test_03_deepening_trigger_simple_responses(self):
        """Validates difficulty adaptation: Simple response -> DEEPENING probe."""
        simple_input = "I write code for our backend services and I like solving general software problems every day."
        needs_fup, reason, category, tier, prompt, diag = self.engine.evaluate_and_generate_followup(
            current_question=self.tech_question,
            candidate_response=simple_input,
            current_depth=0,
        )

        self.assertTrue(needs_fup)
        self.assertEqual(category, FollowUpProbeCategory.DEEPENING)
        self.assertEqual(reason, FollowUpTriggerReason.SURFACE_LEVEL)
        self.assertEqual(tier, AdaptationTier.DEEP_PROBE)
        self.assertTrue("deeper" in prompt.lower() or "depth" in prompt.lower() or "trade-offs" in prompt.lower() or "implications" in prompt.lower())

    def test_04_scenario_based_followup_confident_responses(self):
        """Validates difficulty adaptation: Confident response -> SCENARIO_CHALLENGE probe."""
        confident_input = (
            "Over the past 5 years I architected high-throughput microservices handling 50k QPS "
            "with Redis and Kafka, reducing p99 latency by 45% and optimizing database concurrency under peak scale."
        )
        needs_fup, reason, category, tier, prompt, diag = self.engine.evaluate_and_generate_followup(
            current_question=self.tech_question,
            candidate_response=confident_input,
            current_depth=0,
        )

        self.assertTrue(needs_fup)
        self.assertEqual(category, FollowUpProbeCategory.SCENARIO_CHALLENGE)
        self.assertEqual(reason, FollowUpTriggerReason.HIGH_CONFIDENCE)
        self.assertEqual(tier, AdaptationTier.SCENARIO_CHALLENGE)
        self.assertTrue("scenario" in prompt.lower() or "challenge" in prompt.lower() or "surge" in prompt.lower() or "failure" in prompt.lower())

    def test_05_example_based_trigger_pure_theory(self):
        """Verifies that purely theoretical responses without personal grounding trigger an EXAMPLE_BASED probe."""
        theory_input = (
            "Object-oriented design revolves around encapsulation, inheritance, and polymorphism "
            "to ensure decoupled architecture and modular maintainability across large enterprise systems."
        )
        needs_fup, reason, category, tier, prompt, diag = self.engine.evaluate_and_generate_followup(
            current_question=self.tech_question,
            candidate_response=theory_input,
            current_depth=0,
        )

        self.assertTrue(needs_fup)
        self.assertEqual(category, FollowUpProbeCategory.EXAMPLE_BASED)
        self.assertEqual(reason, FollowUpTriggerReason.THEORETICAL_ONLY)
        self.assertTrue("incident" in prompt.lower() or "example" in prompt.lower() or "project" in prompt.lower() or "outage" in prompt.lower())

    def test_06_repetition_prevention_and_max_depth(self):
        """Verifies anti-repetition guard: follow-up depth cap (K=1) halts interrogation loops."""
        # First turn: terse input at depth=0 -> triggers follow-up
        terse_input = "I do Python backend."
        needs_fup_1, _, _, _, _, _ = self.engine.evaluate_and_generate_followup(
            current_question=self.tech_question,
            candidate_response=terse_input,
            current_depth=0,
        )
        self.assertTrue(needs_fup_1)

        # Second turn on same parent question at depth=1 -> blocked by depth cap
        still_terse = "Still doing Python."
        needs_fup_2, reason_2, cat_2, tier_2, prompt_2, _ = self.engine.evaluate_and_generate_followup(
            current_question=self.tech_question,
            candidate_response=still_terse,
            current_depth=1,  # Already probed once!
        )
        self.assertFalse(needs_fup_2)
        self.assertEqual(reason_2, FollowUpTriggerReason.NONE)
        self.assertEqual(cat_2, FollowUpProbeCategory.NONE)
        self.assertEqual(prompt_2, "")

    def test_07_full_adaptive_session_and_ats_telemetry(self):
        """Verifies full conversational flow integration, tracking follow-up types and exporting ATS dossier."""
        cfg = HRInterviewConfig.auto_classify(
            candidate_id="CAND-ADV-34",
            candidate_name="Vikram Mehta",
            job_role="Senior Distributed Systems Architect",
            experience_years=6.5,
        )
        session = self.flow_engine.start_session(cfg)

        # 1. Introduction: Good detailed intro
        t1 = self.flow_engine.process_turn(
            session.session_id,
            "Hello, I am Vikram Mehta. For 6 years, I have architected and scaled distributed backend pipelines.",
        )
        # Should advance to Phase 2 CORE_HR
        self.assertEqual(t1.phase, InterviewPhase.CORE_HR)

        # 2. Strengths: Confident answer triggering a scenario challenge
        t2 = self.flow_engine.process_turn(
            session.session_id,
            "My strength is designing high-throughput microservices handling 50k QPS with Redis and Kafka, optimizing p99 latency under scale.",
        )
        # Should trigger SCENARIO_CHALLENGE probe
        self.assertTrue(t2.follow_up_triggered)
        self.assertEqual(t2.adaptation_tier, AdaptationTier.SCENARIO_CHALLENGE)
        self.assertEqual(t2.probe_category, FollowUpProbeCategory.SCENARIO_CHALLENGE)
        self.assertEqual(session.total_scenarios_triggered, 1)

        # 3. Answer the scenario challenge
        t3 = self.flow_engine.process_turn(
            session.session_id,
            "In that outage scenario, I immediately enable rate limiting, isolate degraded workers, and fail over to read-replicas.",
        )
        # Should now advance to Teamwork question
        self.assertEqual(t3.question_id, "HR-TEAM-E-TECH-01")

        # 4. Teamwork: Conflict avoidance response
        t4 = self.flow_engine.process_turn(
            session.session_id,
            "In our engineering teams we never had any conflict, everybody always agreed on all design docs.",
        )
        # Should trigger CONFLICT_AVOIDANCE probe
        self.assertTrue(t4.follow_up_triggered)
        self.assertEqual(session.turns[-2].follow_up_reason, FollowUpTriggerReason.CONFLICT_AVOIDANCE)

        # 5. Answer conflict probe
        t5 = self.flow_engine.process_turn(
            session.session_id,
            "When we disagreed on database schema migration, I led a benchmarking test and aligned everyone on objective latency data.",
        )
        self.assertEqual(t5.question_id, "HR-JOURNEY-E-TECH-01")

        # Check export dossier
        dossier = self.flow_engine.export_session_dossier(session.session_id)
        self.assertEqual(dossier["candidate_name"], "Vikram Mehta")
        self.assertEqual(dossier["total_scenarios_triggered"], 1)
        self.assertTrue(dossier["follow_ups_triggered"] >= 2)
        self.assertTrue(len(dossier["probes_dispatched_history"]) >= 2)


if __name__ == "__main__":
    unittest.main()

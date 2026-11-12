"""
Day 33: Automated Unit Test Suite for HR Interview Engine
=========================================================
Verifies:
1. All 6 HR categories representation and schemas
2. Role-based Question Generator across all 4 quadrants (Fresher/Exp x Tech/NonTech)
3. Interview state structure (question ID, response capture, follow-up eligibility)
4. Phase progression across the 4 conversation phases (Introduction -> Core HR -> Role Evaluation -> Closing)
5. Adaptive follow-up probing triggers (terse answers, conflict avoidance, substantive responses)
"""

import unittest
from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    FollowUpTriggerReason,
    HRInterviewConfig,
    HRInterviewSession,
    InterviewTurnState,
)
from interview_ai.hr_question_generator import (
    HRQuestionBank,
    HRQuestionGenerator,
)
from interview_ai.hr_flow_engine import HRInterviewFlowEngine


class TestHRInterviewEngine(unittest.TestCase):
    """Comprehensive test harness for the Day 33 HR Interview Engine."""

    def setUp(self):
        self.bank = HRQuestionBank()
        self.generator = HRQuestionGenerator(self.bank)
        self.engine = HRInterviewFlowEngine(self.generator)

    def test_01_hr_categories_and_models(self):
        """Validates all 6 mandatory HR categories and enum values."""
        expected_categories = {
            "self_introduction",
            "career_journey",
            "strengths_and_weaknesses",
            "teamwork_and_culture_fit",
            "career_goals",
            "availability_and_commitment",
        }
        actual_categories = {c.value for c in HRCategory}
        self.assertEqual(actual_categories, expected_categories)

        # Validate Phase Enums
        expected_phases = {"introduction", "core_hr", "role_based_evaluation", "closing"}
        self.assertEqual({p.value for p in InterviewPhase}, expected_phases)

        # Validate Auto-Classification
        cfg_fresher_tech = HRInterviewConfig.auto_classify(
            candidate_id="cand_01",
            candidate_name="Ananya Sharma",
            job_role="Junior Cloud Engineer",
            experience_years=0.8,
            target_skills=["AWS", "Docker", "Python"],
        )
        self.assertEqual(cfg_fresher_tech.experience_tier, ExperienceTier.FRESHER)
        self.assertEqual(cfg_fresher_tech.role_track, RoleTrack.TECHNICAL)

        cfg_exp_nontech = HRInterviewConfig.auto_classify(
            candidate_id="cand_02",
            candidate_name="Vikram Seth",
            job_role="Senior Brand Marketing Manager",
            experience_years=6.5,
            target_skills=["Growth Marketing", "Brand Strategy", "P&L"],
        )
        self.assertEqual(cfg_exp_nontech.experience_tier, ExperienceTier.EXPERIENCED)
        self.assertEqual(cfg_exp_nontech.role_track, RoleTrack.NON_TECHNICAL)

    def test_02_question_bank_matrix_coverage(self):
        """Validates that question bank contains all 24 questions across all 4 quadrants."""
        all_questions = self.bank.get_all_questions()
        self.assertEqual(len(all_questions), 24)

        seen_ids = set()
        for q in all_questions:
            self.assertNotIn(q.question_id, seen_ids, f"Duplicate question ID: {q.question_id}")
            seen_ids.add(q.question_id)
            self.assertTrue(len(q.prompt_text) > 20)
            self.assertTrue(len(q.follow_up_prompt) > 15)
            self.assertTrue(len(q.evaluation_criteria) >= 2)
            self.assertTrue(len(q.expected_competencies) >= 2)

        # Check that each of the 6 categories is present for all 4 quadrants
        for tier in ExperienceTier:
            for track in RoleTrack:
                for cat in HRCategory:
                    match = self.bank.find_question(cat, tier, track)
                    self.assertIsNotNone(match, f"Missing question for: {cat}, {tier}, {track}")

    def test_03_role_based_question_generation(self):
        """Validates that question generator builds tailored paths for all 4 matrix quadrants."""
        configs = [
            # 1. Fresher Technical
            HRInterviewConfig(
                candidate_id="c1", candidate_name="Amit", job_role="Backend Dev",
                experience_years=0.5, experience_tier=ExperienceTier.FRESHER,
                role_track=RoleTrack.TECHNICAL,
            ),
            # 2. Fresher Non-Technical
            HRInterviewConfig(
                candidate_id="c2", candidate_name="Pooja", job_role="HR Associate",
                experience_years=0.0, experience_tier=ExperienceTier.FRESHER,
                role_track=RoleTrack.NON_TECHNICAL,
            ),
            # 3. Experienced Technical
            HRInterviewConfig(
                candidate_id="c3", candidate_name="Deepak", job_role="Principal Architect",
                experience_years=9.0, experience_tier=ExperienceTier.EXPERIENCED,
                role_track=RoleTrack.TECHNICAL,
            ),
            # 4. Experienced Non-Technical
            HRInterviewConfig(
                candidate_id="c4", candidate_name="Meera", job_role="VP of Sales",
                experience_years=12.0, experience_tier=ExperienceTier.EXPERIENCED,
                role_track=RoleTrack.NON_TECHNICAL,
            ),
        ]

        for cfg in configs:
            plan = self.generator.generate_interview_plan(cfg)
            self.assertEqual(len(plan), 6)

            # Ensure all questions in plan correspond to candidate's tier and track
            for q in plan:
                self.assertEqual(q.experience_tier, cfg.experience_tier)
                self.assertEqual(q.role_track, cfg.role_track)

            # Ensure sequence of categories and phases matches curriculum structure
            self.assertEqual(plan[0].category, HRCategory.SELF_INTRODUCTION)
            self.assertEqual(plan[0].phase, InterviewPhase.INTRODUCTION)

            self.assertEqual(plan[1].category, HRCategory.STRENGTHS_AND_WEAKNESSES)
            self.assertEqual(plan[1].phase, InterviewPhase.CORE_HR)

            self.assertEqual(plan[2].category, HRCategory.TEAMWORK_AND_CULTURE_FIT)
            self.assertEqual(plan[2].phase, InterviewPhase.CORE_HR)

            self.assertEqual(plan[3].category, HRCategory.CAREER_JOURNEY)
            self.assertEqual(plan[3].phase, InterviewPhase.ROLE_BASED_EVALUATION)

            self.assertEqual(plan[4].category, HRCategory.CAREER_GOALS)
            self.assertEqual(plan[4].phase, InterviewPhase.CLOSING)

            self.assertEqual(plan[5].category, HRCategory.AVAILABILITY_AND_COMMITMENT)
            self.assertEqual(plan[5].phase, InterviewPhase.CLOSING)

    def test_04_interview_state_and_response_capture(self):
        """Validates state structure: Question ID, response capture, word count, and timestamps."""
        cfg = HRInterviewConfig.auto_classify("cand_t4", "Karan Johar", "Fullstack Engineer", 3.0)
        session = self.engine.start_session(cfg)

        self.assertTrue(session.session_id.startswith("sess_hr_"))
        self.assertEqual(session.current_phase, InterviewPhase.INTRODUCTION)
        self.assertEqual(session.current_question_index, 0)
        self.assertEqual(len(session.turns), 1)

        first_turn = session.turns[0]
        self.assertEqual(first_turn.turn_index, 1)
        self.assertEqual(first_turn.question_id, "HR-INTRO-E-TECH-01")
        self.assertIsNone(first_turn.candidate_response)

        # Candidate provides response
        speech = "Hello, I am Karan. Over the past 3 years, I have architected high-throughput microservices using FastAPI, Redis, and PostgreSQL."
        next_turn = self.engine.process_turn(session.session_id, candidate_response=speech, response_time_seconds=1.2)

        # Inspect captured state on first turn
        updated_first_turn = session.turns[0]
        self.assertEqual(updated_first_turn.candidate_response, speech)
        self.assertIsNotNone(updated_first_turn.response_timestamp)
        self.assertEqual(updated_first_turn.word_count, len(speech.split()))
        self.assertEqual(updated_first_turn.response_time_seconds, 1.2)
        self.assertIn("Ownership", updated_first_turn.extracted_themes)
        self.assertTrue(updated_first_turn.phase_completed)

        # Next turn should be in CORE_HR
        self.assertEqual(next_turn.phase, InterviewPhase.CORE_HR)
        self.assertEqual(next_turn.question_id, "HR-STRENGTH-E-TECH-01")

    def test_05_follow_up_eligibility_triggers(self):
        """Validates adaptive probing logic for terse answers, conflict avoidance, and rich answers."""
        cfg = HRInterviewConfig.auto_classify("cand_t5", "Rahul Verma", "DevOps Engineer", 4.0)
        session = self.engine.start_session(cfg)

        # 1. Candidate gives terse response (< 15 words) on Introduction
        terse_speech = "I am Rahul. I do DevOps and cloud systems."  # 9 words
        follow_up_turn = self.engine.process_turn(session.session_id, terse_speech)

        # Turn 1 should be flagged as follow-up eligible
        turn_1 = session.turns[0]
        self.assertTrue(turn_1.follow_up_eligible)
        self.assertEqual(turn_1.follow_up_reason, FollowUpTriggerReason.TERSE_RESPONSE)

        # System should have generated a follow-up probe turn instead of advancing category
        self.assertEqual(follow_up_turn.question_id, "HR-INTRO-E-TECH-01-PROBE")
        self.assertTrue(follow_up_turn.follow_up_triggered)
        self.assertEqual(session.current_question_index, 0)  # Still on Q1

        # 2. Candidate answers follow-up with substantive detail
        detailed_speech = "Specifically, I spearheaded our Kubernetes migration across fifty microservices, reducing deployment latency by forty percent and managing our AWS Terraform infrastructure."
        advanced_turn = self.engine.process_turn(session.session_id, detailed_speech)

        # Now it should advance to Question 2 (Strengths & Weaknesses) in CORE_HR
        self.assertEqual(session.current_question_index, 1)
        self.assertEqual(advanced_turn.phase, InterviewPhase.CORE_HR)
        self.assertEqual(advanced_turn.question_id, "HR-STRENGTH-E-TECH-01")

    def test_06_conflict_avoidance_trigger(self):
        """Validates that avoiding conflict triggers a follow-up probe on culture fit questions."""
        q = self.bank.find_question(HRCategory.TEAMWORK_AND_CULTURE_FIT, ExperienceTier.EXPERIENCED, RoleTrack.TECHNICAL)
        self.assertIsNotNone(q)

        avoidance_response = "In my entire career, we never had any conflict at all, everything was always smooth and agreeable."
        needs_probe, reason = self.generator.evaluate_follow_up_eligibility(q, avoidance_response)
        self.assertTrue(needs_probe)
        self.assertEqual(reason, FollowUpTriggerReason.CONFLICT_AVOIDANCE)

        substantive_response = "When our team disagreed on adopting GraphQL versus REST, I organized a spike sprint where we benchmarked payload sizes and client caching, leading us to adopt GraphQL for mobile clients while keeping REST for external integrations."
        needs_probe_sub, reason_sub = self.generator.evaluate_follow_up_eligibility(q, substantive_response)
        self.assertFalse(needs_probe_sub)
        self.assertEqual(reason_sub, FollowUpTriggerReason.NONE)

    def test_07_end_to_end_phases_and_dossier_export(self):
        """Validates full progression across all 4 conversation phases to completion."""
        cfg = HRInterviewConfig.auto_classify("cand_t7", "Sneha Roy", "Software Engineer", 1.5)
        session = self.engine.start_session(cfg)

        responses = [
            # 1. Introduction
            "I graduated with honors in Computer Science and completed a six-month backend internship where I built asynchronous REST APIs using FastAPI.",
            # 2. Strengths & Weaknesses
            "My strength is rapid debugging and deep-diving into system logs. My weakness was public speaking, but I joined Toastmasters and now present sprint demos comfortably.",
            # 3. Teamwork & Culture
            "During our capstone project, when a teammate fell ill, I reallocated module responsibilities and pair-programmed with peers to ship the release on time.",
            # 4. Career Journey
            "The toughest problem was resolving a memory leak in our Celery background worker queues caused by unclosed database connections under high load.",
            # 5. Career Goals
            "Over the next three years, I want to become a core contributor to distributed systems and lead backend microservices architecture.",
            # 6. Availability & Commitment
            "I have already completed my graduation exams and I am available to join immediately with full commitment to the team.",
        ]

        expected_phases = [
            InterviewPhase.CORE_HR,                  # After Intro -> Core HR
            InterviewPhase.CORE_HR,                  # After Strengths -> Teamwork (still Core HR)
            InterviewPhase.ROLE_BASED_EVALUATION,    # After Teamwork -> Role Based
            InterviewPhase.CLOSING,                  # After Journey -> Closing (Goals)
            InterviewPhase.CLOSING,                  # After Goals -> Closing (Avail)
            InterviewPhase.CLOSING,                  # Final wrap-up terminal
        ]

        for i, resp in enumerate(responses):
            next_turn = self.engine.process_turn(session.session_id, candidate_response=resp)
            self.assertEqual(next_turn.phase, expected_phases[i])

        # Session should be marked completed
        self.assertTrue(session.is_completed)
        self.assertIsNotNone(session.completed_at)

        # Export Dossier
        dossier = self.engine.export_session_dossier(session.session_id)
        self.assertEqual(dossier["interview_status"], "COMPLETED")
        self.assertEqual(dossier["candidate_name"], "Sneha Roy")
        self.assertEqual(dossier["total_turns_conducted"], 6)
        self.assertEqual(len(dossier["categories_assessed"]), 6)
        self.assertTrue(dossier["average_response_words"] > 15)
        self.assertTrue(len(dossier["identified_themes"]) > 0)


if __name__ == "__main__":
    unittest.main()

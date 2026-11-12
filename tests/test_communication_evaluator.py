"""
Unit Tests for Day 35: Communication Skill Evaluation Engine
============================================================
Validates:
1. Fluency & sentence continuity (transition connectives, fragmentation, run-ons).
2. Grammar quality & agreement anti-patterns.
3. Vocabulary range & length-damped RTTR calculation.
4. Clarity of explanation & vagueness deductions.
5. Filler word detection & density decay scoring.
6. Answer structure analysis (STAR vs PREP frameworks).
7. Bias-reduction normalization (ESL fairness, length-invariance).
8. Full integration with HRInterviewFlowEngine & ATS dossier export.
"""

import unittest
from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    HRInterviewConfig,
)
from interview_ai.communication_evaluator import (
    FluencyAnalyzer,
    GrammarQualityAnalyzer,
    VocabularyAnalyzer,
    ClarityAnalyzer,
    FillerWordDetector,
    AnswerStructureAnalyzer,
    CommunicationEvaluator,
)
from interview_ai.hr_flow_engine import HRInterviewFlowEngine


class TestCommunicationEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = CommunicationEvaluator()
        self.fluency = FluencyAnalyzer()
        self.grammar = GrammarQualityAnalyzer()
        self.vocab = VocabularyAnalyzer()
        self.clarity = ClarityAnalyzer()
        self.fillers = FillerWordDetector()
        self.structure = AnswerStructureAnalyzer()
        self.flow_engine = HRInterviewFlowEngine()

    def test_01_fluency_and_sentence_continuity(self):
        """Verifies fluency scoring, transition connectors, and continuity."""
        # High fluency with transitions
        fluent_text = (
            "During our major system upgrade, our team faced high latency. "
            "Consequently, I refactored the database query layer. "
            "Furthermore, we added Redis caching to guarantee sub-millisecond lookups."
        )
        score_fluent, connectors, diag = self.fluency.analyze(fluent_text)
        self.assertTrue(score_fluent >= 85.0)
        self.assertIn("consequently", connectors)
        self.assertIn("furthermore", connectors)

        # Broken, fragmented speech with ellipses
        broken_text = "I did code... then it broke... um... fixed it maybe... not sure..."
        score_broken, _, _ = self.fluency.analyze(broken_text)
        self.assertTrue(score_broken < 60.0)

    def test_02_grammar_quality_analysis(self):
        """Validates grammatical agreement, anti-patterns, and punctuation health."""
        # Clean grammar
        clean_text = "I architected the microservice and resolved all concurrency bottlenecks."
        score_clean, errors, _ = self.grammar.analyze(clean_text)
        self.assertTrue(score_clean >= 90.0)
        self.assertEqual(len(errors), 0)

        # Anti-pattern: subject-verb mismatch and double negative
        bad_text = "we was working on it and we didn't had no tests."
        score_bad, errors_bad, _ = self.grammar.analyze(bad_text)
        self.assertTrue(score_bad <= 75.0)
        self.assertTrue(len(errors_bad) >= 1)

    def test_03_vocabulary_range_and_rttr(self):
        """Validates Root Type-Token Ratio and domain technical sophistication."""
        tech_text = (
            "I refactored the distributed pipeline using asynchronous message queues in Kafka "
            "to maximize throughput and minimize latency across our microservices."
        )
        score_tech, diag = self.vocab.analyze(tech_text, RoleTrack.TECHNICAL)
        self.assertTrue(score_tech >= 80.0)
        self.assertTrue(diag["rttr"] >= 3.8)
        self.assertTrue("throughput" in diag["matched_domain_terms"] or "latency" in diag["matched_domain_terms"])

        # Repetitive monotony text
        repetitive_text = "I did work. The work was big work. We like work and work was nice work every day."
        score_rep, _ = self.vocab.analyze(repetitive_text, RoleTrack.TECHNICAL)
        self.assertTrue(score_rep < 65.0)

    def test_04_clarity_and_vagueness_penalty(self):
        """Verifies content word density and vagueness hand-waving penalties."""
        clear_text = "We achieved an 85% branch test coverage before rolling out the release."
        score_clear, vague_clear, _ = self.clarity.analyze(clear_text)
        self.assertTrue(score_clear >= 85.0)
        self.assertEqual(len(vague_clear), 0)

        vague_text = "I basically did some backend stuff and all, kind of fixing things like that."
        score_vague, vague_hits, _ = self.clarity.analyze(vague_text)
        self.assertTrue(score_vague <= 65.0)
        self.assertTrue(len(vague_hits) >= 2)

    def test_05_filler_word_detection(self):
        """Validates filler word frequency counting and density decay scoring."""
        # Clean speech
        clean_text = "Our objective was to increase throughput while maintaining zero downtime."
        score_clean, fillers_clean, diag_clean = self.fillers.analyze(clean_text)
        self.assertEqual(score_clean, 100.0)
        self.assertEqual(diag_clean["total_fillers"], 0)

        # Filler-heavy text
        filler_text = "Um, so like, basically, you know, we had to, like, fix the server, um, quickly."
        score_fillers, fillers_dict, diag_fillers = self.fillers.analyze(filler_text)
        self.assertTrue(score_fillers <= 65.0)
        self.assertTrue(diag_fillers["total_fillers"] >= 4)
        self.assertIn("um", fillers_dict)
        self.assertIn("basically", fillers_dict)

    def test_06_answer_structure_star_and_prep(self):
        """Validates STAR and PREP structural alignment."""
        # Complete STAR answer
        star_text = (
            "When I was at my previous company, our core database was overloading under high load. "
            "My objective was to eliminate bottlenecks. "
            "I designed and implemented a Redis caching cluster. "
            "Which reduced database p99 latency by 45% and saved 20 hours of downtime."
        )
        score_star, framework, elements, _ = self.structure.analyze(star_text, HRCategory.CAREER_JOURNEY)
        self.assertEqual(framework, "STAR")
        self.assertTrue(score_star >= 90.0)
        self.assertIn("Situation", elements)
        self.assertIn("Task", elements)
        self.assertIn("Action", elements)
        self.assertIn("Result", elements)

        # Unstructured answer
        unstructured_text = "I like software development and I work on computers every day."
        score_unstructured, _, _, _ = self.structure.analyze(unstructured_text, HRCategory.CAREER_JOURNEY)
        self.assertTrue(score_unstructured <= 50.0)

    def test_07_bias_reduction_normalization(self):
        """Validates non-native English speaker fairness adjustment and length invariance."""
        # Non-native speaker with clean structure and high clarity, but simpler vocabulary
        esl_text = (
            "During my project, we faced very slow search performance. "
            "My goal was to make search fast. "
            "I implemented an index on the user database table. "
            "As a result, query time improved from two seconds to fifty milliseconds."
        )
        result = self.evaluator.evaluate(esl_text, HRCategory.CAREER_JOURNEY, RoleTrack.TECHNICAL)
        # Should achieve high normalized score despite simpler vocabulary
        self.assertTrue(result.normalized_score >= 82.0)
        self.assertTrue(result.structure_score >= 80.0)
        self.assertTrue(result.filler_score >= 90.0)

    def test_08_full_flow_engine_integration_and_ats_dossier(self):
        """Validates integration with HRInterviewFlowEngine, turn telemetry, and ATS export."""
        cfg = HRInterviewConfig.auto_classify(
            candidate_id="CAND-COMM-35",
            candidate_name="Priya Patel",
            job_role="Senior Full Stack Engineer",
            experience_years=5.0,
        )
        session = self.flow_engine.start_session(cfg)

        # Turn 1: Articulate, structured self-introduction
        self.flow_engine.process_turn(
            session.session_id,
            "Hello, thank you for having me. For the past five years, I have architected web applications. "
            "Furthermore, I led our migration to microservices, resulting in 40% faster deployment cycles.",
        )
        turn_1_evaluated = session.turns[0]
        self.assertIsNotNone(turn_1_evaluated.communication_score)
        self.assertTrue(turn_1_evaluated.communication_score.normalized_score >= 80.0)
        self.assertEqual(session.total_fillers_detected, 0)

        # Turn 2: Response with minor fillers
        self.flow_engine.process_turn(
            session.session_id,
            "Basically, my strength is debugging distributed systems. However, like, I sometimes spend too much time perfecting code.",
        )
        turn_2_evaluated = session.turns[1]
        self.assertIsNotNone(turn_2_evaluated.communication_score)
        self.assertTrue(session.total_fillers_detected >= 1)
        self.assertTrue(session.average_communication_score > 0.0)

        # Export ATS dossier
        dossier = self.flow_engine.export_session_dossier(session.session_id)
        self.assertIn("communication_summary", dossier)
        comm_summary = dossier["communication_summary"]
        self.assertTrue(comm_summary["average_score"] >= 70.0)
        self.assertIn(comm_summary["proficiency_tier"], ["Exceptional", "Proficient", "Developing"])
        self.assertEqual(len(dossier["turn_details"]), 3)
        self.assertIsNotNone(dossier["turn_details"][0]["communication_score"])


if __name__ == "__main__":
    unittest.main()

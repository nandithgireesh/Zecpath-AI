"""
Unit Tests for Day 47: Technical Skill Scoring Model
====================================================
Validates all Deliverables and Tasks for Day 47:
- Deliverable 1: Technical Scoring Engine (Accuracy, Depth, Reasoning, Applicability)
- Rubrics per question type (Conceptual, Experience, Scenario, System Design)
- Shallow vs Deep answer detection & buzzword penalty
- Difficulty-level score normalization & IRT latent ability theta
- Deliverable 2: Skill-wise scoring breakdown & proficiency tiers
- Deliverable 3: Standardized technical evaluation report format & explainability
"""

import unittest
import math

from tech_interview.blueprint import (
    JobRole,
    ExperienceTier,
    QuestionCategory,
    DifficultyLevel,
    BloomsTaxonomyLevel,
    CandidateProfile,
)
from tech_interview.question_hierarchy import (
    QuestionNode,
    CURATED_QUESTION_BANK,
)
from tech_interview.scoring_models import (
    ScoringParameter,
    AnswerDepthClassification,
    SkillProficiencyLevel,
    QuestionTypeRubric,
    QUESTION_TYPE_RUBRICS,
    ShallowAnswerDiagnostics,
    ParameterScoreBreakdown,
    NormalizedTurnScore,
    ExplainableScoringOutput,
    SkillDomainScore,
    TechnicalEvaluationReportFormat,
)
from tech_interview.scoring_engine import TechnicalSkillScoringEngine


class TestDay47TechnicalSkillScoring(unittest.TestCase):
    """Comprehensive test suite for Day 47 technical skill scoring engine."""

    @classmethod
    def setUpClass(cls):
        cls.engine = TechnicalSkillScoringEngine()
        cls.q_map = {q.question_id: q for q in CURATED_QUESTION_BANK}

    # ==========================================================================
    # 1. SCORING PARAMETERS & RUBRICS PER QUESTION TYPE
    # ==========================================================================

    def test_01_scoring_parameters_definition(self):
        """Verify the 4 core technical scoring parameters exist."""
        params = [p.value for p in ScoringParameter]
        self.assertIn("ACCURACY", params)
        self.assertIn("DEPTH", params)
        self.assertIn("LOGICAL_REASONING", params)
        self.assertIn("REAL_WORLD_APPLICABILITY", params)

    def test_02_question_type_rubric_weights_sum_to_one(self):
        """Verify that all calibrated rubrics sum strictly to 1.0."""
        for q_type, rubric in QUESTION_TYPE_RUBRICS.items():
            total = round(
                rubric.accuracy_weight +
                rubric.depth_weight +
                rubric.logical_reasoning_weight +
                rubric.real_world_applicability_weight,
                4
            )
            self.assertEqual(total, 1.0, f"Rubric for {q_type} does not sum to 1.0")

    def test_03_rubric_category_weight_priorities(self):
        """Verify that each question type prioritizes its core cognitive competency."""
        r_conceptual = QUESTION_TYPE_RUBRICS["CONCEPTUAL"]
        self.assertGreaterEqual(r_conceptual.accuracy_weight, 0.35)
        self.assertGreaterEqual(r_conceptual.depth_weight, 0.30)

        r_scenario = QUESTION_TYPE_RUBRICS["SCENARIO_BASED"]
        self.assertGreaterEqual(r_scenario.real_world_applicability_weight, 0.30)
        self.assertGreaterEqual(r_scenario.logical_reasoning_weight, 0.25)

        r_system_design = QUESTION_TYPE_RUBRICS["SYSTEM_DESIGN"]
        self.assertGreaterEqual(r_system_design.logical_reasoning_weight, 0.30)
        self.assertGreaterEqual(r_system_design.real_world_applicability_weight, 0.25)

    def test_04_invalid_rubric_weights_raise_value_error(self):
        """Verify that creating a rubric with weights not summing to 1.0 raises ValueError."""
        with self.assertRaises(ValueError):
            QuestionTypeRubric(
                accuracy_weight=0.5,
                depth_weight=0.5,
                logical_reasoning_weight=0.5,
                real_world_applicability_weight=0.5,
            )

    # ==========================================================================
    # 2. SHALLOW VS DEEP ANSWER DETECTION
    # ==========================================================================

    def test_05_shallow_buzzword_stuffed_answer_detection(self):
        """Verify that hollow buzzword dropping is detected as SHALLOW_SURFACE with penalties."""
        q = self.q_map["Q-JAVA-CONC-01"]  # JVM Memory layout
        shallow_answer = (
            "We use microservices, scalable cloud, redis, kafka, docker, and agile architecture. "
            "It is very fast, efficient, robust, modern, performant, and scalable."
        )
        diag = self.engine.analyze_answer_depth(shallow_answer, q)

        self.assertEqual(diag.depth_classification, AnswerDepthClassification.SHALLOW_SURFACE)
        self.assertGreaterEqual(diag.buzzword_density, 0.70)
        self.assertGreater(len(diag.detected_buzzwords_without_context), 0)
        self.assertEqual(len(diag.mechanisms_explained), 0)
        self.assertLess(diag.depth_index, 0.30)
        self.assertGreater(diag.shallow_penalty_applied, 0.0)

    def test_06_circular_definition_detection(self):
        """Verify circular definitions trigger is_circular_definition and penalties."""
        q = self.q_map["Q-JAVA-EXP-01"]  # Spring Data JPA & Hibernate Caching
        # Sub-skill is "Spring Data JPA & Hibernate Caching"
        circular_answer = "Hibernate caching is when hibernate does caching in memory."
        diag = self.engine.analyze_answer_depth(circular_answer, q)

        self.assertTrue(diag.is_circular_definition)
        self.assertGreaterEqual(diag.shallow_penalty_applied, 0.25)

    def test_07_deep_mechanical_explanation_detection(self):
        """Verify deep answer with internal runtime mechanisms and trade-offs is classified as DEEP/EXPERT."""
        q = self.q_map["Q-JAVA-CONC-01"]  # JVM Memory Layout
        deep_answer = (
            "JVM memory layout separates Thread Stacks from Heap and Metaspace. Instantiated objects allocate "
            "into the Young Generation's Eden space. During minor garbage collection, active surviving objects "
            "copy into Survivor spaces (S0/S1). When an object's age exceeds the tenuring threshold, it is promoted "
            "into the Old Generation. While Metaspace expands natively, unconstrained thread pool spawning risks "
            "native memory exhaustion at the cost of high throughput."
        )
        diag = self.engine.analyze_answer_depth(deep_answer, q)

        self.assertIn(diag.depth_classification, [
            AnswerDepthClassification.DEEP_ANALYTICAL,
            AnswerDepthClassification.EXPERT_ARCHITECTURAL
        ])
        self.assertGreaterEqual(diag.depth_index, 0.55)
        self.assertGreaterEqual(len(diag.mechanisms_explained), 3)
        self.assertGreaterEqual(len(diag.tradeoffs_defended), 1)
        self.assertEqual(diag.shallow_penalty_applied, 0.0)

    def test_08_concrete_engineering_metrics_detection(self):
        """Verify detection of production metrics (latencies, sizes, TPS, exit codes)."""
        q = self.q_map["Q-DEVOPS-SCEN-01"]  # K8s CrashLoopBackOff & OOMKill
        answer_with_metrics = (
            "I checked kubectl describe pod exit code 137, which confirmed an OS SIGKILL from cgroups memory pressure. "
            "Container memory requests were set to 512MB while limits were 1GB. API latency was spiking past 450ms P99 "
            "under 15,000 TPS traffic. We performed a rollback and adjusted limits to 2GB with RTO < 5 min."
        )
        diag = self.engine.analyze_answer_depth(answer_with_metrics, q)

        self.assertGreaterEqual(len(diag.concrete_metrics_cited), 3)
        self.assertGreaterEqual(len(diag.mechanisms_explained), 2)
        self.assertIn(diag.depth_classification, [
            AnswerDepthClassification.DEEP_ANALYTICAL,
            AnswerDepthClassification.EXPERT_ARCHITECTURAL
        ])

    # ==========================================================================
    # 3. FOUR-FACTOR PARAMETER SCORING ENGINE
    # ==========================================================================

    def test_09_parameter_scores_calculation(self):
        """Verify accurate calculation of the 4 parameters and rubric weighting."""
        q = self.q_map["Q-MERN-CONC-01"]  # Node.js Event Loop (Conceptual)
        ans = (
            "Node.js event loop runs on a single thread utilizing libuv. When synchronous CPU tasks run on the "
            "call stack, they block the event loop timers and poll phases. Asynchronous network I/O is offloaded "
            "to the libuv thread pool. In exchange for non-blocking I/O throughput, CPU-heavy operations must be "
            "delegated to worker threads to avoid latency spikes."
        )
        diag = self.engine.analyze_answer_depth(ans, q)
        scores = self.engine.calculate_parameter_scores(ans, q, diag)

        self.assertIsInstance(scores, ParameterScoreBreakdown)
        self.assertGreaterEqual(scores.accuracy, 0.70)
        self.assertGreaterEqual(scores.depth, 0.60)
        self.assertGreaterEqual(scores.logical_reasoning, 0.60)
        self.assertGreaterEqual(scores.real_world_applicability, 0.50)
        self.assertGreaterEqual(scores.weighted_composite_raw, 0.65)

    # ==========================================================================
    # 4. DIFFICULTY-LEVEL SCORE NORMALIZATION & IRT THETA
    # ==========================================================================

    def test_10_difficulty_normalization_curves(self):
        """Verify that identical raw scores scale properly across difficulty levels 1 to 5."""
        raw = 0.80

        norm_l1 = self.engine.normalize_score(raw, DifficultyLevel.L1_BASIC, ExperienceTier.JUNIOR_0_2_YRS)
        norm_l3 = self.engine.normalize_score(raw, DifficultyLevel.L3_INTERMEDIATE, ExperienceTier.MID_3_5_YRS)
        norm_l5 = self.engine.normalize_score(raw, DifficultyLevel.L5_SYSTEM_DESIGN, ExperienceTier.SENIOR_5_PLUS_YRS)

        self.assertEqual(norm_l1.difficulty_weight_multiplier, 0.90)
        self.assertEqual(norm_l3.difficulty_weight_multiplier, 1.00)
        self.assertEqual(norm_l5.difficulty_weight_multiplier, 1.18)

        # Higher difficulty must yield higher normalized points for identical performance
        self.assertLess(norm_l1.normalized_score, norm_l3.normalized_score)
        self.assertLess(norm_l3.normalized_score, norm_l5.normalized_score)

        # Clamping check: Normalized score must never exceed 100.0
        norm_high = self.engine.normalize_score(0.95, DifficultyLevel.L5_SYSTEM_DESIGN, ExperienceTier.SENIOR_5_PLUS_YRS)
        self.assertLessEqual(norm_high.normalized_score, 100.0)

    def test_11_irt_proficiency_theta_monotonicity(self):
        """Verify Item Response Theory latent ability theta increases with raw score and difficulty."""
        t1 = self.engine.normalize_score(0.40, DifficultyLevel.L2_FOUNDATIONAL, ExperienceTier.JUNIOR_0_2_YRS)
        t2 = self.engine.normalize_score(0.85, DifficultyLevel.L2_FOUNDATIONAL, ExperienceTier.JUNIOR_0_2_YRS)
        t3 = self.engine.normalize_score(0.85, DifficultyLevel.L5_SYSTEM_DESIGN, ExperienceTier.SENIOR_5_PLUS_YRS)

        self.assertLess(t1.irt_proficiency_theta, t2.irt_proficiency_theta)
        self.assertLess(t2.irt_proficiency_theta, t3.irt_proficiency_theta)

    # ==========================================================================
    # 5. EXPLAINABLE SCORING OUTPUTS & COUNTERFACTUALS
    # ==========================================================================

    def test_12_explainable_scoring_output_generation(self):
        """Verify explainable scoring output contains justifications and counterfactual guidance."""
        q = self.q_map["Q-DEVOPS-CONC-01"]  # Docker Multi-stage Builds
        ans = (
            "Multi-stage Docker builds separate build tools from runtime containers. We compile binaries in stage 1 "
            "and copy only the executable into distroless in stage 2, reducing container size from 1.2GB to 45MB "
            "and slashing CVE attack surfaces."
        )
        diag = self.engine.analyze_answer_depth(ans, q)
        params = self.engine.calculate_parameter_scores(ans, q, diag)
        norm = self.engine.normalize_score(params.weighted_composite_raw, q.difficulty, q.experience_tier)
        output = self.engine.build_explainable_output(1, q, params, diag, norm)

        self.assertIsInstance(output, ExplainableScoringOutput)
        self.assertEqual(output.question_id, q.question_id)
        self.assertIn("Multi-stage", output.justification_summary)
        self.assertGreater(len(output.positive_technical_evidence), 0)
        self.assertIsNotNone(output.counterfactual_guidance)

    # ==========================================================================
    # 6. SKILL-WISE SCORING BREAKDOWN (DELIVERABLE 2) & REPORT FORMAT (DELIVERABLE 3)
    # ==========================================================================

    def test_13_skill_wise_breakdown_and_report_format(self):
        """Verify complete synthesis of skill-wise breakdown and standardized report format."""
        profile = CandidateProfile(
            candidate_id="CAND-TEST-47",
            target_role=JobRole.JAVA_BACKEND,
            years_experience=4.5,
        )

        # Simulate 3 turns across Java skills
        test_data = [
            ("Q-JAVA-INT-01", "I have 4.5 years developing Spring Boot services with PostgreSQL and Kafka, building high-throughput payment architectures in production."),
            ("Q-JAVA-CONC-01", "JVM divides memory into Heap, Metaspace, and Thread Stacks. Minor GC clears Eden space while tenured objects move to Old Generation. Concurrency locks prevent race conditions."),
            ("Q-JAVA-EXP-01", "We resolved Hibernate N+1 selects using JOIN FETCH and EntityGraphs, profiling query counts with Hibernate statistics logs under 5000 TPS load."),
        ]

        turn_outputs = []
        questions = []
        for idx, (qid, ans) in enumerate(test_data, start=1):
            q = self.q_map[qid]
            questions.append(q)
            diag = self.engine.analyze_answer_depth(ans, q)
            params = self.engine.calculate_parameter_scores(ans, q, diag)
            norm = self.engine.normalize_score(params.weighted_composite_raw, q.difficulty, q.experience_tier)
            exp = self.engine.build_explainable_output(idx, q, params, diag, norm)
            turn_outputs.append(exp)

        report = self.engine.synthesize_evaluation_report(
            candidate_profile=profile,
            session_id="SESS-TEST-DAY47",
            turn_outputs=turn_outputs,
            question_nodes=questions,
        )

        self.assertIsInstance(report, TechnicalEvaluationReportFormat)
        self.assertEqual(report.candidate_id, "CAND-TEST-47")
        self.assertGreater(report.final_technical_score, 50.0)
        self.assertIn(report.hiring_recommendation, ["STRONG_HIRE", "LEAN_HIRE", "BORDERLINE"])

        # Check Deliverable 2: Skill-wise Breakdown
        self.assertGreaterEqual(len(report.skill_domain_breakdown), 2)
        for dom in report.skill_domain_breakdown:
            self.assertIsInstance(dom, SkillDomainScore)
            self.assertGreater(dom.difficulty_weighted_score, 0.0)
            self.assertIn(dom.proficiency_level, [
                SkillProficiencyLevel.COMPETENT,
                SkillProficiencyLevel.PROFICIENT,
                SkillProficiencyLevel.ADVANCED,
                SkillProficiencyLevel.EXPERT,
            ])
            self.assertIn("ACCURACY", dom.parameter_averages)
            self.assertIn("DEPTH", dom.parameter_averages)
            self.assertIn("LOGICAL_REASONING", dom.parameter_averages)
            self.assertIn("REAL_WORLD_APPLICABILITY", dom.parameter_averages)

        # Check Deliverable 3: Report Format Components
        self.assertIn("ACCURACY", report.parameter_aggregate_scores)
        self.assertIn("DEPTH", report.parameter_aggregate_scores)
        self.assertGreater(len(report.key_strengths), 0)
        self.assertGreater(len(report.counterfactual_improvement_plan), 0)
        self.assertIn("eu_ai_act_article_13", report.regulatory_compliance_attestation)

    # ==========================================================================
    # 7. EDGE CASES & SAFETY INVARIANTS
    # ==========================================================================

    def test_14_empty_answer_handling(self):
        """Verify empty answer scores minimum baseline without crashing."""
        q = self.q_map["Q-MERN-EXP-01"]
        diag = self.engine.analyze_answer_depth("", q)
        params = self.engine.calculate_parameter_scores("", q, diag)
        norm = self.engine.normalize_score(params.weighted_composite_raw, q.difficulty, q.experience_tier)

        self.assertEqual(diag.depth_classification, AnswerDepthClassification.SHALLOW_SURFACE)
        self.assertLessEqual(params.accuracy, 0.20)
        self.assertLessEqual(params.depth, 0.10)
        self.assertLessEqual(norm.normalized_score, 25.0)

    def test_15_empty_turn_outputs_raises_value_error(self):
        """Verify attempting to synthesize report with empty turns raises ValueError."""
        profile = CandidateProfile(candidate_id="CAND-EMPTY", target_role=JobRole.DEVOPS_CLOUD, years_experience=2.0)
        with self.assertRaises(ValueError):
            self.engine.synthesize_evaluation_report(profile, "SESS-EMPTY", [], [])


if __name__ == "__main__":
    unittest.main()

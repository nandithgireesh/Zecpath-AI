"""
Day 38 Unit Tests: Aptitude Logic Design & Scenario Evaluation Framework
========================================================================
Validates all 3 deliverables:
- Deliverable 1: Aptitude AI Design (AptitudeAIEngine, scenario banks, question taxonomy)
- Deliverable 2: Logical Reasoning Scoring Model (LogicalReasoningScorer, causal chains, fallacies)
- Deliverable 3: Scenario Evaluation Framework (ScenarioEvaluator, ProblemSolvingClarityAnalyzer, IDEA adherence)
"""

import unittest
from interview_ai.aptitude_models import (
    CognitiveDimension,
    ScenarioCategory,
    CognitiveMaturityLevel,
    FrameworkType,
    SituationalScenario,
)
from interview_ai.logical_reasoning_scorer import LogicalReasoningScorer
from interview_ai.scenario_evaluator import (
    ProblemSolvingClarityAnalyzer,
    ScenarioEvaluator,
)
from interview_ai.aptitude_engine import AptitudeAIEngine
from interview_ai.hr_models import RoleTrack


class TestAptitudeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AptitudeAIEngine()
        self.logic_scorer = LogicalReasoningScorer()
        self.clarity_analyzer = ProblemSolvingClarityAnalyzer()
        self.scenario_evaluator = ScenarioEvaluator()

    # =========================================================================
    # Deliverable 2: Logical Reasoning Scoring Tests
    # =========================================================================

    def test_logical_reasoning_high_rigor(self):
        """Asserts methodical deductive response with trade-offs scores high (>=80)."""
        response = (
            "The core issue is that low CPU alongside high latency indicates an I/O bottleneck rather than "
            "compute starvation. Assuming that our connection pool is exhausted, the thread pool blocks because "
            "incoming queries cannot acquire a database handle. Therefore, as a result of lock contention, "
            "requests queue up, which causes p99 latency to spike. On one hand, scaling out web servers might "
            "seem attractive, but the downside is that it exacerbates connection saturation on the database. "
            "Alternatively, enabling aggressive query timeouts and tuning connection pools provides a balanced "
            "trade-off between throughput and transaction stability."
        )
        scenario = self.engine.get_scenario("SJT_INCIDENT_01")
        breakdown = self.logic_scorer.evaluate(response, scenario)

        self.assertGreaterEqual(breakdown.premise_identification_score, 70.0)
        self.assertGreaterEqual(breakdown.causal_inference_score, 75.0)
        self.assertGreaterEqual(breakdown.tradeoff_depth_score, 75.0)
        self.assertEqual(breakdown.fallacy_deductions, 0.0)
        self.assertEqual(len(breakdown.detected_fallacies), 0)
        self.assertGreaterEqual(breakdown.calibrated_logic_score, 80.0)

    def test_logical_reasoning_false_dilemma_fallacy(self):
        """Asserts artificial black-and-white framing triggers FALSE_DILEMMA deduction."""
        response = (
            "We have no choice but to immediately restart the entire database cluster, because either we do that "
            "or everything dies right now. There is no other way to resolve this latency."
        )
        breakdown = self.logic_scorer.evaluate(response)
        self.assertGreater(breakdown.fallacy_deductions, 0.0)
        self.assertTrue(any("FALSE_DILEMMA" in f for f in breakdown.detected_fallacies))
        self.assertLess(breakdown.calibrated_logic_score, 60.0)

    def test_logical_reasoning_hasty_conclusion_fallacy(self):
        """Asserts extreme untested recommendations trigger HASTY_CONCLUSION deduction."""
        response = (
            "The architecture is flawed. We should just rewrite the whole system in Go and fire the developer "
            "who deployed that migration."
        )
        breakdown = self.logic_scorer.evaluate(response)
        self.assertGreater(breakdown.fallacy_deductions, 0.0)
        self.assertTrue(any("HASTY_CONCLUSION" in f for f in breakdown.detected_fallacies))

    def test_logical_reasoning_blame_deflection_fallacy(self):
        """Asserts deflecting ownership triggers BLAME_DEFLECTION deduction."""
        response = (
            "This outage is not my problem because management's fault was forcing us to release too early. "
            "The pm messed up the schedule."
        )
        breakdown = self.logic_scorer.evaluate(response)
        self.assertGreater(breakdown.fallacy_deductions, 0.0)
        self.assertTrue(any("BLAME_DEFLECTION" in f for f in breakdown.detected_fallacies))

    # =========================================================================
    # Deliverable 3: Problem-Solving Clarity & Scenario Evaluator Tests
    # =========================================================================

    def test_problem_solving_clarity_signposting(self):
        """Asserts sequential milestone markers ('first... second... finally') award high clarity."""
        response = (
            "First, I will isolate the failure domain by checking our Grafana error rates. "
            "Secondly, I will deploy a hotfix feature flag to disable the offending checkout module. "
            "Thirdly, we will coordinate with customer support to update the status page. "
            "Finally, once traffic stabilizes, we will conduct a blameless post-mortem."
        )
        breakdown = self.clarity_analyzer.analyze(response)
        self.assertGreaterEqual(breakdown.structural_signposting_score, 85.0)
        self.assertGreaterEqual(breakdown.decisiveness_score, 80.0)
        self.assertGreaterEqual(breakdown.calibrated_clarity_score, 75.0)

    def test_problem_solving_clarity_hedging_penalty(self):
        """Asserts non-committal hedging reduces decisiveness."""
        response = "Maybe we could check something, or I guess someone might work on it, but I am really not sure."
        breakdown = self.clarity_analyzer.analyze(response)
        self.assertLess(breakdown.decisiveness_score, 50.0)

    def test_situational_effectiveness_optimal_actions(self):
        """Asserts matching scenario-specific optimal actions awards high effectiveness."""
        scenario = self.engine.get_scenario("SJT_INCIDENT_01")
        response = (
            "First, I will isolate failure domain and enable feature flag to redirect traffic to standby queue. "
            "Next, we will communicate transparently on status bridge and conduct a thorough post-mortem analysis."
        )
        result = self.scenario_evaluator.evaluate_scenario(scenario, response)
        self.assertGreaterEqual(result.situational_effectiveness_score, 80.0)
        self.assertGreaterEqual(len(result.observed_strengths), 1)

    def test_situational_effectiveness_high_risk_actions(self):
        """Asserts adopting anti-patterns incurs severe penalties and generates risk flags."""
        scenario = self.engine.get_scenario("SJT_INCIDENT_01")
        response = (
            "I would force restart production database without backup and ignore customer error rates to keep ads running."
        )
        result = self.scenario_evaluator.evaluate_scenario(scenario, response)
        self.assertLess(result.situational_effectiveness_score, 50.0)
        self.assertTrue(any("Anti-pattern identified" in flag for flag in result.cognitive_flags))

    def test_risk_mitigation_and_stakeholder_scores(self):
        """Asserts safeguards, telemetry, and stakeholder communication are accurately scored."""
        scenario = self.engine.get_scenario("SJT_ETHICAL_01")
        response = (
            "I will implement an immediate regex filter and rollback configuration, ensuring telemetry monitoring "
            "and circuit breakers are active. Simultaneously, I will communicate transparently with the client, "
            "inform leadership, and align expectations with our compliance stakeholder."
        )
        result = self.scenario_evaluator.evaluate_scenario(scenario, response)
        self.assertGreaterEqual(result.risk_mitigation_score, 80.0)
        self.assertGreaterEqual(result.stakeholder_awareness_score, 80.0)

    def test_framework_adherence_idea(self):
        """Asserts completion of IDEA framework milestones."""
        scenario = self.engine.get_scenario("SJT_INCIDENT_01")
        response = (
            "The core conflict is transaction failure. The constraint is irreversible migration. "
            "Evaluating option A versus option B, I will toggle the feature flag and lead the root-cause post-mortem."
        )
        result = self.scenario_evaluator.evaluate_scenario(scenario, response)
        self.assertGreater(result.framework_adherence_percent, 50.0)

    # =========================================================================
    # Deliverable 1: Aptitude AI Design & Orchestration Tests
    # =========================================================================

    def test_aptitude_engine_role_routing(self):
        """Asserts role tracks route to appropriate representative scenarios."""
        tech_sjt = self.engine.get_recommended_scenario_for_role(RoleTrack.TECHNICAL)
        self.assertEqual(tech_sjt.scenario_id, "SJT_INCIDENT_01")
        self.assertEqual(tech_sjt.category, ScenarioCategory.SYSTEM_INCIDENT_ESCALATION)

        non_tech_sjt = self.engine.get_recommended_scenario_for_role(RoleTrack.NON_TECHNICAL)
        self.assertEqual(non_tech_sjt.scenario_id, "SJT_STAKEHOLDER_01")
        self.assertEqual(non_tech_sjt.category, ScenarioCategory.STAKEHOLDER_CONFLICT)

    def test_cognitive_maturity_levels(self):
        """Asserts correct deterministic classification into CognitiveMaturityLevel tiers."""
        scenario = self.engine.get_scenario("SJT_INCIDENT_01")
        
        # High maturity response
        exemplary_resp = (
            "First, we must identify the root cause by inspecting database connection pool saturation. "
            "Because 40% of checkouts are failing, incoming queries queue up, resulting in latency cascading downstream. "
            "Given the constraint that schema migrations cannot be cleanly rolled back, our trade-off is between "
            "shedding load or graceful degradation. I will enable a feature flag to bypass non-critical checkout features, "
            "redirect traffic to standby queue, communicate transparently on the incident bridge, and establish "
            "monitoring telemetry with automated circuit breakers."
        )
        result_high = self.scenario_evaluator.evaluate_scenario(scenario, exemplary_resp)
        self.assertIn(result_high.cognitive_maturity, [CognitiveMaturityLevel.EXEMPLARY, CognitiveMaturityLevel.PROFICIENT])
        self.assertGreaterEqual(result_high.composite_aptitude_score, 70.0)

        # Deficient response
        bad_resp = "Just fire the engineer. Not my problem anyway. The only option is restart."
        result_low = self.scenario_evaluator.evaluate_scenario(scenario, bad_resp)
        self.assertEqual(result_low.cognitive_maturity, CognitiveMaturityLevel.DEFICIENT)
        self.assertLess(result_low.composite_aptitude_score, 45.0)


if __name__ == "__main__":
    unittest.main()

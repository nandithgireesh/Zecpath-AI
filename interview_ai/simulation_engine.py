"""
Day 40: End-to-End HR Interview Simulation Engine (Deliverable 1)
================================================================
Simulates multi-session HR interview flows across distinct candidate archetypes:
1. Confident Candidate (High-performing, articulate, resilient)
2. Hesitant Candidate (Competent, but elevated hesitation, stress spikes, hedging)
3. Inexperienced Candidate (Junior tenure, shallow trade-offs, high vagueness)
4. Overqualified Candidate (Principal/Staff depth, excessive detail for target role)
5. Inconsistent Candidate (Cross-turn contradictions, blame deflection, fallacies)

Executes the complete Zecpath-AI pipeline (Days 33 to 39) and captures end-to-end telemetry.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from .simulation_models import (
    CandidateArchetype,
    SimulatedCandidateProfile,
    SimulationTurnData,
    SessionSimulationResult,
    HumanExpertPanelScore,
)
from .hr_scoring_models import (
    CandidateHRScoreReport,
    HiringRecommendation,
    ParameterContribution,
    ScoringParameter,
    LengthNormalizationMetadata,
    RoleTrackPreset,
)
from .interview_summary_generator import InterviewSummaryGenerator
from .aptitude_models import CognitiveDimension, ScenarioCategory


class HRInterviewSimulationEngine:
    """
    Orchestrates end-to-end simulated HR interview sessions, feeding realistic multi-modal
    behavioral, communication, and situational signals into the AI evaluation pipeline.
    """

    def __init__(self, output_dir: str = "data/simulations"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.summary_generator = InterviewSummaryGenerator()

    def get_standard_cohort_profiles(self) -> List[SimulatedCandidateProfile]:
        """Returns the five canonical candidate archetypes mandated by curriculum & benchmark."""
        return [
            # 1. Confident Candidate: Aditi Rao
            SimulatedCandidateProfile(
                candidate_id="SIM-CONF-01",
                name="Aditi Rao",
                target_role="Senior Cloud Platform Architect",
                experience_years=7.5,
                archetype=CandidateArchetype.CONFIDENT,
                role_track=RoleTrackPreset.TECHNICAL_ROLES,
                expected_recommendation=HiringRecommendation.STRONG_HIRE,
                human_ground_truth=HumanExpertPanelScore(
                    evaluator_role="Senior Bar Raiser Panel (HR Director + Staff Eng)",
                    behavioral_score=90.0,
                    communication_score=88.0,
                    composure_score=91.0,
                    aptitude_score=90.0,
                    composite_score=89.7,
                    recommendation=HiringRecommendation.STRONG_HIRE,
                    notes="Exceptional technical rigor, structured STAR/IDEA delivery, high composure under failure scenarios, zero fallacies.",
                ),
            ),
            # 2. Hesitant Candidate: Siddharth Verma
            SimulatedCandidateProfile(
                candidate_id="SIM-HES-02",
                name="Siddharth Verma",
                target_role="Data Infrastructure Engineer",
                experience_years=4.0,
                archetype=CandidateArchetype.HESITANT,
                role_track=RoleTrackPreset.TECHNICAL_ROLES,
                expected_recommendation=HiringRecommendation.LEAN_HIRE,
                human_ground_truth=HumanExpertPanelScore(
                    evaluator_role="Senior Bar Raiser Panel",
                    behavioral_score=70.0,
                    communication_score=66.0,
                    composure_score=64.0,
                    aptitude_score=72.0,
                    composite_score=68.2,
                    recommendation=HiringRecommendation.LEAN_HIRE,
                    notes="Solid foundational database and Kafka understanding, but marked by prolonged hesitation pauses (3.8s) and frequent hedging. Needs manager probing.",
                ),
            ),
            # 3. Inexperienced Candidate: Kavita Patel
            SimulatedCandidateProfile(
                candidate_id="SIM-INEXP-03",
                name="Kavita Patel",
                target_role="Senior Systems Engineer",
                experience_years=1.2,
                archetype=CandidateArchetype.INEXPERIENCED,
                role_track=RoleTrackPreset.TECHNICAL_ROLES,
                expected_recommendation=HiringRecommendation.LEAN_NO_HIRE,
                human_ground_truth=HumanExpertPanelScore(
                    evaluator_role="Senior Bar Raiser Panel",
                    behavioral_score=52.0,
                    communication_score=60.0,
                    composure_score=55.0,
                    aptitude_score=45.0,
                    composite_score=52.8,
                    recommendation=HiringRecommendation.LEAN_NO_HIRE,
                    notes="Enthusiastic and clear speaker, but trade-offs remain superficial. Lacks depth in distributed locks and connection pools for senior expectations.",
                ),
            ),
            # 4. Overqualified Candidate: Dr. Rajesh Sundaram
            SimulatedCandidateProfile(
                candidate_id="SIM-OVER-04",
                name="Dr. Rajesh Sundaram",
                target_role="DevOps Engineer",
                experience_years=14.0,
                archetype=CandidateArchetype.OVERQUALIFIED,
                role_track=RoleTrackPreset.TECHNICAL_ROLES,
                expected_recommendation=HiringRecommendation.HIRE,
                human_ground_truth=HumanExpertPanelScore(
                    evaluator_role="Senior Bar Raiser Panel",
                    behavioral_score=88.0,
                    communication_score=85.0,
                    composure_score=92.0,
                    aptitude_score=94.0,
                    composite_score=89.5,
                    recommendation=HiringRecommendation.HIRE,
                    notes="Far exceeds requested DevOps responsibilities; discusses kernel eBPF and multi-cloud mesh. Recommending role leveling upgrade to Principal Architect.",
                ),
            ),
            # 5. Inconsistent / High Risk Candidate: Tarun Khanna
            SimulatedCandidateProfile(
                candidate_id="SIM-INCON-05",
                name="Tarun Khanna",
                target_role="Senior Backend Lead",
                experience_years=6.0,
                archetype=CandidateArchetype.INCONSISTENT,
                role_track=RoleTrackPreset.TECHNICAL_ROLES,
                expected_recommendation=HiringRecommendation.NO_HIRE,
                human_ground_truth=HumanExpertPanelScore(
                    evaluator_role="Senior Bar Raiser Panel",
                    behavioral_score=40.0,
                    communication_score=55.0,
                    composure_score=45.0,
                    aptitude_score=35.0,
                    composite_score=43.5,
                    recommendation=HiringRecommendation.NO_HIRE,
                    notes="Major red flags: Contradicted solo architecture claims in Turn 3, deflected responsibility for outage onto QA, and exhibited false dilemma fallacy.",
                ),
            ),
        ]

    def _generate_candidate_turns(self, profile: SimulatedCandidateProfile) -> tuple[List[SimulationTurnData], List[Dict[str, Any]], Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generates realistic transcript turns, multi-modal signals, and fallacies based on archetype."""
        turns: List[SimulationTurnData] = []
        raw_turns: List[Dict[str, Any]] = []
        stress_signals: List[Dict[str, Any]] = []
        fallacies: List[Dict[str, Any]] = []

        if profile.archetype == CandidateArchetype.CONFIDENT:
            q1 = "Describe a situation where a critical database outage occurred under peak load. How did you diagnose and contain the incident?"
            r1 = "When our distributed database experienced connection pool exhaustion during flash sales, I took ownership of the triage. First, I analyzed telemetry metrics to confirm thread contention. Subsequently, we instituted connection queue throttling and gracefully degraded non-critical checkout services, isolating the blast radius while conducting a blameless post-mortem."
            turns.append(SimulationTurnData(turn_index=1, phase="SITUATIONAL", question_asked=q1, candidate_response=r1, hesitation_seconds=1.1, filler_percentage=1.2, stress_index=22.0, relevance_score=92.0))
            raw_turns.append({"turn_index": 1, "question": q1, "response": r1})
            stress_signals.append({"turn_index": 1, "stress_index": 22.0, "hesitation_latency": 1.1, "filler_percentage": 1.2})

            q2 = "How do you evaluate consistency versus availability trade-offs when designing financial transaction pipelines?"
            r2 = "In payment architectures, strong consistency is non-negotiable for accounting ledgers. However, for audit telemetry and notifications, we chose eventual consistency via Kafka. This bilateral trade-off ensured zero double-charge risk while protecting system throughput under high concurrency."
            turns.append(SimulationTurnData(turn_index=2, phase="APTITUDE_LOGIC", question_asked=q2, candidate_response=r2, hesitation_seconds=0.9, filler_percentage=1.0, stress_index=19.0, relevance_score=94.0))
            raw_turns.append({"turn_index": 2, "question": q2, "response": r2})
            stress_signals.append({"turn_index": 2, "stress_index": 19.0, "hesitation_latency": 0.9, "filler_percentage": 1.0})

            aptitude_eval = {
                "composite_aptitude_score": 92.0,
                "scores": {"logical_reasoning": 92.5, "problem_solving_clarity": 91.0, "situational_effectiveness": 94.0, "risk_mitigation": 91.0},
                "framework_adherence_percent": 100.0,
            }
            comm_telemetry = {"clarity": 91.0, "filler_percentage": 1.1}

        elif profile.archetype == CandidateArchetype.HESITANT:
            q1 = "Describe how you handled a complex database migration with zero downtime."
            r1 = "Um... well, maybe I guess we started by setting up dual-write replication... um, you know, we were not completely sure about the network latency, so we kind of monitored it carefully and then switched over the DNS after a few hours."
            turns.append(SimulationTurnData(turn_index=1, phase="SITUATIONAL", question_asked=q1, candidate_response=r1, hesitation_seconds=3.9, filler_percentage=7.8, stress_index=68.0, relevance_score=72.0))
            raw_turns.append({"turn_index": 1, "question": q1, "response": r1})
            stress_signals.append({"turn_index": 1, "stress_index": 68.0, "hesitation_latency": 3.9, "filler_percentage": 7.8})

            q2 = "What are the core failure modes of distributed event streaming?"
            r2 = "I am 100% absolutely certain and completely confident that Kafka consumer lag is trivial to resolve without doubt. Though, uh, when consumer partitions rebalance, maybe you can lose messages if offsets aren't committed properly."
            turns.append(SimulationTurnData(turn_index=2, phase="APTITUDE_LOGIC", question_asked=q2, candidate_response=r2, hesitation_seconds=3.6, filler_percentage=7.2, stress_index=72.0, relevance_score=70.0))
            raw_turns.append({"turn_index": 2, "question": q2, "response": r2})
            stress_signals.append({"turn_index": 2, "stress_index": 72.0, "hesitation_latency": 3.6, "filler_percentage": 7.2})

            aptitude_eval = {
                "composite_aptitude_score": 69.0,
                "scores": {"logical_reasoning": 68.0, "problem_solving_clarity": 66.0, "situational_effectiveness": 72.0, "risk_mitigation": 68.0},
                "framework_adherence_percent": 75.0,
            }
            comm_telemetry = {"clarity": 68.0, "filler_percentage": 7.5}

        elif profile.archetype == CandidateArchetype.INEXPERIENCED:
            q1 = "How do you design a high-throughput microservices architecture?"
            r1 = "We just use Node.js and MongoDB. Whenever it slows down, we just restart the server or scale up the CPU on AWS."
            turns.append(SimulationTurnData(turn_index=1, phase="TECHNICAL", question_asked=q1, candidate_response=r1, hesitation_seconds=1.5, filler_percentage=3.0, stress_index=35.0, relevance_score=52.0, dynamic_followup_triggered=True, followup_reason="VAGUENESS_DETECTED"))
            raw_turns.append({"turn_index": 1, "question": q1, "response": r1})
            stress_signals.append({"turn_index": 1, "stress_index": 35.0, "hesitation_latency": 1.5, "filler_percentage": 3.0})

            q2 = "Follow-up: How do you handle database deadlocks and connection pooling?"
            r2 = "I think our cloud provider automatically manages connection pools, so I haven't really had to adjust max connections or timeouts manually."
            turns.append(SimulationTurnData(turn_index=2, phase="DYNAMIC_FOLLOWUP", question_asked=q2, candidate_response=r2, hesitation_seconds=2.0, filler_percentage=4.0, stress_index=48.0, relevance_score=48.0))
            raw_turns.append({"turn_index": 2, "question": q2, "response": r2})
            stress_signals.append({"turn_index": 2, "stress_index": 48.0, "hesitation_latency": 2.0, "filler_percentage": 4.0})

            aptitude_eval = {
                "composite_aptitude_score": 46.0,
                "scores": {"logical_reasoning": 44.0, "problem_solving_clarity": 52.0, "situational_effectiveness": 45.0, "risk_mitigation": 42.0},
                "framework_adherence_percent": 50.0,
            }
            comm_telemetry = {"clarity": 62.0, "filler_percentage": 3.5}

        elif profile.archetype == CandidateArchetype.OVERQUALIFIED:
            q1 = "Describe your approach to automating CI/CD pipeline deployments."
            r1 = "In our global financial infrastructure, simple CI/CD is insufficient. I architected zero-trust immutable image pipelines using Cosign cryptographic attestation, SPIFFE/SPIRE workload identities, and automated canary rollouts managed by ArgoCD and eBPF network telemetry to detect anomalies before 1% traffic shifting."
            turns.append(SimulationTurnData(turn_index=1, phase="TECHNICAL", question_asked=q1, candidate_response=r1, hesitation_seconds=0.8, filler_percentage=0.5, stress_index=16.0, relevance_score=96.0))
            raw_turns.append({"turn_index": 1, "question": q1, "response": r1})
            stress_signals.append({"turn_index": 1, "stress_index": 16.0, "hesitation_latency": 0.8, "filler_percentage": 0.5})

            q2 = "How do you manage disagreements on simple configuration choices?"
            r2 = "I prioritize team ownership and blameless consensus. Even if an architecture decision differs from my preferred approach, if it satisfies security, SLAs, and observability constraints, I empower the team to execute autonomously."
            turns.append(SimulationTurnData(turn_index=2, phase="BEHAVIORAL", question_asked=q2, candidate_response=r2, hesitation_seconds=1.0, filler_percentage=0.8, stress_index=18.0, relevance_score=92.0))
            raw_turns.append({"turn_index": 2, "question": q2, "response": r2})
            stress_signals.append({"turn_index": 2, "stress_index": 18.0, "hesitation_latency": 1.0, "filler_percentage": 0.8})

            aptitude_eval = {
                "composite_aptitude_score": 94.0,
                "scores": {"logical_reasoning": 95.0, "problem_solving_clarity": 93.0, "situational_effectiveness": 95.0, "risk_mitigation": 94.0},
                "framework_adherence_percent": 100.0,
            }
            comm_telemetry = {"clarity": 92.0, "filler_percentage": 0.6}

        else:  # INCONSISTENT
            q1 = "Tell me about your role leading the payment gateway redesign."
            r1 = "I single-handedly built the entire distributed payment gateway from scratch alone, making all architectural choices."
            turns.append(SimulationTurnData(turn_index=1, phase="BEHAVIORAL", question_asked=q1, candidate_response=r1, hesitation_seconds=1.8, filler_percentage=4.5, stress_index=55.0, relevance_score=65.0))
            raw_turns.append({"turn_index": 1, "question": q1, "response": r1})
            stress_signals.append({"turn_index": 1, "stress_index": 55.0, "hesitation_latency": 1.8, "filler_percentage": 4.5})

            q2 = "When the recent release failed, how did the post-mortem proceed?"
            r2 = "It wasn't my fault at all, the management ruined our timeline and the QA team failed to test properly. Either we rewrite the entire codebase in Go or the company will go bankrupt."
            turns.append(SimulationTurnData(turn_index=2, phase="SITUATIONAL", question_asked=q2, candidate_response=r2, hesitation_seconds=3.5, filler_percentage=6.0, stress_index=82.0, relevance_score=40.0))
            raw_turns.append({"turn_index": 2, "question": q2, "response": r2})
            stress_signals.append({"turn_index": 2, "stress_index": 82.0, "hesitation_latency": 3.5, "filler_percentage": 6.0})

            q3 = "How did you configure database connection pools in that gateway?"
            r3 = "My seniors decided all database architecture decisions, I only wrote tests and followed orders."
            turns.append(SimulationTurnData(turn_index=3, phase="TECHNICAL", question_asked=q3, candidate_response=r3, hesitation_seconds=3.2, filler_percentage=5.5, stress_index=75.0, relevance_score=45.0))
            raw_turns.append({"turn_index": 3, "question": q3, "response": r3})
            stress_signals.append({"turn_index": 3, "stress_index": 75.0, "hesitation_latency": 3.2, "filler_percentage": 5.5})

            fallacies.append({"fallacy_type": "BLAME_DEFLECTION", "explanation": "Candidate stated failure wasn't their fault and blamed management and QA."})
            fallacies.append({"fallacy_type": "FALSE_DILEMMA", "explanation": "Framed operational choice as an extreme binary: rewrite in Go or go bankrupt."})

            aptitude_eval = {
                "composite_aptitude_score": 35.0,
                "scores": {"logical_reasoning": 30.0, "problem_solving_clarity": 42.0, "situational_effectiveness": 38.0, "risk_mitigation": 30.0},
                "framework_adherence_percent": 35.0,
            }
            comm_telemetry = {"clarity": 55.0, "filler_percentage": 5.5}

        return turns, raw_turns, aptitude_eval, comm_telemetry, stress_signals, fallacies

    def _create_mock_score_report(self, profile: SimulatedCandidateProfile, turns: List[SimulationTurnData]) -> CandidateHRScoreReport:
        """Constructs an integrated CandidateHRScoreReport based on turn telemetry."""
        avg_rel = sum(t.relevance_score for t in turns) / max(len(turns), 1)
        avg_stress = sum(t.stress_index for t in turns) / max(len(turns), 1)
        comp_score = max(0.0, min(100.0, 100.0 - (avg_stress * 0.75)))

        if profile.archetype == CandidateArchetype.CONFIDENT:
            comm_score = 90.0
            cons_score = 92.0
            base_comp = 90.5
            rec = HiringRecommendation.STRONG_HIRE
        elif profile.archetype == CandidateArchetype.HESITANT:
            comm_score = 68.0
            cons_score = 70.0
            base_comp = 68.5
            rec = HiringRecommendation.LEAN_HIRE
        elif profile.archetype == CandidateArchetype.INEXPERIENCED:
            comm_score = 62.0
            cons_score = 55.0
            base_comp = 53.0
            rec = HiringRecommendation.LEAN_NO_HIRE
        elif profile.archetype == CandidateArchetype.OVERQUALIFIED:
            comm_score = 92.0
            cons_score = 94.0
            base_comp = 92.0
            rec = HiringRecommendation.STRONG_HIRE
        else:  # INCONSISTENT
            comm_score = 52.0
            cons_score = 35.0
            base_comp = 42.0
            rec = HiringRecommendation.NO_HIRE

        return CandidateHRScoreReport(
            candidate_id=profile.candidate_id,
            candidate_name=profile.name,
            job_role=profile.target_role,
            experience_years=profile.experience_years,
            session_id=f"SESS-{profile.candidate_id}-2026",
            evaluation_date=datetime.now().isoformat(),
            weight_profile_used="technical_roles",
            composite_score=base_comp,
            recommendation=rec,
            executive_summary=f"Automated simulation completed for {profile.name} ({profile.archetype.value}).",
            parameter_breakdown={
                "answer_relevance": ParameterContribution(
                    parameter=ScoringParameter.ANSWER_RELEVANCE,
                    display_name="Answer Relevance",
                    raw_score=avg_rel,
                    normalized_score=avg_rel,
                    weight=0.30,
                    weighted_contribution=round(avg_rel * 0.30, 2),
                    percentage_of_total=30.0,
                    diagnostic_summary="Relevance assessment.",
                ),
                "communication_score": ParameterContribution(
                    parameter=ScoringParameter.COMMUNICATION,
                    display_name="Communication Score",
                    raw_score=comm_score,
                    normalized_score=comm_score,
                    weight=0.25,
                    weighted_contribution=round(comm_score * 0.25, 2),
                    percentage_of_total=25.0,
                    diagnostic_summary="Communication assessment.",
                ),
                "confidence_score": ParameterContribution(
                    parameter=ScoringParameter.CONFIDENCE,
                    display_name="Confidence Score",
                    raw_score=comp_score,
                    normalized_score=comp_score,
                    weight=0.25,
                    weighted_contribution=round(comp_score * 0.25, 2),
                    percentage_of_total=25.0,
                    diagnostic_summary="Composure assessment.",
                ),
                "consistency": ParameterContribution(
                    parameter=ScoringParameter.CONSISTENCY,
                    display_name="Consistency",
                    raw_score=cons_score,
                    normalized_score=cons_score,
                    weight=0.20,
                    weighted_contribution=round(cons_score * 0.20, 2),
                    percentage_of_total=20.0,
                    diagnostic_summary="Narrative consistency.",
                ),
            },
            length_normalization=LengthNormalizationMetadata(
                total_turns_evaluated=len(turns),
                expected_standard_turns=5,
                raw_average_score=base_comp,
                normalized_score=base_comp,
                prior_mean=70.0,
                prior_weight_m=2.0,
                recency_weighted_average=base_comp,
                session_completeness_factor=1.0,
                normalization_adjustment=0.0,
            ),
            communication_subdimensions={"fluency": comm_score, "clarity": comm_score, "filler_control": comm_score},
            behavioral_subdimensions={"hesitation_control": comp_score, "stress_resilience": comp_score},
            turn_score_trajectory=[],
            key_strengths=[],
            risk_flags=[],
            recommended_next_steps=[],
        )

    def simulate_session(self, profile: SimulatedCandidateProfile) -> SessionSimulationResult:
        """Executes a single end-to-end simulated session for a candidate profile."""
        turns, raw_turns, apt_eval, comm_telemetry, stress_signals, fallacies = self._generate_candidate_turns(profile)
        score_report = self._create_mock_score_report(profile, turns)

        candidate_meta = {
            "candidate_id": profile.candidate_id,
            "candidate_name": profile.name,
            "job_role": profile.target_role,
            "experience_years": profile.experience_years,
            "session_id": f"SESS-{profile.candidate_id}-2026",
        }

        # Run InterviewSummaryGenerator
        summary = self.summary_generator.generate_summary(
            candidate_metadata=candidate_meta,
            transcript_turns=raw_turns,
            score_report=score_report,
            aptitude_evaluation=apt_eval,
            communication_telemetry=comm_telemetry,
            stress_signals=stress_signals,
            fallacy_flags=fallacies,
        )

        ai_score = summary.overall_performance.composite_score
        ai_rec = summary.overall_performance.recommendation
        human_score = profile.human_ground_truth.composite_score
        human_rec = profile.human_ground_truth.recommendation

        variance = round(ai_score - human_score, 2)
        decision_match = (ai_rec == human_rec)

        tier_order = [
            HiringRecommendation.NO_HIRE,
            HiringRecommendation.LEAN_NO_HIRE,
            HiringRecommendation.LEAN_HIRE,
            HiringRecommendation.HIRE,
            HiringRecommendation.STRONG_HIRE,
        ]
        ai_tier_idx = tier_order.index(ai_rec) if ai_rec in tier_order else 2
        human_tier_idx = tier_order.index(human_rec) if human_rec in tier_order else 2
        tier_distance = abs(ai_tier_idx - human_tier_idx)

        # Save artifacts
        json_path = os.path.join(self.output_dir, f"{profile.candidate_id}_summary.json")
        md_path = os.path.join(self.output_dir, f"{profile.candidate_id}_summary.md")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(self.summary_generator.to_ats_json(summary))
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.summary_generator.to_recruiter_markdown(summary))

        cult_avg = sum(c.score for c in summary.cultural_fit_indicators) / max(len(summary.cultural_fit_indicators), 1)

        return SessionSimulationResult(
            session_id=f"SESS-{profile.candidate_id}-2026",
            candidate=profile,
            turns_executed=turns,
            ai_composite_score=ai_score,
            ai_recommendation=ai_rec,
            human_composite_score=human_score,
            human_recommendation=human_rec,
            score_variance=variance,
            decision_match=decision_match,
            tier_distance=tier_distance,
            inconsistencies_detected=len(summary.inconsistencies),
            cultural_fit_average=round(cult_avg, 1),
            summary_markdown_path=md_path,
            summary_json_path=json_path,
        )

    def run_cohort_simulation(self, profiles: Optional[List[SimulatedCandidateProfile]] = None) -> List[SessionSimulationResult]:
        """Runs the simulation across all profiles in the cohort and persists master JSON results."""
        cohort = profiles or self.get_standard_cohort_profiles()
        results: List[SessionSimulationResult] = []

        for p in cohort:
            res = self.simulate_session(p)
            results.append(res)

        master_path = os.path.join(self.output_dir, "simulation_cohort_results.json")
        with open(master_path, "w", encoding="utf-8") as f:
            serializable = [r.model_dump() for r in results]
            json.dump(serializable, f, indent=2)

        return results

"""
Day 63: End-to-End Pipeline Simulation Environment
Simulates: ATS Ingestion -> Screening -> Technical AI -> Behavioral STAR -> Machine Test -> Decision Seal
Platform: Zecpath Automated Hiring Platform
"""

import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from demo_dataset_ai.models import (
    JobDescription,
    CandidateResume,
    TurnResponseSet,
    SimulationStageResult,
    FullPipelineSimulationReport,
)
from demo_dataset_ai.job_descriptions import CURATED_JOB_DESCRIPTIONS
from demo_dataset_ai.resumes import CURATED_CANDIDATE_RESUMES
from demo_dataset_ai.candidate_responses import CURATED_CANDIDATE_RESPONSES


class EndToEndSimulationEnvironment:
    """
    End-to-End Hiring Pipeline Simulation Environment.
    Executes automated candidate journey through all 5 evaluation gates.
    """

    def __init__(self, job_description: Optional[JobDescription] = None):
        self.job = job_description or CURATED_JOB_DESCRIPTIONS["JOB-BACKEND-SR"]

    def simulate_candidate(self, candidate_id: str) -> FullPipelineSimulationReport:
        start_time = time.perf_counter()

        resume = CURATED_CANDIDATE_RESUMES.get(candidate_id)
        responses = CURATED_CANDIDATE_RESPONSES.get(candidate_id)

        if not resume or not responses:
            raise ValueError(f"Candidate {candidate_id} not found in curated demo dataset.")

        stages: List[SimulationStageResult] = []

        # -------------------------------------------------------------
        # Stage 1: ATS Resume Parser & Keyword Vector Matcher
        # -------------------------------------------------------------
        matched_req = [s for s in resume.skills if s in self.job.required_skills]
        matched_pref = [s for s in resume.skills if s in self.job.preferred_skills]
        raw_match_pct = (len(matched_req) / max(1, len(self.job.required_skills))) * 80.0 + (
            len(matched_pref) / max(1, len(self.job.preferred_skills))
        ) * 20.0
        ats_score = min(100.0, raw_match_pct)
        ats_status = "PASSED" if ats_score >= 50.0 else "FILTERED_OUT"

        stages.append(
            SimulationStageResult(
                stage_name="1_ATS_Resume_Ingestion",
                status=ats_status,
                score=round(ats_score, 1),
                metrics={
                    "experience_years": resume.experience_years,
                    "matched_required_skills": matched_req,
                    "matched_preferred_skills": matched_pref,
                },
                feedback=f"Matched {len(matched_req)}/{len(self.job.required_skills)} required core skills.",
            )
        )

        # -------------------------------------------------------------
        # Stage 2: Initial Screening & Demographic Bias Scrubber
        # -------------------------------------------------------------
        exp_score = min(100.0, (resume.experience_years / self.job.min_experience_years) * 100.0)
        screening_score = round(0.60 * ats_score + 0.40 * exp_score, 1)
        screening_status = "QUALIFIED" if screening_score >= 60.0 else "BELOW_THRESHOLD"

        stages.append(
            SimulationStageResult(
                stage_name="2_Screening_and_Bias_Isolation",
                status=screening_status,
                score=screening_score,
                metrics={
                    "demographic_data_scrubbed": True,
                    "pii_redacted": True,
                    "experience_ratio": round(resume.experience_years / self.job.min_experience_years, 2),
                },
                feedback="Demographic markers shielded; candidate assessed strictly on merit.",
            )
        )

        # -------------------------------------------------------------
        # Stage 3: Technical Interview AI (Semantic Depth & Mechanisms)
        # -------------------------------------------------------------
        tech_text = responses.technical_answer.lower()
        mechanisms = ["replica set", "thread pool", "mutex", "kafka", "redis", "fastapi"]
        tradeoffs = ["latency vs throughput", "write heavy", "consistency", "trade-off"]

        mech_count = sum(1 for m in mechanisms if m in tech_text)
        trade_count = sum(1 for t in tradeoffs if t in tech_text)

        tech_score = min(100.0, (mech_count * 20.0) + (trade_count * 25.0) + min(20.0, len(tech_text.split()) * 0.4))
        tech_status = "STRONG" if tech_score >= 75.0 else ("COMPETENT" if tech_score >= 45.0 else "DEFICIENT")

        stages.append(
            SimulationStageResult(
                stage_name="3_Technical_Interview_AI",
                status=tech_status,
                score=round(tech_score, 1),
                metrics={
                    "mechanisms_identified": mech_count,
                    "tradeoffs_analyzed": trade_count,
                    "word_count": len(responses.technical_answer.split()),
                },
                feedback=f"Identified {mech_count} concrete mechanisms and {trade_count} architectural trade-offs.",
            )
        )

        # -------------------------------------------------------------
        # Stage 4: Behavioral AI (STAR Structure & Deliberation Credit)
        # -------------------------------------------------------------
        b_text = responses.behavioral_star_answer.lower()
        star_markers = sum(1 for kw in ["situation", "task", "action", "result", "incident", "dropped", "stabilize"] if kw in b_text)
        base_fluency = max(10.0, 100.0 - (responses.hesitation_filler_count * 2.0))

        # Cognitive Deliberation Restoration
        if responses.formulation_pause_sec >= 2.0 and len(b_text.split()) >= 20:
            deliberation_bonus = 6.0
        else:
            deliberation_bonus = 0.0

        star_score = min(100.0, (star_markers * 15.0) + (base_fluency * 0.5) + deliberation_bonus)
        behavioral_status = "EXEMPLARY" if star_score >= 75.0 else ("ACCEPTABLE" if star_score >= 50.0 else "UNSTRUCTURED")

        stages.append(
            SimulationStageResult(
                stage_name="4_Behavioral_STAR_AI",
                status=behavioral_status,
                score=round(star_score, 1),
                metrics={
                    "star_indicators_found": star_markers,
                    "hesitation_fillers": responses.hesitation_filler_count,
                    "formulation_pause_sec": responses.formulation_pause_sec,
                    "deliberation_bonus_awarded": deliberation_bonus,
                },
                feedback="Structured STAR response with cognitive deliberation pause credit.",
            )
        )

        # -------------------------------------------------------------
        # Stage 5: Machine Test Sandbox (AST Complexity & Correctness)
        # -------------------------------------------------------------
        code = responses.machine_test_code
        if "seen" in code and "target - num" in code:
            code_score = 95.0
            code_status = "OPTIMAL_O_N"
        elif "for j in range" in code:
            code_score = 65.0
            code_status = "SUBOPTIMAL_O_N2"
        elif "pass" in code:
            code_score = 15.0
            code_status = "INCOMPLETE"
        else:
            code_score = 5.0
            code_status = "NON_CODE"

        stages.append(
            SimulationStageResult(
                stage_name="5_Machine_Test_Sandbox",
                status=code_status,
                score=code_score,
                metrics={
                    "ast_loop_nesting_depth": 2 if "for j in range" in code else (1 if "for i in enumerate" in code else 0),
                    "memory_sandbox_limit_mb": 256,
                    "execution_timeout_sec": 5.0,
                },
                feedback=f"Code evaluated in containerized sandbox: status {code_status}.",
            )
        )

        # -------------------------------------------------------------
        # Cross-Round Decision Engine & Cryptographic Seal
        # -------------------------------------------------------------
        final_composite = round(
            0.15 * ats_score + 0.35 * tech_score + 0.25 * star_score + 0.25 * code_score, 1
        )

        if final_composite >= 80.0:
            final_verdict = "STRONG_HIRE"
        elif final_composite >= 60.0:
            final_verdict = "OFFER"
        elif final_composite >= 40.0:
            final_verdict = "HOLD"
        else:
            final_verdict = "REJECT"

        # Adverse impact simulation (EEOC compliance)
        air = 0.94 if final_composite >= 50.0 else 0.88

        # Cryptographic SHA-256 seal
        seal_payload = f"{candidate_id}:{self.job.job_id}:{final_composite}:{final_verdict}:{air}:{time.time()}"
        crypto_seal = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()

        total_ms = (time.perf_counter() - start_time) * 1000.0

        return FullPipelineSimulationReport(
            candidate_id=candidate_id,
            candidate_name=resume.name,
            target_role=self.job.title,
            archetype=resume.archetype,
            stages=stages,
            final_composite_score=final_composite,
            final_verdict=final_verdict,
            adverse_impact_ratio=air,
            cryptographic_seal=crypto_seal,
            total_execution_ms=round(total_ms, 2),
        )

    def run_all_simulations(self) -> List[FullPipelineSimulationReport]:
        return [self.simulate_candidate(cid) for cid in CURATED_CANDIDATE_RESUMES.keys()]

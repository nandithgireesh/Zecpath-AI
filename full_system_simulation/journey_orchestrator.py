"""
Day 56: Journey Orchestrator - End-to-End Hiring Journey Simulation
===================================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Simulates all 6 stages sequentially with stage transitions, SLA timings,
and full state tracking.
"""

import time
import math
import uuid
import datetime
from typing import Dict, List, Optional, Tuple, Any

from full_system_simulation.models import (
    HiringStage, StageStatus, DecisionVerdict,
    ResumeArtifact, ATSScoreResult, ScreeningResult,
    HRInterviewResult, TechnicalInterviewResult,
    FinalDecisionResult, CompleteJourneyDossier
)


class JourneyOrchestrator:
    """
    Simulates the candidate hiring journey through the 6 end-to-end stages:
    1. Resume Upload
    2. ATS Scoring
    3. Screening
    4. HR Interview
    5. Technical Interview
    6. Final Decision
    """

    # Stage weights for final composite scoring
    ATS_WEIGHT = 0.15
    SCREENING_WEIGHT = 0.10
    HR_WEIGHT = 0.30
    TECH_WEIGHT = 0.45

    def __init__(self, ats_cutoff: float = 65.0, screening_cutoff: float = 60.0):
        self.ats_cutoff = ats_cutoff
        self.screening_cutoff = screening_cutoff

    def run_stage_1_resume_upload(
        self,
        candidate_id: str,
        full_name: str,
        target_role: str,
        raw_text: str,
        experience_years: float,
        education_level: str,
        institution: str,
        primary_skills: List[str]
    ) -> Tuple[ResumeArtifact, float]:
        """Stage 1: Ingests and parses candidate resume."""
        t0 = time.perf_counter()
        # Simulated parsing latency (40 - 60ms)
        time.sleep(0.005)
        artifact = ResumeArtifact(
            candidate_id=candidate_id,
            full_name=full_name,
            target_role=target_role,
            raw_text=raw_text,
            experience_years=experience_years,
            education_level=education_level,
            institution=institution,
            primary_skills=primary_skills
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return artifact, elapsed_ms

    def run_stage_2_ats_scoring(
        self,
        resume: ResumeArtifact,
        required_role_keywords: List[str],
        min_experience_years: float = 3.0
    ) -> Tuple[ATSScoreResult, float]:
        """Stage 2: Deterministic ATS scoring based on keywords, experience, and format."""
        t0 = time.perf_counter()
        time.sleep(0.006)

        # Keyword match
        matched_kw = [kw for kw in required_role_keywords if kw.lower() in resume.raw_text.lower() or kw in resume.primary_skills]
        missing_kw = [kw for kw in required_role_keywords if kw not in matched_kw]
        kw_ratio = len(matched_kw) / max(len(required_role_keywords), 1)
        keyword_score = round(kw_ratio * 100.0, 1)

        # Experience relevance
        exp_ratio = min(resume.experience_years / max(min_experience_years, 1.0), 1.5) / 1.5
        experience_score = round(min(exp_ratio * 100.0, 100.0), 1)

        # Format hygiene
        has_sections = all(term in resume.raw_text.lower() for term in ["experience", "education", "skills"])
        format_score = 95.0 if has_sections else 70.0

        # Composite ATS
        composite = round(0.50 * keyword_score + 0.35 * experience_score + 0.15 * format_score, 1)
        passed = composite >= self.ats_cutoff

        result = ATSScoreResult(
            candidate_id=resume.candidate_id,
            keyword_match_score=keyword_score,
            experience_relevance_score=experience_score,
            format_hygiene_score=format_score,
            composite_ats_score=composite,
            passed=passed,
            status=StageStatus.PASSED if passed else StageStatus.FAILED,
            extracted_keywords=matched_kw,
            missing_critical_skills=missing_kw
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return result, elapsed_ms

    def run_stage_3_screening(
        self,
        candidate_id: str,
        work_auth: bool,
        salary_fit: bool,
        notice_days: int,
        raw_screening_score: float
    ) -> Tuple[ScreeningResult, float]:
        """Stage 3: Fast-gate prerequisite and administrative screening."""
        t0 = time.perf_counter()
        time.sleep(0.004)

        flags = []
        if not work_auth:
            flags.append("NO_VALID_WORK_AUTH")
        if not salary_fit:
            flags.append("COMPENSATION_EXPECTATION_MISMATCH")
        if notice_days > 90:
            flags.append("EXTENDED_NOTICE_PERIOD")

        prereq_met = work_auth and salary_fit
        score = raw_screening_score if prereq_met else min(raw_screening_score, 45.0)
        passed = prereq_met and (score >= self.screening_cutoff)

        result = ScreeningResult(
            candidate_id=candidate_id,
            work_authorization_valid=work_auth,
            salary_alignment_valid=salary_fit,
            notice_period_days=notice_days,
            prerequisite_met=prereq_met,
            screening_score=round(score, 1),
            status=StageStatus.PASSED if passed else StageStatus.FAILED,
            flags=flags
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return result, elapsed_ms

    def run_stage_4_hr_interview(
        self,
        candidate_id: str,
        behavioral_score: float,
        communication_clarity_score: float,
        confidence_index: float,
        sentiment_stability_score: float,
        speech_pause_telemetry: float
    ) -> Tuple[HRInterviewResult, float]:
        """Stage 4: Multi-modal behavioral, sentiment, and communication interview."""
        t0 = time.perf_counter()
        time.sleep(0.008)

        red_flags = []
        if behavioral_score < 50.0:
            red_flags.append("CULTURE_FIT_DEFICIT")
        if sentiment_stability_score < 45.0:
            red_flags.append("HIGH_SENTIMENT_VOLATILITY")
        if speech_pause_telemetry < 40.0:
            red_flags.append("EXTENDED_SPEECH_HESITATION")

        composite = round(
            0.35 * behavioral_score +
            0.25 * communication_clarity_score +
            0.20 * confidence_index +
            0.20 * sentiment_stability_score,
            1
        )
        passed = composite >= 55.0 and len(red_flags) <= 1

        result = HRInterviewResult(
            candidate_id=candidate_id,
            behavioral_score=round(behavioral_score, 1),
            communication_clarity_score=round(communication_clarity_score, 1),
            confidence_index=round(confidence_index, 1),
            sentiment_stability_score=round(sentiment_stability_score, 1),
            speech_pause_telemetry=round(speech_pause_telemetry, 1),
            composite_hr_score=composite,
            status=StageStatus.PASSED if passed else StageStatus.FAILED,
            red_flags=red_flags
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return result, elapsed_ms

    def run_stage_5_technical_interview(
        self,
        candidate_id: str,
        coding_correctness: float,
        algorithmic_efficiency: float,
        system_design: float,
        problem_solving: float,
        test_cases_passed: int,
        total_test_cases: int
    ) -> Tuple[TechnicalInterviewResult, float]:
        """Stage 5: Algorithmic sandbox and technical architecture evaluation."""
        t0 = time.perf_counter()
        time.sleep(0.010)

        composite = round(
            0.40 * coding_correctness +
            0.25 * algorithmic_efficiency +
            0.20 * system_design +
            0.15 * problem_solving,
            1
        )
        passed = composite >= 60.0 and (test_cases_passed / max(total_test_cases, 1) >= 0.6)

        result = TechnicalInterviewResult(
            candidate_id=candidate_id,
            coding_correctness_score=round(coding_correctness, 1),
            algorithmic_efficiency_score=round(algorithmic_efficiency, 1),
            system_design_score=round(system_design, 1),
            problem_solving_score=round(problem_solving, 1),
            composite_technical_score=composite,
            test_cases_passed=test_cases_passed,
            total_test_cases=total_test_cases,
            status=StageStatus.PASSED if passed else StageStatus.FAILED,
            execution_time_ms=135.2
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return result, elapsed_ms

    def run_stage_6_final_decision(
        self,
        candidate_id: str,
        ats: ATSScoreResult,
        screening: ScreeningResult,
        hr: HRInterviewResult,
        tech: TechnicalInterviewResult,
        human_verdict: DecisionVerdict
    ) -> Tuple[FinalDecisionResult, float]:
        """Stage 6: Multi-pillar Bayesian score arbitration and AI verdict generation."""
        t0 = time.perf_counter()
        time.sleep(0.005)

        raw_score = (
            self.ATS_WEIGHT * ats.composite_ats_score +
            self.SCREENING_WEIGHT * screening.screening_score +
            self.HR_WEIGHT * hr.composite_hr_score +
            self.TECH_WEIGHT * tech.composite_technical_score
        )

        # Cross-round variance smoothing
        scores = [ats.composite_ats_score, screening.screening_score, hr.composite_hr_score, tech.composite_technical_score]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)

        # Variance damping penalty
        stability_penalty = min(std_dev * 0.15, 6.0)
        variance_smoothed = round(raw_score - stability_penalty, 2)

        # Determine AI Verdict
        if variance_smoothed >= 85.0:
            ai_verdict = DecisionVerdict.STRONG_HIRE
        elif variance_smoothed >= 74.0:
            ai_verdict = DecisionVerdict.HIRE
        elif variance_smoothed >= 65.0:
            ai_verdict = DecisionVerdict.LEAN_HIRE
        elif variance_smoothed >= 58.0:
            ai_verdict = DecisionVerdict.HOLD_REVIEW
        elif variance_smoothed >= 50.0:
            ai_verdict = DecisionVerdict.LEAN_REJECT
        else:
            ai_verdict = DecisionVerdict.REJECT

        # Evaluate Alignment
        alignment = (ai_verdict == human_verdict)
        divergence_reasons = []
        if not alignment:
            divergence_reasons.append(f"AI verdict is '{ai_verdict.value}' while Human verdict is '{human_verdict.value}'.")
            if abs(tech.composite_technical_score - hr.composite_hr_score) > 25.0:
                divergence_reasons.append("High cross-round variance between HR soft skills and Technical depth.")

        result = FinalDecisionResult(
            candidate_id=candidate_id,
            raw_composite_score=round(raw_score, 2),
            variance_smoothed_score=variance_smoothed,
            confidence_interval=round(max(0.95 - (std_dev / 100.0), 0.70), 3),
            ai_verdict=ai_verdict,
            human_verdict=human_verdict,
            alignment=alignment,
            dossier_id=f"DOSSIER-{uuid.uuid4().hex[:8].upper()}",
            status=StageStatus.PASSED,
            divergence_reasons=divergence_reasons
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return result, elapsed_ms

    def simulate_complete_journey(
        self,
        candidate_data: Dict[str, Any],
        required_keywords: List[str]
    ) -> CompleteJourneyDossier:
        """
        Executes the entire 6-stage candidate pipeline sequentially.
        """
        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cid = candidate_data["candidate_id"]
        cname = candidate_data["full_name"]
        role = candidate_data["target_role"]

        dossier = CompleteJourneyDossier(
            journey_id=f"JRN-{uuid.uuid4().hex[:8].upper()}",
            candidate_id=cid,
            candidate_name=cname,
            target_role=role,
            start_time=start_time,
            completion_time=start_time
        )

        total_lat = 0.0

        # Stage 1
        resume, lat1 = self.run_stage_1_resume_upload(
            candidate_id=cid,
            full_name=cname,
            target_role=role,
            raw_text=candidate_data["resume_text"],
            experience_years=candidate_data["experience_years"],
            education_level=candidate_data["education_level"],
            institution=candidate_data["institution"],
            primary_skills=candidate_data["primary_skills"]
        )
        dossier.resume = resume
        dossier.stage_progression[HiringStage.RESUME_UPLOAD] = StageStatus.PASSED
        total_lat += lat1

        # Stage 2
        ats, lat2 = self.run_stage_2_ats_scoring(resume, required_keywords, min_experience_years=3.0)
        dossier.ats_result = ats
        dossier.stage_progression[HiringStage.ATS_SCORING] = ats.status
        total_lat += lat2

        # Stage 3
        scr_data = candidate_data["screening"]
        screening, lat3 = self.run_stage_3_screening(
            candidate_id=cid,
            work_auth=scr_data["work_auth"],
            salary_fit=scr_data["salary_fit"],
            notice_days=scr_data["notice_days"],
            raw_screening_score=scr_data["score"]
        )
        dossier.screening_result = screening
        dossier.stage_progression[HiringStage.SCREENING] = screening.status
        total_lat += lat3

        # Stage 4
        hr_data = candidate_data["hr_interview"]
        hr, lat4 = self.run_stage_4_hr_interview(
            candidate_id=cid,
            behavioral_score=hr_data["behavioral"],
            communication_clarity_score=hr_data["communication"],
            confidence_index=hr_data["confidence"],
            sentiment_stability_score=hr_data["sentiment"],
            speech_pause_telemetry=hr_data["speech_pause"]
        )
        dossier.hr_result = hr
        dossier.stage_progression[HiringStage.HR_INTERVIEW] = hr.status
        total_lat += lat4

        # Stage 5
        tech_data = candidate_data["technical_interview"]
        tech, lat5 = self.run_stage_5_technical_interview(
            candidate_id=cid,
            coding_correctness=tech_data["coding"],
            algorithmic_efficiency=tech_data["algorithmic"],
            system_design=tech_data["design"],
            problem_solving=tech_data["problem_solving"],
            test_cases_passed=tech_data["passed_cases"],
            total_test_cases=tech_data["total_cases"]
        )
        dossier.technical_result = tech
        dossier.stage_progression[HiringStage.TECHNICAL_INTERVIEW] = tech.status
        total_lat += lat5

        # Stage 6
        final_dec, lat6 = self.run_stage_6_final_decision(
            candidate_id=cid,
            ats=ats,
            screening=screening,
            hr=hr,
            tech=tech,
            human_verdict=candidate_data["human_verdict"]
        )
        dossier.final_decision = final_dec
        dossier.stage_progression[HiringStage.FINAL_DECISION] = final_dec.status
        total_lat += lat6

        dossier.total_latency_ms = round(total_lat, 2)
        dossier.completion_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        dossier.journey_passed = final_dec.ai_verdict in [DecisionVerdict.STRONG_HIRE, DecisionVerdict.HIRE, DecisionVerdict.LEAN_HIRE]

        return dossier

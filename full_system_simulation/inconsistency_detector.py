"""
Day 56: Inconsistency Detector - Anomaly Identification & Diagnosis Engine
==========================================================================
Platform: Zecpath Enterprise Talent Assessment Platform
Detects systemic anomalies, cross-round variance, and human/AI divergences
across the 6-stage hiring journey.
"""

import uuid
from typing import Dict, List, Optional, Any

from full_system_simulation.models import (
    HiringStage, InconsistencyType, InconsistencyRecord, CompleteJourneyDossier
)


class InconsistencyDetector:
    """
    Identifies and categorizes systematic inconsistencies across stages
    and between AI and Human evaluations.
    """

    def scan_dossier_for_inconsistencies(
        self,
        dossier: CompleteJourneyDossier
    ) -> List[InconsistencyRecord]:
        """
        Analyzes a candidate's complete journey dossier for anomalies.
        """
        records: List[InconsistencyRecord] = []

        ats = dossier.ats_result
        hr = dossier.hr_result
        tech = dossier.technical_result
        final = dossier.final_decision
        comp = dossier.comparative_record

        if not (ats and hr and tech and final):
            return records

        # 1. Resume Inflation vs Technical Execution
        if ats.composite_ats_score >= 85.0 and tech.composite_technical_score < 55.0:
            rec = InconsistencyRecord(
                inconsistency_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                candidate_id=dossier.candidate_id,
                candidate_name=dossier.candidate_name,
                inconsistency_type=InconsistencyType.RESUME_INFLATION,
                severity="CRITICAL",
                detected_stage=HiringStage.TECHNICAL_INTERVIEW,
                ai_observation=(
                    f"Candidate scored ATS {ats.composite_ats_score:.1f}% based on keywords, "
                    f"but achieved only {tech.composite_technical_score:.1f}% in sandbox execution "
                    f"({tech.test_cases_passed}/{tech.total_test_cases} test cases)."
                ),
                human_observation="Interviewer noted candidate struggled with basic data structure syntax despite 5+ yrs listed.",
                root_cause="CV keyword optimization and resume inflation unbacked by practical coding capability.",
                recommended_remediation="Weight sandbox machine test higher (50%) and enforce interactive syntax pre-screens."
            )
            records.append(rec)

        # 2. Fluency Masking Weak Technical Depth
        if hr.communication_clarity_score >= 82.0 and hr.confidence_index >= 85.0 and tech.coding_correctness_score < 52.0:
            rec = InconsistencyRecord(
                inconsistency_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                candidate_id=dossier.candidate_id,
                candidate_name=dossier.candidate_name,
                inconsistency_type=InconsistencyType.FLUENCY_DISGUISE,
                severity="CRITICAL",
                detected_stage=HiringStage.FINAL_DECISION,
                ai_observation=(
                    f"High verbal polish (HR Clarity {hr.communication_clarity_score:.1f}%, Confidence {hr.confidence_index:.1f}%) "
                    f"contradicted by failing code correctness ({tech.coding_correctness_score:.1f}%)."
                ),
                human_observation="Non-technical hiring manager was highly impressed by articulation and recommended hire.",
                root_cause="Vocal confidence and charismatic delivery created an unmerited halo effect overshadowing technical failure.",
                recommended_remediation="Decouple HR confidence from technical gates; require hard coding cutoff before interview panel."
            )
            records.append(rec)

        # 3. Non-Native Accent / Speech Telemetry Rigidity (AI False Negative)
        if tech.composite_technical_score >= 88.0 and hr.speech_pause_telemetry < 45.0 and final.variance_smoothed_score < 70.0:
            rec = InconsistencyRecord(
                inconsistency_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                candidate_id=dossier.candidate_id,
                candidate_name=dossier.candidate_name,
                inconsistency_type=InconsistencyType.ACCENT_BIAS_DRIFT,
                severity="CRITICAL",
                detected_stage=HiringStage.HR_INTERVIEW,
                ai_observation=(
                    f"Candidate delivered top-tier technical performance ({tech.composite_technical_score:.1f}%), but "
                    f"acoustic pause telemetry score ({hr.speech_pause_telemetry:.1f}) depressed composite score to {final.variance_smoothed_score:.1f}."
                ),
                human_observation="Human panel found candidate's explanations deeply technical and accurate despite deliberate, accented pacing.",
                root_cause="Acoustic NLP telemetry over-penalized non-native articulation cadence as lack of confidence.",
                recommended_remediation="Calibrate speech telemetry against dialect-neutral baseline; isolate acoustic metrics from final verdict."
            )
            records.append(rec)

        # 4. Pedigree Halo Bias (Human False Positive)
        if comp and comp.human_bias_marker == "PEDIGREE_HALO":
            rec = InconsistencyRecord(
                inconsistency_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                candidate_id=dossier.candidate_id,
                candidate_name=dossier.candidate_name,
                inconsistency_type=InconsistencyType.PEDIGREE_HALO_BIAS,
                severity="MODERATE",
                detected_stage=HiringStage.FINAL_DECISION,
                ai_observation=(
                    f"Objective AI composite score was {final.variance_smoothed_score:.1f} (Verdict: {final.ai_verdict.value}), "
                    f"reflecting deficient system design ({tech.system_design_score:.1f}%)."
                ),
                human_observation="Hiring lead overrode AI to 'HIRE' citing prestigious Alma Mater and past brand-name employer.",
                root_cause="Human subjective bias anchor to elite educational institution over actual performance metrics.",
                recommended_remediation="Implement blinded resume review and mandate objective rubric justifications for overrides."
            )
            records.append(rec)

        # 5. Evaluator Fatigue Drift
        if comp and comp.human_bias_marker == "AFTERNOON_FATIGUE":
            rec = InconsistencyRecord(
                inconsistency_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                candidate_id=dossier.candidate_id,
                candidate_name=dossier.candidate_name,
                inconsistency_type=InconsistencyType.FATIGUE_DRIFT,
                severity="LOW",
                detected_stage=HiringStage.HR_INTERVIEW,
                ai_observation="AI performance telemetry was stable across all cohort time slots.",
                human_observation="Human evaluator scores dropped by 18% during late-afternoon evaluation sessions (4 PM - 6 PM).",
                root_cause="Human cognitive fatigue and decision exhaustion causing stricter grading later in the business day.",
                recommended_remediation="Cap daily interview schedules at 4 sessions and use AI normalized baseline for calibration."
            )
            records.append(rec)

        dossier.inconsistencies = records
        return records

    def aggregate_cohort_inconsistencies(
        self,
        dossiers: List[CompleteJourneyDossier]
    ) -> Dict[str, Any]:
        """
        Summarizes inconsistency prevalence and breakdown across candidate population.
        """
        all_inconsistencies = []
        for d in dossiers:
            all_inconsistencies.extend(self.scan_dossier_for_inconsistencies(d))

        type_counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {"CRITICAL": 0, "MODERATE": 0, "LOW": 0}

        for inc in all_inconsistencies:
            t = inc.inconsistency_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
            severity_counts[inc.severity] = severity_counts.get(inc.severity, 0) + 1

        return {
            "total_inconsistencies_flagged": len(all_inconsistencies),
            "candidates_with_inconsistencies": len({inc.candidate_id for inc in all_inconsistencies}),
            "type_breakdown": type_counts,
            "severity_breakdown": severity_counts,
            "inconsistency_records": all_inconsistencies
        }

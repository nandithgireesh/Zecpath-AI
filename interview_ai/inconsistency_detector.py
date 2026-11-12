"""
Day 39: Cross-Turn & Cross-Modal Inconsistency Detection Engine
================================================================
Analyzes candidate interview transcripts, behavioral responses, multi-modal stress signals,
and claimed credentials to detect contradictions, factual mismatches, and affect discordance.
"""

import re
from typing import List, Dict, Any, Optional
from .summary_models import (
    InconsistencyFlag,
    InconsistencyType,
    InconsistencySeverity,
)


class InconsistencyDetector:
    """
    Automated inconsistency engine identifying factual contradictions, cross-turn discrepancies,
    and verbal-affect discordance across the HR interview pipeline.
    """

    def __init__(self):
        # Known indicators of extreme verbal confidence
        self.high_certainty_patterns = [
            r"\b(100%|completely|absolutely|without doubt|expert in|mastered|flawless|never failed)\b",
            r"\b(definitely know|inside out|trivially easy|piece of cake)\b",
        ]
        # Indicators of team size / role claims
        self.solo_claim_patterns = [
            r"\b(single-handedly|solo|alone|built it all myself|sole engineer|only person)\b"
        ]
        self.team_dependence_patterns = [
            r"\b(my tech lead decided|management decided|team made all decisions|i only wrote tests|i just followed orders)\b",
            r"\b(my seniors handled|not involved in architecture|team of \d+ handled)\b",
        ]
        # Blame deflection patterns
        self.blame_patterns = [
            r"\b(wasn't my fault|their mistake|management failed|pm ruined|blame the team|they didn't listen)\b"
        ]

    def detect_inconsistencies(
        self,
        transcript_turns: List[Dict[str, Any]],
        candidate_metadata: Optional[Dict[str, Any]] = None,
        stress_signals: Optional[List[Dict[str, Any]]] = None,
        fallacy_flags: Optional[List[Dict[str, Any]]] = None,
    ) -> List[InconsistencyFlag]:
        """
        Executes comprehensive inconsistency scanning across transcript turns,
        comparing statements against earlier claims, metadata, and affective signals.
        """
        inconsistencies: List[InconsistencyFlag] = []
        flag_idx = 1

        turns = transcript_turns or []
        meta = candidate_metadata or {}
        stresses = stress_signals or []
        fallacies = fallacy_flags or []

        # 1. Cross-Turn Contradiction: Solo Ownership vs Subordinate Execution
        solo_turn = None
        team_turn = None
        for i, turn in enumerate(turns):
            text = (turn.get("response") or turn.get("answer") or "").lower()
            turn_num = turn.get("turn_index", i + 1)
            
            for pat in self.solo_claim_patterns:
                if re.search(pat, text):
                    solo_turn = (turn_num, text)
                    break
            for pat in self.team_dependence_patterns:
                if re.search(pat, text):
                    team_turn = (turn_num, text)
                    break

        if solo_turn and team_turn:
            inconsistencies.append(
                InconsistencyFlag(
                    inconsistency_id=f"INC-{flag_idx:02d}",
                    inconsistency_type=InconsistencyType.CROSS_TURN_CONTRADICTION,
                    severity=InconsistencySeverity.CRITICAL,
                    claim_source=f"Turn {solo_turn[0]} Response",
                    contradicting_source=f"Turn {team_turn[0]} Response",
                    claimed_statement=solo_turn[1][:120] + "...",
                    contradicting_statement=team_turn[1][:120] + "...",
                    explanation=(
                        f"Candidate claimed total solo ownership and single-handed architecture in Turn {solo_turn[0]}, "
                        f"but contradicted this in Turn {team_turn[0]} stating key decisions were made by seniors or team leads."
                    ),
                    recommended_probing_question=(
                        "Could you specify precisely which modules in that project you architected personally versus "
                        "components managed by the broader team or technical lead?"
                    ),
                )
            )
            flag_idx += 1

        # 2. Verbal-Affect Discordance: Extreme Verbal Certainty vs High Stress / Hesitation
        for i, turn in enumerate(turns):
            text = (turn.get("response") or turn.get("answer") or "").lower()
            turn_num = turn.get("turn_index", i + 1)

            has_high_certainty = any(re.search(pat, text) for pat in self.high_certainty_patterns)
            
            # Check corresponding stress telemetry
            stress_match = next((s for s in stresses if s.get("turn_index") == turn_num), None)
            if stress_match and has_high_certainty:
                stress_index = stress_match.get("stress_index", 0.0)
                hesitation = stress_match.get("hesitation_latency", 0.0)
                fillers = stress_match.get("filler_percentage", 0.0)

                if stress_index >= 65.0 or hesitation >= 3.0 or fillers >= 8.0:
                    inconsistencies.append(
                        InconsistencyFlag(
                            inconsistency_id=f"INC-{flag_idx:02d}",
                            inconsistency_type=InconsistencyType.VERBAL_AFFECT_DISCORDANCE,
                            severity=InconsistencySeverity.MODERATE,
                            claim_source=f"Turn {turn_num} Verbal Claim",
                            contradicting_source=f"Turn {turn_num} Multi-Modal Telemetry",
                            claimed_statement=text[:120] + "...",
                            contradicting_statement=(
                                f"Stress Index: {stress_index:.1f}/100, Hesitation Latency: {hesitation:.2f}s, "
                                f"Filler Rate: {fillers:.1f}%"
                            ),
                            explanation=(
                                f"In Turn {turn_num}, candidate projected absolute verbal certainty, but acoustic and behavioral "
                                f"telemetry revealed severe physiological tension (Stress Index: {stress_index:.1f}) and hesitation."
                            ),
                            recommended_probing_question=(
                                "When faced with unexpected production outages in this domain, what specific telemetry "
                                "checkpoints do you examine first before committing a fix?"
                            ),
                        )
                    )
                    flag_idx += 1

        # 3. Competency Performance Gap: Senior Architecture Claim vs Fallacious Reasoning
        exp_years = meta.get("experience_years", 0.0)
        is_senior = exp_years >= 5.0 or "senior" in meta.get("job_role", "").lower() or "lead" in meta.get("job_role", "").lower()

        if is_senior and fallacies:
            for f in fallacies:
                fallacy_type = f.get("fallacy_type", "LOGICAL_FALLACY")
                inconsistencies.append(
                    InconsistencyFlag(
                        inconsistency_id=f"INC-{flag_idx:02d}",
                        inconsistency_type=InconsistencyType.COMPETENCY_PERFORMANCE_GAP,
                        severity=InconsistencySeverity.CRITICAL if "BLAME" in fallacy_type or "FALSE_DILEMMA" in fallacy_type else InconsistencySeverity.MODERATE,
                        claim_source=f"Resume/Profile ({meta.get('job_role', 'Senior Role')} with {exp_years:.1f} yrs)",
                        contradicting_source="Analytical Reasoning / SJT Evaluation",
                        claimed_statement=f"Targeting Senior Leadership Role ({meta.get('job_role', 'Engineering Lead')})",
                        contradicting_statement=f.get("explanation", f"Demonstrated {fallacy_type}"),
                        explanation=(
                            f"Candidate profile asserts senior technical leadership ({exp_years:.1f} years experience), "
                            f"yet situational evaluation exposed fundamental cognitive bias ({fallacy_type}) inconsistent with senior engineering."
                        ),
                        recommended_probing_question=(
                            "Can you walk through how you manage operational trade-offs without resorting to extreme binary choices "
                            "or blaming external dependencies?"
                        ),
                    )
                )
                flag_idx += 1

        # 4. Factual Experience Mismatch (e.g. Years of Experience or Scale discrepancies)
        claimed_years = meta.get("experience_years", 0.0)
        for i, turn in enumerate(turns):
            text = (turn.get("response") or turn.get("answer") or "").lower()
            turn_num = turn.get("turn_index", i + 1)
            
            # Check for mentions of starting career or years
            year_matches = re.findall(r"(\d+)\s+years?(?:\s+of)?\s+(?:experience|working|in industry)", text)
            for ym in year_matches:
                spoken_years = float(ym)
                if abs(spoken_years - claimed_years) >= 3.0:
                    inconsistencies.append(
                        InconsistencyFlag(
                            inconsistency_id=f"INC-{flag_idx:02d}",
                            inconsistency_type=InconsistencyType.FACTUAL_EXPERIENCE_MISMATCH,
                            severity=InconsistencySeverity.CRITICAL,
                            claim_source="Resume Profile",
                            contradicting_source=f"Turn {turn_num} Spoken Transcript",
                            claimed_statement=f"Resume asserts {claimed_years:.1f} years of professional experience",
                            contradicting_statement=f"Spoken response: '{ym} years of experience'",
                            explanation=(
                                f"Factual divergence of {abs(spoken_years - claimed_years):.1f} years between submitted resume profile "
                                f"({claimed_years:.1f} yrs) and candidate verbal disclosure ({spoken_years:.1f} yrs) in Turn {turn_num}."
                            ),
                            recommended_probing_question=(
                                f"Could you clarify the exact timeline of your career progression and how your professional tenure "
                                f"maps between your submitted resume and full-time industry roles?"
                            ),
                        )
                    )
                    flag_idx += 1

        return inconsistencies

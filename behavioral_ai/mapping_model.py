"""
Day 48 Deliverable 2: Signal-to-Score Mapping Model
===================================================
Mathematical formulations mapping observable continuous video/kinematic signals
into quantified behavioral indicators, cognitive deliberation credits,
neurodiversity safeguards, and composite behavioral scores.

Curriculum Reference: Day 48 - Deliverable 2: Signal-to-Score Mapping Model
"""

from typing import List, Dict, Tuple, Optional
import math

from behavioral_ai.models import (
    GazeDirection,
    HeadPoseMovement,
    FacialEngagementState,
    BehavioralInsightCategory,
    EthicalScoringClassification,
    RawTurnBehavioralSignals,
    MeasurableBehavioralIndicators,
    TurnBehavioralScore,
)


class BehavioralSignalMappingEngine:
    """
    Mathematical engine transforming raw kinematic and ocular telemetry
    into ethical, non-punitive behavioral metrics and cognitive insights.
    """

    def __init__(self, neurodiversity_mode_enabled: bool = False):
        self.neurodiversity_mode_enabled = neurodiversity_mode_enabled

    # --------------------------------------------------------------------------
    # 1. MEASURABLE INDICATOR COMPUTATION
    # --------------------------------------------------------------------------

    def compute_measurable_indicators(
        self,
        signals: RawTurnBehavioralSignals,
    ) -> MeasurableBehavioralIndicators:
        """
        Maps continuous raw telemetry into standardized indicators:
        - Focus Level [0-100]
        - Distraction Frequency [events/min]
        - Nervous Gestures Index [0-100]
        - Cognitive Deliberation Ratio [0.0-1.0]
        - Conversational Presence Score [0-100]
        """
        eye = signals.eye_telemetry
        head = signals.head_telemetry
        face = signals.facial_telemetry
        attn = signals.attention_telemetry
        duration_min = max(signals.turn_duration_sec / 60.0, 0.1)

        # 1. Focus Level (0.0 - 100.0)
        # Driven by screen dwell ratio, gaze stability, head steadiness, and sustained attention
        span_factor = min(1.0, attn.continuous_attention_span_sec / 25.0)
        focus_raw = (
            (eye.screen_dwell_ratio * 0.45) +
            (eye.gaze_stability_index * 0.25) +
            (head.head_stability_index * 0.15) +
            (span_factor * 0.15)
        ) * 100.0
        focus_level = round(max(0.0, min(100.0, focus_raw)), 1)

        # 2. Distraction Frequency (events per minute)
        # Sum of off-screen lookaways, head turning jerks, and ambient diversions normalized by time
        jerks = 1 if head.primary_pose_movement in (HeadPoseMovement.RESTLESS_TURNING, HeadPoseMovement.SUDDEN_JERK) else 0
        total_diversions = attn.off_screen_lookaway_events + jerks
        distraction_freq = round(total_diversions / duration_min, 2)

        # 3. Nervous Gestures Index (0.0 - 100.0)
        # Baseline blink rate is ~15-22 blinks/min; bursts > 32 blinks/min signal autonomic arousal
        excess_blink = max(0.0, min(1.0, (eye.blink_rate_per_minute - 22.0) / 25.0))
        lip_tension = face.lip_compression_index
        head_restlessness = max(0.0, min(1.0, (head.pitch_velocity_deg_sec + head.yaw_velocity_deg_sec + head.roll_velocity_deg_sec) / 50.0))

        nervous_raw = (
            (excess_blink * 0.40) +
            (lip_tension * 0.35) +
            (head_restlessness * 0.25)
        ) * 100.0
        nervous_index = round(max(0.0, min(100.0, nervous_raw)), 1)

        # 4. Cognitive Deliberation Ratio (0.0 - 1.0)
        # Distinguishes genuine problem-solving thinking gaze (looking up, concentrated brow) from distraction
        is_thinking_gaze = eye.dominant_gaze_direction in (GazeDirection.LOOKING_UP_THINKING, GazeDirection.SLIGHT_OFF_CENTER)
        has_brow_furrow = face.brow_furrow_intensity >= 0.40
        is_steady_pose = head.head_stability_index >= 0.60

        deliberation_score = 0.0
        if is_thinking_gaze:
            deliberation_score += 0.50
        if has_brow_furrow:
            deliberation_score += 0.30
        if is_steady_pose:
            deliberation_score += 0.20
        deliberation_ratio = round(max(0.0, min(1.0, deliberation_score)), 2)

        # 5. Conversational Presence Score (0.0 - 100.0)
        # Facial expressiveness, affirmative nodding, smile authenticity, responsive engagement
        nod_bonus = min(0.20, head.affirmative_nods_count * 0.07)
        presence_raw = (
            (face.expressiveness_score * 0.40) +
            (face.smile_authenticity_ratio * 0.25) +
            (nod_bonus * 0.20) +
            (eye.gaze_stability_index * 0.15)
        ) * 100.0
        presence_score = round(max(0.0, min(100.0, presence_raw)), 1)

        return MeasurableBehavioralIndicators(
            focus_level=focus_level,
            distraction_frequency=distraction_freq,
            nervous_gestures_index=nervous_index,
            cognitive_deliberation_ratio=deliberation_ratio,
            conversational_presence_score=presence_score,
        )

    # --------------------------------------------------------------------------
    # 2. TURN BEHAVIORAL SCORING & COMPOSITE FUSION
    # --------------------------------------------------------------------------

    def calculate_turn_score(
        self,
        signals: RawTurnBehavioralSignals,
        indicators: MeasurableBehavioralIndicators,
    ) -> TurnBehavioralScore:
        """
        Computes composite behavioral score incorporating:
        - Focus level (45%)
        - Conversational presence (35%)
        - Inverted nervousness (20%)
        - Deliberation credit (up to +12.0 pts)
        - Neurodiversity safeguard offset (up to +15.0 pts)
        """
        base_composite = (
            (indicators.focus_level * 0.45) +
            (indicators.conversational_presence_score * 0.35) +
            ((100.0 - indicators.nervous_gestures_index) * 0.20)
        )

        # Cognitive Deliberation Credit
        # Candidates deeply contemplating complex technical logic look away momentarily
        # We restore up to +12.0 credits to prevent false penalization
        deliberation_credit = 0.0
        if indicators.cognitive_deliberation_ratio >= 0.50:
            deliberation_credit = round(indicators.cognitive_deliberation_ratio * 12.0, 1)

        # Neurodiversity Safeguard Offset
        # If candidate exhibits low direct gaze but calm facial expression & zero deception signals,
        # apply non-punitive safeguard
        neurodiversity_offset = 0.0
        is_neurodiverse_candidate = (
            self.neurodiversity_mode_enabled or
            (signals.eye_telemetry.screen_dwell_ratio < 0.65 and
             indicators.nervous_gestures_index < 35.0 and
             indicators.distraction_frequency < 2.0)
        )

        if is_neurodiverse_candidate:
            neurodiversity_offset = 12.5

        # Final Composite
        composite_score = round(
            max(0.0, min(100.0, base_composite + deliberation_credit + neurodiversity_offset)),
            1
        )

        # Behavioral Insight Classification
        if is_neurodiverse_candidate and indicators.focus_level < 65.0:
            insight = BehavioralInsightCategory.NEURODIVERGENT_SAFEGUARDED
            ethical_class = EthicalScoringClassification.NEURODIVERSE_ADJUSTED
        elif indicators.distraction_frequency >= 4.0 or signals.attention_telemetry.multi_monitor_dispersion_detected:
            insight = BehavioralInsightCategory.DISENGAGED_OR_READING
            ethical_class = EthicalScoringClassification.NEUTRAL_BASELINE
        elif indicators.distraction_frequency >= 2.5:
            insight = BehavioralInsightCategory.MODERATE_DISTRACTION
            ethical_class = EthicalScoringClassification.NEUTRAL_BASELINE
        elif indicators.nervous_gestures_index >= 60.0:
            insight = BehavioralInsightCategory.MILD_INTERVIEW_ANXIETY
            ethical_class = EthicalScoringClassification.HIGH_STRESS_SUPPORT_RECOMMENDED
        elif indicators.cognitive_deliberation_ratio >= 0.60:
            insight = BehavioralInsightCategory.COGNITIVELY_DELIBERATING
            ethical_class = EthicalScoringClassification.ASSISTIVE_AFFIRMATIVE
        else:
            insight = BehavioralInsightCategory.COMPOSED_AND_ATTENTIVE
            ethical_class = EthicalScoringClassification.ASSISTIVE_AFFIRMATIVE

        # Evidence Extraction
        positives = []
        if indicators.focus_level >= 75.0:
            positives.append(f"Strong sustained on-screen focus ({indicators.focus_level:.1f}%)")
        if signals.head_telemetry.affirmative_nods_count >= 2:
            positives.append(f"Active conversational listening cues ({signals.head_telemetry.affirmative_nods_count} affirmative nods)")
        if indicators.cognitive_deliberation_ratio >= 0.50:
            positives.append("Demonstrated deliberate cognitive problem-solving gaze patterns")
        if signals.facial_telemetry.smile_authenticity_ratio >= 0.60:
            positives.append("Authentic, natural facial expressiveness and rapport")
        if not positives:
            positives.append("Maintained standard conversational baseline")

        concerns = []
        if indicators.distraction_frequency >= 2.5:
            concerns.append(f"Frequent off-screen gaze diversions ({indicators.distraction_frequency} lookaways/min)")
        if signals.attention_telemetry.multi_monitor_dispersion_detected:
            concerns.append("Repetitive lateral head posture consistent with secondary screen reference")
        if indicators.nervous_gestures_index >= 55.0:
            concerns.append(f"Elevated stress signals detected (Blink rate: {signals.eye_telemetry.blink_rate_per_minute:.0f}/min, Lip compression: {signals.facial_telemetry.lip_compression_index:.2f})")
        if not concerns:
            concerns.append("No abnormal behavioural distractions observed")

        return TurnBehavioralScore(
            turn_index=signals.turn_index,
            indicators=indicators,
            composite_behavioral_score=composite_score,
            deliberation_credit_awarded=deliberation_credit,
            neurodiversity_offset_applied=neurodiversity_offset,
            primary_behavioral_insight=insight,
            ethical_classification=ethical_class,
            observable_positive_evidence=positives,
            observable_concerns_or_gaps=concerns,
        )

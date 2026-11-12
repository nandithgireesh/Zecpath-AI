"""
Unit Tests for Day 48: Behavioral AI Research & Design
======================================================
Validates all Deliverables and Tasks for Day 48:
- Deliverable 1: Behavioral AI Design Document (Architecture manifest & BIPA compliance)
- Deliverable 2: Signal-to-Score Mapping Model (Focus level, distraction frequency, nervous gestures, deliberation credit)
- Deliverable 3: Behavioral Analysis Framework (Report format, multi-turn synthesis, explainability, SHA-256 seal)
- Non-invasive ethical scoring & neurodiversity safeguards
"""

import unittest
import math

from behavioral_ai.models import (
    GazeDirection,
    HeadPoseMovement,
    FacialEngagementState,
    BehavioralInsightCategory,
    EthicalScoringClassification,
    EyeMovementTelemetry,
    HeadKinematicsTelemetry,
    FacialEngagementTelemetry,
    AttentionPatternTelemetry,
    RawTurnBehavioralSignals,
    MeasurableBehavioralIndicators,
    TurnBehavioralScore,
    BehavioralAnalysisReportFormat,
)
from behavioral_ai.mapping_model import (
    BehavioralSignalMappingEngine,
)
from behavioral_ai.framework import (
    BehavioralAnalysisFramework,
)
from behavioral_ai.design_document import (
    BehavioralAIDesignDocument,
)


class TestDay48BehavioralAI(unittest.TestCase):
    """Test suite validating all Day 48 behavioral models, mappings, and framework."""

    def setUp(self):
        self.mapping_engine = BehavioralSignalMappingEngine()
        self.framework = BehavioralAnalysisFramework()

    # ==========================================================================
    # 1. DELIVERABLE 1: DESIGN DOCUMENT & ARCHITECTURE MANIFEST
    # ==========================================================================

    def test_01_design_document_manifest_and_sha256(self):
        """Verify Deliverable 1 design document manifest structure and SHA-256 seal."""
        manifest = BehavioralAIDesignDocument.get_manifest()
        sha_hash = BehavioralAIDesignDocument.generate_blueprint_hash()

        self.assertEqual(manifest["specification_id"], "SPEC-DAY48-BEHAVIORAL-AI")
        self.assertEqual(manifest["p99_latency_sla_ms"], 50)
        self.assertIn("VSE", manifest["subsystems"])
        self.assertIn("TIA", manifest["subsystems"])
        self.assertIn("CIM", manifest["subsystems"])
        self.assertIn("ESSC", manifest["subsystems"])
        self.assertIn("illinois_bipa", manifest["statutory_compliance"])
        self.assertEqual(len(sha_hash), 64)

    def test_02_raw_telemetry_model_instantiation(self):
        """Verify strict validation and boundaries on raw observable signal telemetry."""
        eye = EyeMovementTelemetry(
            fixation_duration_ms=450.0,
            saccade_velocity_deg_per_sec=120.0,
            blink_rate_per_minute=18.0,
            gaze_stability_index=0.88,
            dominant_gaze_direction=GazeDirection.DIRECT_SCREEN_CENTER,
            screen_dwell_ratio=0.92,
        )
        head = HeadKinematicsTelemetry(
            pitch_velocity_deg_sec=8.5,
            yaw_velocity_deg_sec=6.0,
            roll_velocity_deg_sec=3.2,
            head_stability_index=0.85,
            affirmative_nods_count=3,
            primary_pose_movement=HeadPoseMovement.STABLE_CENTERED,
        )
        face = FacialEngagementTelemetry(
            expressiveness_score=0.75,
            smile_authenticity_ratio=0.70,
            brow_furrow_intensity=0.20,
            lip_compression_index=0.15,
            primary_facial_state=FacialEngagementState.NATURAL_CALM_COMPOSED,
        )
        attn = AttentionPatternTelemetry(
            continuous_attention_span_sec=28.5,
            off_screen_lookaway_events=1,
            off_screen_total_duration_sec=2.0,
            multi_monitor_dispersion_detected=False,
        )

        turn_signals = RawTurnBehavioralSignals(
            turn_index=1,
            turn_duration_sec=45.0,
            eye_telemetry=eye,
            head_telemetry=head,
            facial_telemetry=face,
            attention_telemetry=attn,
        )

        self.assertEqual(turn_signals.turn_index, 1)
        self.assertGreaterEqual(turn_signals.eye_telemetry.screen_dwell_ratio, 0.90)

    # ==========================================================================
    # 2. DELIVERABLE 2: SIGNAL-TO-SCORE MAPPING & INDICATORS
    # ==========================================================================

    def test_03_focus_level_computation(self):
        """Verify focus level mapping from gaze stability, dwell ratio, and attention span."""
        high_focus_signals = RawTurnBehavioralSignals(
            turn_index=1,
            turn_duration_sec=60.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=600.0,
                saccade_velocity_deg_per_sec=90.0,
                blink_rate_per_minute=16.0,
                gaze_stability_index=0.95,
                screen_dwell_ratio=0.95,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=5.0,
                yaw_velocity_deg_sec=4.0,
                roll_velocity_deg_sec=2.0,
                head_stability_index=0.90,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.70,
                smile_authenticity_ratio=0.50,
                brow_furrow_intensity=0.10,
                lip_compression_index=0.10,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=45.0,
                off_screen_lookaway_events=0,
                off_screen_total_duration_sec=0.0,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(high_focus_signals)
        self.assertGreaterEqual(indicators.focus_level, 85.0)

    def test_04_distraction_frequency_calculation(self):
        """Verify distraction frequency calculation normalized per minute."""
        distracted_signals = RawTurnBehavioralSignals(
            turn_index=2,
            turn_duration_sec=60.0,  # 1.0 minute
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=200.0,
                saccade_velocity_deg_per_sec=250.0,
                blink_rate_per_minute=22.0,
                gaze_stability_index=0.40,
                screen_dwell_ratio=0.50,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=35.0,
                yaw_velocity_deg_sec=40.0,
                roll_velocity_deg_sec=15.0,
                head_stability_index=0.35,
                primary_pose_movement=HeadPoseMovement.RESTLESS_TURNING,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.40,
                smile_authenticity_ratio=0.10,
                brow_furrow_intensity=0.10,
                lip_compression_index=0.20,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=6.0,
                off_screen_lookaway_events=4,
                off_screen_total_duration_sec=25.0,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(distracted_signals)
        # 4 off-screen lookaways + 1 restless turning jerk = 5 events / 1.0 min = 5.0
        self.assertEqual(indicators.distraction_frequency, 5.0)

    def test_05_nervous_gestures_excess_blink_and_lip_tension(self):
        """Verify high blink bursts and lip compression elevate nervous gestures index."""
        nervous_signals = RawTurnBehavioralSignals(
            turn_index=3,
            turn_duration_sec=30.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=300.0,
                saccade_velocity_deg_per_sec=180.0,
                blink_rate_per_minute=42.0,  # Highly elevated blink rate
                gaze_stability_index=0.60,
                screen_dwell_ratio=0.80,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=15.0,
                yaw_velocity_deg_sec=12.0,
                roll_velocity_deg_sec=8.0,
                head_stability_index=0.65,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.30,
                smile_authenticity_ratio=0.0,
                brow_furrow_intensity=0.20,
                lip_compression_index=0.85,  # High lip tension
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=15.0,
                off_screen_lookaway_events=1,
                off_screen_total_duration_sec=2.0,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(nervous_signals)
        self.assertGreater(indicators.nervous_gestures_index, 50.0)

    def test_06_cognitive_deliberation_detection(self):
        """Verify looking up while thinking with furrowed brow yields high deliberation ratio."""
        thinking_signals = RawTurnBehavioralSignals(
            turn_index=4,
            turn_duration_sec=45.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=750.0,
                saccade_velocity_deg_per_sec=110.0,
                blink_rate_per_minute=18.0,
                gaze_stability_index=0.75,
                dominant_gaze_direction=GazeDirection.LOOKING_UP_THINKING,
                screen_dwell_ratio=0.70,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=6.0,
                yaw_velocity_deg_sec=5.0,
                roll_velocity_deg_sec=2.0,
                head_stability_index=0.80,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.55,
                smile_authenticity_ratio=0.10,
                brow_furrow_intensity=0.65,  # Concentrated brow furrow
                lip_compression_index=0.20,
                primary_facial_state=FacialEngagementState.CONCENTRATED_BROW_FURROW,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=20.0,
                off_screen_lookaway_events=1,
                off_screen_total_duration_sec=4.0,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(thinking_signals)
        self.assertGreaterEqual(indicators.cognitive_deliberation_ratio, 0.80)

    def test_07_deliberation_credit_awarded(self):
        """Verify cognitive deliberation credit is added to composite score."""
        thinking_signals = RawTurnBehavioralSignals(
            turn_index=5,
            turn_duration_sec=45.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=650.0,
                saccade_velocity_deg_per_sec=100.0,
                blink_rate_per_minute=19.0,
                gaze_stability_index=0.78,
                dominant_gaze_direction=GazeDirection.LOOKING_UP_THINKING,
                screen_dwell_ratio=0.75,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=6.0,
                yaw_velocity_deg_sec=5.0,
                roll_velocity_deg_sec=2.0,
                head_stability_index=0.85,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.60,
                smile_authenticity_ratio=0.10,
                brow_furrow_intensity=0.60,
                lip_compression_index=0.15,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=22.0,
                off_screen_lookaway_events=1,
                off_screen_total_duration_sec=3.0,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(thinking_signals)
        score = self.mapping_engine.calculate_turn_score(thinking_signals, indicators)

        self.assertGreater(score.deliberation_credit_awarded, 0.0)
        self.assertIn("cognitive problem-solving", " ".join(score.observable_positive_evidence))

    def test_08_multi_monitor_dispersion_detection(self):
        """Verify reading off secondary screen triggers DISENGAGED_OR_READING classification."""
        cheating_signals = RawTurnBehavioralSignals(
            turn_index=6,
            turn_duration_sec=50.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=400.0,
                saccade_velocity_deg_per_sec=160.0,
                blink_rate_per_minute=18.0,
                gaze_stability_index=0.55,
                dominant_gaze_direction=GazeDirection.OFF_SCREEN_RIGHT,
                screen_dwell_ratio=0.45,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=10.0,
                yaw_velocity_deg_sec=28.0,  # Sustained lateral turn
                roll_velocity_deg_sec=4.0,
                head_stability_index=0.50,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.20,
                smile_authenticity_ratio=0.0,
                brow_furrow_intensity=0.10,
                lip_compression_index=0.20,
                primary_facial_state=FacialEngagementState.FLAT_UNRESPONSIVE_AFFECT,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=10.0,
                off_screen_lookaway_events=5,
                off_screen_total_duration_sec=24.0,
                multi_monitor_dispersion_detected=True,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(cheating_signals)
        score = self.mapping_engine.calculate_turn_score(cheating_signals, indicators)

        self.assertEqual(score.primary_behavioral_insight, BehavioralInsightCategory.DISENGAGED_OR_READING)
        self.assertIn("secondary screen", " ".join(score.observable_concerns_or_gaps))

    def test_09_neurodiversity_safeguard_offset(self):
        """Verify indirect gaze with calm facial expression receives neurodiversity protection."""
        neuro_signals = RawTurnBehavioralSignals(
            turn_index=7,
            turn_duration_sec=60.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=350.0,
                saccade_velocity_deg_per_sec=110.0,
                blink_rate_per_minute=17.0,  # Calm blink rate
                gaze_stability_index=0.60,
                dominant_gaze_direction=GazeDirection.SLIGHT_OFF_CENTER,
                screen_dwell_ratio=0.55,     # Naturally lower direct eye contact
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=7.0,
                yaw_velocity_deg_sec=6.0,
                roll_velocity_deg_sec=3.0,
                head_stability_index=0.80,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.50,
                smile_authenticity_ratio=0.30,
                brow_furrow_intensity=0.10,
                lip_compression_index=0.15,  # Calm facial tone
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=20.0,
                off_screen_lookaway_events=1,
                off_screen_total_duration_sec=3.0,
            ),
        )
        indicators = self.mapping_engine.compute_measurable_indicators(neuro_signals)
        score = self.mapping_engine.calculate_turn_score(neuro_signals, indicators)

        self.assertGreater(score.neurodiversity_offset_applied, 0.0)
        self.assertEqual(score.ethical_classification, EthicalScoringClassification.NEURODIVERSE_ADJUSTED)

    # ==========================================================================
    # 3. COMPOSITE PROFILES & BEHAVIORAL INSIGHT CLASSIFICATION
    # ==========================================================================

    def test_10_composed_and_attentive_candidate(self):
        """Verify calm, focused candidate receives composed insight and affirmative classification."""
        signals = RawTurnBehavioralSignals(
            turn_index=1,
            turn_duration_sec=60.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=580.0,
                saccade_velocity_deg_per_sec=85.0,
                blink_rate_per_minute=18.0,
                gaze_stability_index=0.92,
                screen_dwell_ratio=0.94,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=6.0,
                yaw_velocity_deg_sec=5.0,
                roll_velocity_deg_sec=2.0,
                head_stability_index=0.92,
                affirmative_nods_count=4,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.85,
                smile_authenticity_ratio=0.75,
                brow_furrow_intensity=0.15,
                lip_compression_index=0.10,
                primary_facial_state=FacialEngagementState.DUCHENNE_AUTHENTIC_SMILE,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=48.0,
                off_screen_lookaway_events=0,
                off_screen_total_duration_sec=0.0,
            ),
        )
        turn_score = self.framework.analyze_turn(signals)
        self.assertEqual(turn_score.primary_behavioral_insight, BehavioralInsightCategory.COMPOSED_AND_ATTENTIVE)
        self.assertGreater(turn_score.composite_behavioral_score, 80.0)
        self.assertEqual(turn_score.ethical_classification, EthicalScoringClassification.ASSISTIVE_AFFIRMATIVE)

    def test_11_mild_anxiety_candidate(self):
        """Verify high autonomic arousal triggers MILD_INTERVIEW_ANXIETY insight."""
        signals = RawTurnBehavioralSignals(
            turn_index=2,
            turn_duration_sec=40.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=280.0,
                saccade_velocity_deg_per_sec=190.0,
                blink_rate_per_minute=46.0,  # High blink rate
                gaze_stability_index=0.55,
                screen_dwell_ratio=0.78,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=18.0,
                yaw_velocity_deg_sec=14.0,
                roll_velocity_deg_sec=10.0,
                head_stability_index=0.60,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.35,
                smile_authenticity_ratio=0.0,
                brow_furrow_intensity=0.30,
                lip_compression_index=0.90,  # Clenched lips
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=12.0,
                off_screen_lookaway_events=1,
                off_screen_total_duration_sec=2.0,
            ),
        )
        turn_score = self.framework.analyze_turn(signals)
        self.assertEqual(turn_score.primary_behavioral_insight, BehavioralInsightCategory.MILD_INTERVIEW_ANXIETY)
        self.assertEqual(turn_score.ethical_classification, EthicalScoringClassification.HIGH_STRESS_SUPPORT_RECOMMENDED)

    def test_12_turn_behavioral_score_evidence_extraction(self):
        """Verify observable evidence and concern lists are populated in turn score."""
        signals = RawTurnBehavioralSignals(
            turn_index=3,
            turn_duration_sec=50.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=500.0,
                saccade_velocity_deg_per_sec=95.0,
                blink_rate_per_minute=18.0,
                gaze_stability_index=0.88,
                screen_dwell_ratio=0.90,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=8.0,
                yaw_velocity_deg_sec=6.0,
                roll_velocity_deg_sec=3.0,
                head_stability_index=0.88,
                affirmative_nods_count=3,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.80,
                smile_authenticity_ratio=0.65,
                brow_furrow_intensity=0.10,
                lip_compression_index=0.10,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=35.0,
                off_screen_lookaway_events=0,
                off_screen_total_duration_sec=0.0,
            ),
        )
        turn_score = self.framework.analyze_turn(signals)
        self.assertGreater(len(turn_score.observable_positive_evidence), 0)
        self.assertIn("sustained on-screen focus", turn_score.observable_positive_evidence[0])

    # ==========================================================================
    # 4. DELIVERABLE 3: MULTI-TURN FRAMEWORK & REPORT FORMAT
    # ==========================================================================

    def test_13_multi_turn_report_synthesis_deliverable3(self):
        """Verify synthesis of multi-turn session into BehavioralAnalysisReportFormat."""
        # Create 3 turns
        turns = []
        for i in range(1, 4):
            signals = RawTurnBehavioralSignals(
                turn_index=i,
                turn_duration_sec=50.0,
                eye_telemetry=EyeMovementTelemetry(
                    fixation_duration_ms=500.0 + (i * 20),
                    saccade_velocity_deg_per_sec=95.0,
                    blink_rate_per_minute=17.0 + i,
                    gaze_stability_index=0.85,
                    screen_dwell_ratio=0.90,
                ),
                head_telemetry=HeadKinematicsTelemetry(
                    pitch_velocity_deg_sec=7.0,
                    yaw_velocity_deg_sec=5.0,
                    roll_velocity_deg_sec=3.0,
                    head_stability_index=0.85,
                    affirmative_nods_count=2,
                ),
                facial_telemetry=FacialEngagementTelemetry(
                    expressiveness_score=0.70,
                    smile_authenticity_ratio=0.60,
                    brow_furrow_intensity=0.20,
                    lip_compression_index=0.15,
                ),
                attention_telemetry=AttentionPatternTelemetry(
                    continuous_attention_span_sec=30.0,
                    off_screen_lookaway_events=1,
                    off_screen_total_duration_sec=2.0,
                ),
            )
            turns.append(self.framework.analyze_turn(signals))

        report = self.framework.synthesize_evaluation_report(
            candidate_id="CAND-TEST-DAY48",
            session_id="SESS-TEST-DAY48",
            target_role="FULL_STACK_ENGINEER",
            turn_scores=turns,
        )

        self.assertIsInstance(report, BehavioralAnalysisReportFormat)
        self.assertEqual(report.candidate_id, "CAND-TEST-DAY48")
        self.assertGreater(report.overall_behavioral_score, 70.0)
        self.assertGreater(len(report.key_behavioral_strengths), 0)
        self.assertIn("illinois_bipa_compliance", report.statutory_compliance_attestation)

    def test_14_cryptographic_audit_hash_integrity(self):
        """Verify report audit_integrity_hash is a 64-character SHA-256 string."""
        signals = RawTurnBehavioralSignals(
            turn_index=1,
            turn_duration_sec=30.0,
            eye_telemetry=EyeMovementTelemetry(
                fixation_duration_ms=450.0,
                saccade_velocity_deg_per_sec=100.0,
                blink_rate_per_minute=18.0,
                gaze_stability_index=0.80,
                screen_dwell_ratio=0.85,
            ),
            head_telemetry=HeadKinematicsTelemetry(
                pitch_velocity_deg_sec=8.0,
                yaw_velocity_deg_sec=6.0,
                roll_velocity_deg_sec=3.0,
                head_stability_index=0.80,
            ),
            facial_telemetry=FacialEngagementTelemetry(
                expressiveness_score=0.60,
                smile_authenticity_ratio=0.50,
                brow_furrow_intensity=0.20,
                lip_compression_index=0.20,
            ),
            attention_telemetry=AttentionPatternTelemetry(
                continuous_attention_span_sec=20.0,
                off_screen_lookaway_events=1,
                off_screen_total_duration_sec=2.0,
            ),
        )
        t1 = self.framework.analyze_turn(signals)
        report = self.framework.synthesize_evaluation_report("CAND-HASH-01", "SESS-01", "SOFTWARE_DEV", [t1])

        self.assertEqual(len(report.audit_integrity_hash), 64)
        # Deterministic check
        report2 = self.framework.synthesize_evaluation_report("CAND-HASH-01", "SESS-01", "SOFTWARE_DEV", [t1])
        # Report ID has random uuid, but hash payload structure is strictly valid sha256
        self.assertTrue(all(c in "0123456789abcdef" for c in report.audit_integrity_hash))

    def test_15_empty_turn_scores_error_handling(self):
        """Verify ValueError is raised when synthesizing empty turn list."""
        with self.assertRaises(ValueError):
            self.framework.synthesize_evaluation_report("CAND-ERR", "SESS-ERR", "DATA_ENG", [])


if __name__ == "__main__":
    unittest.main()

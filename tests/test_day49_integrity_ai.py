"""
Unit Test Suite for Day 49: Malpractice & Integrity Detection Design
====================================================================
Tests all detailed tasks:
- Malpractice signals (tab switching, focus loss, external voice, looking away)
- Detection logic (threshold flags, pattern recognition)
- Warning & flagging system (real-time alerts, interview risk tagging)
- Behavioral signals integration (Day 48 cognitive deliberation & neurodiversity)
- Deliverable 1, 2, and 3 schema validation and cryptographic audit seals
"""

import unittest
from integrity_ai.models import (
    MalpracticeSignalType,
    FlagSeverity,
    AlertTierLevel,
    InterviewRiskTag,
    BrowserActivityTelemetry,
    AcousticIntegrityTelemetry,
    VisualIntegrityTelemetry,
    RawTurnIntegritySignals,
    IntegrityFlag,
    TurnIntegrityScore,
    IntegrityEvaluationReportFormat,
)
from integrity_ai.detection_logic import (
    ThresholdDetectionEngine,
    PatternRecognitionEngine,
    MalpracticeDetectionEngine,
)
from integrity_ai.risk_engine import (
    WarningEscalationStateMachine,
    InterviewRiskTagger,
)
from integrity_ai.framework import IntegrityDetectionFramework


class TestDay49IntegrityAI(unittest.TestCase):

    def setUp(self):
        self.framework = IntegrityDetectionFramework()
        self.detection_engine = MalpracticeDetectionEngine()

    def test_01_framework_manifest_and_hash(self):
        manifest = IntegrityDetectionFramework.get_architecture_manifest()
        self.assertEqual(manifest["framework_id"], "FRAMEWORK-DAY49-INTEGRITY-AI")
        self.assertLessEqual(manifest["p99_latency_sla_ms"], 45)
        self.assertIn("STAGE_2_LOGIC", manifest["pipeline_stages"])

        blueprint_hash = IntegrityDetectionFramework.generate_blueprint_hash()
        self.assertEqual(len(blueprint_hash), 64)

    def test_02_browser_telemetry_models(self):
        browser = BrowserActivityTelemetry(
            tab_switch_count=3,
            loss_of_focus_count=2,
            cumulative_unfocused_time_sec=4.5,
            clipboard_paste_count=1,
            devtools_open_flag=False,
            fullscreen_exit_count=0,
        )
        self.assertEqual(browser.tab_switch_count, 3)
        self.assertEqual(browser.cumulative_unfocused_time_sec, 4.5)

    def test_03_acoustic_telemetry_models(self):
        acoustic = AcousticIntegrityTelemetry(
            secondary_speaker_detected=True,
            secondary_speaker_confidence=0.88,
            background_whisper_detected=False,
            audio_overlap_duration_sec=2.4,
            ambient_snr_db=32.0,
        )
        self.assertTrue(acoustic.secondary_speaker_detected)
        self.assertAlmostEqual(acoustic.secondary_speaker_confidence, 0.88)

    def test_04_visual_telemetry_models(self):
        visual = VisualIntegrityTelemetry(
            repeated_looking_away_count=4,
            lateral_yaw_lookaways_count=3,
            continuous_off_screen_duration_sec=5.2,
            multiple_faces_detected=False,
            absence_from_camera_sec=0.0,
        )
        self.assertEqual(visual.repeated_looking_away_count, 4)
        self.assertEqual(visual.lateral_yaw_lookaways_count, 3)

    def test_05_threshold_tab_switch_warning_and_critical(self):
        engine = ThresholdDetectionEngine()

        # Warning level (2 switches)
        sig_warn = RawTurnIntegritySignals(
            turn_index=1,
            browser_telemetry=BrowserActivityTelemetry(tab_switch_count=2),
        )
        flags_warn, _ = engine.evaluate_thresholds(sig_warn)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.TAB_SWITCH_BURST and f.severity == FlagSeverity.WARNING for f in flags_warn))

        # Critical level (4 switches)
        sig_crit = RawTurnIntegritySignals(
            turn_index=2,
            browser_telemetry=BrowserActivityTelemetry(tab_switch_count=5),
        )
        flags_crit, _ = engine.evaluate_thresholds(sig_crit)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.TAB_SWITCH_BURST and f.severity == FlagSeverity.CRITICAL for f in flags_crit))

    def test_06_threshold_loss_of_focus(self):
        engine = ThresholdDetectionEngine()
        sig = RawTurnIntegritySignals(
            turn_index=1,
            browser_telemetry=BrowserActivityTelemetry(cumulative_unfocused_time_sec=9.0),
        )
        flags, _ = engine.evaluate_thresholds(sig)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.LOSS_OF_SCREEN_FOCUS and f.severity == FlagSeverity.CRITICAL for f in flags))

    def test_07_threshold_external_voice(self):
        engine = ThresholdDetectionEngine()
        sig = RawTurnIntegritySignals(
            turn_index=1,
            acoustic_telemetry=AcousticIntegrityTelemetry(
                secondary_speaker_detected=True,
                secondary_speaker_confidence=0.78,
            ),
        )
        flags, _ = engine.evaluate_thresholds(sig)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.EXTERNAL_VOICE_COLLUSION and f.severity == FlagSeverity.CRITICAL for f in flags))

    def test_08_behavioral_bridge_deliberation_exoneration(self):
        # Candidate looks away repeatedly, BUT Day 48 deliberation ratio is 0.75 (deep problem solving)
        sig = RawTurnIntegritySignals(
            turn_index=1,
            visual_telemetry=VisualIntegrityTelemetry(
                repeated_looking_away_count=5,
                continuous_off_screen_duration_sec=6.0,
            ),
            day48_cognitive_deliberation_ratio=0.75,
        )
        engine = ThresholdDetectionEngine()
        flags, exonerations = engine.evaluate_thresholds(sig)

        # MUST NOT flag looking away as malpractice!
        self.assertFalse(any(f.signal_type == MalpracticeSignalType.REPEATED_OFF_SCREEN_LOOKAWAY for f in flags))
        self.assertTrue(len(exonerations) > 0)
        self.assertIn("Cognitive Deliberation", exonerations[0])

    def test_09_behavioral_bridge_neurodiversity_safeguard(self):
        # Candidate has neurodiversity safeguard active
        sig = RawTurnIntegritySignals(
            turn_index=1,
            visual_telemetry=VisualIntegrityTelemetry(
                repeated_looking_away_count=4,
                continuous_off_screen_duration_sec=5.0,
            ),
            day48_neurodiversity_safeguard_active=True,
        )
        engine = ThresholdDetectionEngine()
        flags, exonerations = engine.evaluate_thresholds(sig)
        self.assertFalse(any(f.signal_type == MalpracticeSignalType.REPEATED_OFF_SCREEN_LOOKAWAY for f in flags))
        self.assertTrue(len(exonerations) > 0)
        self.assertIn("Neurodiversity Safeguard", exonerations[0])

    def test_10_unauthorized_looking_away_flagged(self):
        # Candidate looks away repeatedly WITHOUT deliberation or neurodiversity
        sig = RawTurnIntegritySignals(
            turn_index=1,
            visual_telemetry=VisualIntegrityTelemetry(
                repeated_looking_away_count=4,
                continuous_off_screen_duration_sec=5.0,
            ),
            day48_cognitive_deliberation_ratio=0.10,
            day48_neurodiversity_safeguard_active=False,
        )
        engine = ThresholdDetectionEngine()
        flags, exonerations = engine.evaluate_thresholds(sig)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.REPEATED_OFF_SCREEN_LOOKAWAY for f in flags))
        self.assertEqual(len(exonerations), 0)

    def test_11_temporal_pattern_prompt_assist(self):
        # Question delivered -> Tab switch -> Clipboard paste / whisper sequence
        sig = RawTurnIntegritySignals(
            turn_index=1,
            browser_telemetry=BrowserActivityTelemetry(tab_switch_count=1, clipboard_paste_count=1),
        )
        pattern_engine = PatternRecognitionEngine()
        flags = pattern_engine.evaluate_patterns(sig)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.TEMPORAL_PATTERN_PROMPT_ASSIST for f in flags))

    def test_12_temporal_pattern_lateral_collusion(self):
        # Lateral yaw lookaway correlated with secondary audio stream
        sig = RawTurnIntegritySignals(
            turn_index=1,
            visual_telemetry=VisualIntegrityTelemetry(lateral_yaw_lookaways_count=3),
            acoustic_telemetry=AcousticIntegrityTelemetry(secondary_speaker_detected=True),
        )
        pattern_engine = PatternRecognitionEngine()
        flags = pattern_engine.evaluate_patterns(sig)
        self.assertTrue(any(f.signal_type == MalpracticeSignalType.LATERAL_PERIPHERY_COLLUSION for f in flags))

    def test_13_progressive_warning_state_machine(self):
        sm = WarningEscalationStateMachine()

        # Turn 1: 1 warning flag -> TIER_1_ADVISORY
        f1 = [IntegrityFlag(
            flag_id="F1", signal_type=MalpracticeSignalType.TAB_SWITCH_BURST,
            severity=FlagSeverity.WARNING, detection_rule="R1",
            confidence_score=0.8, turn_index=1, evidence_details="test"
        )]
        a1 = sm.evaluate_escalation(f1, cumulative_risk=22.0)
        self.assertEqual(sm.current_tier, AlertTierLevel.TIER_1_ADVISORY)
        self.assertFalse(a1.escalated_to_proctor)

        # Turn 2: 1 critical flag -> TIER_2_FORMAL_WARNING
        f2 = [IntegrityFlag(
            flag_id="F2", signal_type=MalpracticeSignalType.EXTERNAL_VOICE_COLLUSION,
            severity=FlagSeverity.CRITICAL, detection_rule="R2",
            confidence_score=0.9, turn_index=2, evidence_details="test"
        )]
        a2 = sm.evaluate_escalation(f2, cumulative_risk=55.0)
        self.assertEqual(sm.current_tier, AlertTierLevel.TIER_2_FORMAL_WARNING)

        # Turn 3: 2nd critical flag -> TIER_3_AUDIT_ESCALATION
        f3 = [IntegrityFlag(
            flag_id="F3", signal_type=MalpracticeSignalType.MULTI_PERSON_ON_CAMERA,
            severity=FlagSeverity.CRITICAL, detection_rule="R3",
            confidence_score=0.95, turn_index=3, evidence_details="test"
        )]
        a3 = sm.evaluate_escalation(f3, cumulative_risk=85.0)
        self.assertEqual(sm.current_tier, AlertTierLevel.TIER_3_AUDIT_ESCALATION)
        self.assertTrue(a3.escalated_to_proctor)

    def test_14_interview_risk_tagging(self):
        tag_clean, _ = InterviewRiskTagger.assign_session_risk_tag(10.0, 0, 0)
        self.assertEqual(tag_clean, InterviewRiskTag.LOW_RISK_VERIFIED)

        tag_mod, _ = InterviewRiskTagger.assign_session_risk_tag(35.0, 1, 0)
        self.assertEqual(tag_mod, InterviewRiskTag.MODERATE_FLAGGED_REVIEW)

        tag_high, _ = InterviewRiskTagger.assign_session_risk_tag(75.0, 2, 1)
        self.assertEqual(tag_high, InterviewRiskTag.HIGH_RISK_TERMINATE_RECOMMENDED)

    def test_15_full_session_synthesis_and_audit_hash(self):
        # 3 turns session
        sig1 = RawTurnIntegritySignals(turn_index=1)
        sig2 = RawTurnIntegritySignals(
            turn_index=2,
            visual_telemetry=VisualIntegrityTelemetry(repeated_looking_away_count=4),
            day48_cognitive_deliberation_ratio=0.80, # Exonerated
        )
        sig3 = RawTurnIntegritySignals(turn_index=3)

        t1 = self.framework.process_turn(sig1)
        t2 = self.framework.process_turn(sig2)
        t3 = self.framework.process_turn(sig3)

        report = self.framework.synthesize_session_report(
            candidate_id="CAND-TEST-4901",
            session_id="SESS-TEST-4901",
            target_role="Software Architect",
            turn_scores=[t1, t2, t3],
        )

        self.assertIsInstance(report, IntegrityEvaluationReportFormat)
        self.assertEqual(report.session_risk_tag, InterviewRiskTag.LOW_RISK_VERIFIED)
        self.assertGreaterEqual(report.overall_integrity_score, 90.0)
        self.assertEqual(len(report.audit_integrity_hash), 64)
        self.assertTrue(len(report.exonerated_behavioral_events) > 0)


if __name__ == "__main__":
    unittest.main()

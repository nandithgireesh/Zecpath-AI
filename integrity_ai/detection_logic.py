"""
Day 49 Deliverable 2: Malpractice Detection Logic
=================================================
Algorithmic engines implementing threshold-based rules, multi-signal temporal
pattern recognition, and seamless integration with Day 48 behavioral models.

Curriculum Reference: Day 49 - Deliverable 2: Malpractice Detection Logic
Tasks:
- Define malpractice signals (tab switching, focus loss, external voice, looking away)
- Design detection logic (threshold flags, temporal pattern recognition)
- Integrate behavioral signals (Day 48 cognitive deliberation exemption)
"""

import uuid
from typing import List, Tuple, Dict, Any

from integrity_ai.models import (
    MalpracticeSignalType,
    FlagSeverity,
    RawTurnIntegritySignals,
    IntegrityFlag,
)


class ThresholdDetectionEngine:
    """
    Evaluates discrete mathematical boundary thresholds across browser telemetry,
    acoustic diarization, and visual kinematics.
    """

    TAB_SWITCH_WARN_THRESHOLD = 2
    TAB_SWITCH_CRITICAL_THRESHOLD = 4
    UNFOCUSED_TIME_WARN_SEC = 3.5
    UNFOCUSED_TIME_CRITICAL_SEC = 8.0
    SPEAKER_DIARIZATION_CONF_THRESHOLD = 0.65
    OFF_SCREEN_LOOKAWAY_THRESHOLD = 3
    OFF_SCREEN_DURATION_WARN_SEC = 4.0

    def evaluate_thresholds(
        self,
        signals: RawTurnIntegritySignals,
    ) -> Tuple[List[IntegrityFlag], List[str]]:
        """
        Runs threshold checks against turn telemetry.
        Returns:
            Tuple of (raised_flags, exonerated_events)
        """
        flags: List[IntegrityFlag] = []
        exonerations: List[str] = []
        turn = signals.turn_index

        browser = signals.browser_telemetry
        acoustic = signals.acoustic_telemetry
        visual = signals.visual_telemetry

        # 1. Tab Switching Frequency Threshold
        if browser.tab_switch_count >= self.TAB_SWITCH_CRITICAL_THRESHOLD:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-TAB-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.TAB_SWITCH_BURST,
                severity=FlagSeverity.CRITICAL,
                detection_rule="TH_TAB_SWITCH_CRITICAL",
                confidence_score=0.95,
                turn_index=turn,
                evidence_details=f"Severe tab switching activity: {browser.tab_switch_count} switches in {signals.turn_duration_sec:.0f}s window.",
            ))
        elif browser.tab_switch_count >= self.TAB_SWITCH_WARN_THRESHOLD:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-TAB-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.TAB_SWITCH_BURST,
                severity=FlagSeverity.WARNING,
                detection_rule="TH_TAB_SWITCH_WARN",
                confidence_score=0.85,
                turn_index=turn,
                evidence_details=f"Excessive tab switching: {browser.tab_switch_count} switches during prompt answering.",
            ))

        # 2. Loss of Screen Focus Threshold
        if browser.cumulative_unfocused_time_sec >= self.UNFOCUSED_TIME_CRITICAL_SEC:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-FOC-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.LOSS_OF_SCREEN_FOCUS,
                severity=FlagSeverity.CRITICAL,
                detection_rule="TH_FOCUS_LOSS_CRITICAL",
                confidence_score=0.96,
                turn_index=turn,
                evidence_details=f"Prolonged loss of screen focus: {browser.cumulative_unfocused_time_sec:.1f}s outside interview window.",
            ))
        elif browser.cumulative_unfocused_time_sec >= self.UNFOCUSED_TIME_WARN_SEC:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-FOC-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.LOSS_OF_SCREEN_FOCUS,
                severity=FlagSeverity.WARNING,
                detection_rule="TH_FOCUS_LOSS_WARN",
                confidence_score=0.86,
                turn_index=turn,
                evidence_details=f"Window blur detected: {browser.cumulative_unfocused_time_sec:.1f}s unfocused duration.",
            ))

        # 3. External Voice Detection Threshold
        if acoustic.secondary_speaker_detected and acoustic.secondary_speaker_confidence >= self.SPEAKER_DIARIZATION_CONF_THRESHOLD:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-VOX-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.EXTERNAL_VOICE_COLLUSION,
                severity=FlagSeverity.CRITICAL,
                detection_rule="TH_EXTERNAL_VOICE_CONFIRMED",
                confidence_score=round(acoustic.secondary_speaker_confidence, 2),
                turn_index=turn,
                evidence_details=f"Secondary human speaker isolated in room with {acoustic.secondary_speaker_confidence*100:.1f}% confidence.",
            ))
        elif acoustic.background_whisper_detected:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-WHISPER-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.WHISPERED_AUDIO_PROMPT,
                severity=FlagSeverity.WARNING,
                detection_rule="TH_WHISPER_AUDIO_ENERGY",
                confidence_score=0.80,
                turn_index=turn,
                evidence_details="Low-amplitude whispered acoustic assistance isolated near microphone.",
            ))

        # 4. Repeated Looking Away Threshold with Day 48 Behavioral Bridge
        has_excessive_lookaways = (
            visual.repeated_looking_away_count >= self.OFF_SCREEN_LOOKAWAY_THRESHOLD or
            visual.continuous_off_screen_duration_sec >= self.OFF_SCREEN_DURATION_WARN_SEC
        )

        if has_excessive_lookaways:
            # INTEGRATION WITH DAY 48 BEHAVIORAL MODEL:
            # If candidate was looking up/away to deeply contemplate complex code,
            # OR has neurodiverse gaze safeguard active, exonerate from cheating flags!
            is_deliberating = signals.day48_cognitive_deliberation_ratio >= 0.50
            is_neurodiverse = signals.day48_neurodiversity_safeguard_active

            if is_deliberating:
                exonerations.append(
                    f"Turn {turn}: Off-screen gaze exonerated as authentic Cognitive Deliberation "
                    f"(Day 48 Deliberation Ratio: {signals.day48_cognitive_deliberation_ratio:.2f})."
                )
            elif is_neurodiverse:
                exonerations.append(
                    f"Turn {turn}: Indirect gaze exonerated under Day 48 Neurodiversity Safeguard Policy."
                )
            else:
                severity = FlagSeverity.CRITICAL if visual.continuous_off_screen_duration_sec >= 7.0 else FlagSeverity.WARNING
                flags.append(IntegrityFlag(
                    flag_id=f"FLG-GAZE-{uuid.uuid4().hex[:6].upper()}",
                    signal_type=MalpracticeSignalType.REPEATED_OFF_SCREEN_LOOKAWAY,
                    severity=severity,
                    detection_rule="TH_OFF_SCREEN_GAZE",
                    confidence_score=0.84,
                    turn_index=turn,
                    evidence_details=(
                        f"Repeated off-screen gaze ({visual.repeated_looking_away_count} lookaways, "
                        f"max {visual.continuous_off_screen_duration_sec:.1f}s) without cognitive deliberation markers."
                    ),
                ))

        # 5. Unauthorized Multi-Person or Clipboard Paste
        if visual.multiple_faces_detected:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-MULTI-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.MULTI_PERSON_ON_CAMERA,
                severity=FlagSeverity.CRITICAL,
                detection_rule="TH_MULTIPLE_FACES_DETECTED",
                confidence_score=0.98,
                turn_index=turn,
                evidence_details="Multiple human faces identified in webcam visual frame concurrently.",
            ))

        if browser.clipboard_paste_count >= 2:
            flags.append(IntegrityFlag(
                flag_id=f"FLG-PASTE-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.SUSPICIOUS_CLIPBOARD_PASTE,
                severity=FlagSeverity.WARNING,
                detection_rule="TH_SUSPICIOUS_CLIPBOARD_PASTE",
                confidence_score=0.82,
                turn_index=turn,
                evidence_details=f"Multiple external clipboard paste events ({browser.clipboard_paste_count} pastes) during coding prompt.",
            ))

        return flags, exonerations


class PatternRecognitionEngine:
    """
    Identifies multi-modal temporal correlations that indicate organized
    or clandestine external assistance during the interview.
    """

    def evaluate_patterns(
        self,
        signals: RawTurnIntegritySignals,
    ) -> List[IntegrityFlag]:
        """
        Analyzes cross-channel temporal clustering across browser, audio, and visual cues.
        """
        pattern_flags: List[IntegrityFlag] = []
        turn = signals.turn_index

        browser = signals.browser_telemetry
        acoustic = signals.acoustic_telemetry
        visual = signals.visual_telemetry

        # PATTERN 1: Prompt-Assistance-Paste Sequence
        # Condition: Tab switch occurs followed by clipboard paste OR background whisper
        has_tab_switch = browser.tab_switch_count >= 1 or browser.loss_of_focus_count >= 1
        has_paste_or_whisper = browser.clipboard_paste_count >= 1 or acoustic.background_whisper_detected

        if has_tab_switch and has_paste_or_whisper:
            pattern_flags.append(IntegrityFlag(
                flag_id=f"PAT-ASSIST-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.TEMPORAL_PATTERN_PROMPT_ASSIST,
                severity=FlagSeverity.CRITICAL,
                detection_rule="PATTERN_PROMPT_ASSIST_PASTE",
                confidence_score=0.94,
                turn_index=turn,
                evidence_details="Temporal correlation: Tab switch immediately correlated with external paste/whisper assistance sequence.",
            ))

        # PATTERN 2: Lateral Periphery Collusion
        # Condition: High lateral head yaw lookaway correlated with secondary audio stream
        has_lateral_gaze = visual.lateral_yaw_lookaways_count >= 2
        has_audio_collusion = acoustic.secondary_speaker_detected or acoustic.background_whisper_detected

        if has_lateral_gaze and has_audio_collusion:
            pattern_flags.append(IntegrityFlag(
                flag_id=f"PAT-COLLUDE-{uuid.uuid4().hex[:6].upper()}",
                signal_type=MalpracticeSignalType.LATERAL_PERIPHERY_COLLUSION,
                severity=FlagSeverity.CRITICAL,
                detection_rule="PATTERN_SIDE_PERIPHERY_AUDIO",
                confidence_score=0.93,
                turn_index=turn,
                evidence_details="Coincident lateral peripheral glances (>35 deg yaw) correlated with secondary speaker audio.",
            ))

        return pattern_flags


class MalpracticeDetectionEngine:
    """
    Coordinates threshold detection and pattern recognition to evaluate
    turn-level integrity incidents and compute mathematical risk metrics.
    """

    def __init__(self):
        self.threshold_engine = ThresholdDetectionEngine()
        self.pattern_engine = PatternRecognitionEngine()

    def analyze_turn_signals(
        self,
        signals: RawTurnIntegritySignals,
    ) -> Tuple[List[IntegrityFlag], List[str], float, float]:
        """
        Executes complete detection logic pipeline for a turn.
        Returns:
            Tuple of (all_flags, exonerations, turn_risk_score, turn_integrity_index)
        """
        th_flags, exonerations = self.threshold_engine.evaluate_thresholds(signals)
        pat_flags = self.pattern_engine.evaluate_patterns(signals)
        all_flags = th_flags + pat_flags

        # Mathematical Risk Calculation (0.0 to 100.0)
        # Weights: Info: 10 pts, Warning: 25 pts, Critical: 45 pts, Patterns: +20 pts
        raw_risk = 0.0
        for flag in all_flags:
            if flag.severity == FlagSeverity.INFO:
                raw_risk += 10.0 * flag.confidence_score
            elif flag.severity == FlagSeverity.WARNING:
                raw_risk += 25.0 * flag.confidence_score
            elif flag.severity == FlagSeverity.CRITICAL:
                raw_risk += 45.0 * flag.confidence_score

        # Pattern synergy multiplier if multiple independent channels triggered
        has_browser_flag = any(f.signal_type in (MalpracticeSignalType.TAB_SWITCH_BURST, MalpracticeSignalType.LOSS_OF_SCREEN_FOCUS) for f in all_flags)
        has_audio_flag = any(f.signal_type in (MalpracticeSignalType.EXTERNAL_VOICE_COLLUSION, MalpracticeSignalType.WHISPERED_AUDIO_PROMPT) for f in all_flags)
        has_visual_flag = any(f.signal_type in (MalpracticeSignalType.REPEATED_OFF_SCREEN_LOOKAWAY, MalpracticeSignalType.LATERAL_PERIPHERY_COLLUSION) for f in all_flags)

        active_channels = sum([1 for c in [has_browser_flag, has_audio_flag, has_visual_flag] if c])
        if active_channels >= 2:
            raw_risk *= 1.35  # Cross-channel collusion penalty

        turn_risk = round(min(100.0, max(0.0, raw_risk)), 1)
        turn_integrity = round(max(0.0, 100.0 - turn_risk), 1)

        return all_flags, exonerations, turn_risk, turn_integrity

"""
Day 31: Resilient Call Flow Controller
======================================
Unified coordinator executing end-to-end edge-case and failure handling:
1. Acoustic Evaluation (AudioConditionHandler) -> SNR, Clipping, Packet Loss, Noise.
2. Code-Switching Normalization (LanguageMixingNormalizer) -> Hinglish to English.
3. Non-Response Assessment (MissingAnswerHandler) -> Silence, Fillers, Passes.
4. Circuit Breaker & Safety Net (SafetyFallbackEngine) -> Retries, Degradation, Human Escalation.
"""

from typing import Dict, Any, Optional, Tuple, List
from screening_ai.failure_models import (
    AudioTelemetry,
    AudioDegradationType,
    NoiseEnvironmentType,
    LanguageMixingCategory,
    CodeSwitchResult,
    MissingAnswerAssessment,
    MissingAnswerType,
    RetryDecision,
    ClarificationAction,
    SafetyDegradationTier,
    FailureSeverity,
    SafetyHandoffPacket,
    ResilientTurnResult,
)
from screening_ai.audio_condition_handler import AudioConditionHandler
from screening_ai.language_mixing_normalizer import LanguageMixingNormalizer
from screening_ai.missing_answer_handler import MissingAnswerHandler
from screening_ai.safety_fallback_engine import SafetyFallbackEngine


class ResilientCallFlowCoordinator:
    """
    Coordinates real-time acoustic, linguistic, and conversational edge-case resolution.
    Ensures zero crashes, fair scoring for non-native/noisy lines, and reliable escalation.
    """

    def __init__(self, session_id: str, candidate_id: str):
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.safety_engine = SafetyFallbackEngine(session_id, candidate_id)
        self.consecutive_missing = 0
        self.handoff_packet: Optional[SafetyHandoffPacket] = None

    def evaluate_turn(
        self,
        turn_id: int,
        utterance: str,
        question_id: str,
        topic: str = "your technical background",
        next_topic: str = "the next subject",
        snr_db: float = 26.0,
        peak_amplitude_dbfs: float = -12.0,
        packet_loss_rate: float = 0.0,
        clipping_events: int = 0,
        codec_bitrate_kbps: float = 64.0,
        noise_hints: Optional[Dict[str, Any]] = None,
        duration_ms: int = 4500,
    ) -> ResilientTurnResult:
        """
        Executes complete multi-stage edge-case analysis on an incoming candidate turn.
        """
        audit_flags: List[str] = []

        # ----------------------------------------------------
        # STAGE 1: Acoustic Quality & Background Noise Gate
        # ----------------------------------------------------
        telemetry = AudioConditionHandler.evaluate_telemetry(
            snr_db=snr_db,
            peak_amplitude_dbfs=peak_amplitude_dbfs,
            packet_loss_rate=packet_loss_rate,
            clipping_events=clipping_events,
            codec_bitrate_kbps=codec_bitrate_kbps,
            noise_hints=noise_hints,
        )

        if telemetry.estimated_audio_degradation != AudioDegradationType.NORMAL:
            audit_flags.append(f"ACOUSTIC_{telemetry.estimated_audio_degradation.value}")

        if telemetry.estimated_noise_type != NoiseEnvironmentType.QUIET:
            audit_flags.append(f"NOISE_{telemetry.estimated_noise_type.value}")

        # Check for immediate acoustic retry condition
        needs_acoustic_retry, acoustic_action, acoustic_prompt = (
            AudioConditionHandler.should_request_acoustic_retry(telemetry)
        )

        if needs_acoustic_retry:
            tier, decision, handoff = self.safety_engine.record_failure(
                question_id=question_id,
                failure_type=f"ACOUSTIC:{telemetry.estimated_audio_degradation.value}",
                severity=FailureSeverity.MEDIUM,
            )
            if handoff:
                self.handoff_packet = handoff

            # Override prompt with targeted acoustic instruction if not escalated
            if decision and not decision.escalation_required and acoustic_prompt:
                decision.prompt_message = acoustic_prompt
                decision.action = acoustic_action or decision.action

            return ResilientTurnResult(
                turn_id=turn_id,
                original_text=utterance,
                normalized_text="",
                audio_telemetry=telemetry,
                code_switch_result=LanguageMixingNormalizer.analyze_and_normalize(utterance),
                missing_answer_result=None,
                retry_decision=decision,
                safety_tier=tier,
                is_safe_to_advance=False,
                system_response=decision.prompt_message if decision else acoustic_prompt,
                audit_flags=audit_flags + ["ACOUSTIC_RETRY_REQUESTED"],
            )

        # ----------------------------------------------------
        # STAGE 2: Language Mixing & Code-Switching Normalization
        # ----------------------------------------------------
        code_switch = LanguageMixingNormalizer.analyze_and_normalize(utterance)
        normalized_text = code_switch.normalized_english_text

        if code_switch.detected_category != LanguageMixingCategory.MONOLINGUAL_ENGLISH:
            audit_flags.append(f"CODE_SWITCH_{code_switch.detected_category.value}")
            if code_switch.extracted_entities:
                audit_flags.append("ENTITIES_RESOLVED_FROM_HINGLISH")

        # ----------------------------------------------------
        # STAGE 3: Missing Answer & Non-Response Assessment
        # ----------------------------------------------------
        missing_assess = MissingAnswerHandler.assess_response(
            text=normalized_text,
            duration_ms=duration_ms,
            consecutive_missing_count=self.consecutive_missing,
            topic=topic,
            next_topic=next_topic,
        )

        is_missing = (
            missing_assess.is_silence
            or missing_assess.is_empty_filler
            or missing_assess.is_explicit_pass
            or missing_assess.is_evasive
        )

        if is_missing:
            self.consecutive_missing += 1
            audit_flags.append(f"MISSING_{missing_assess.category.value}")

            tier, decision, handoff = self.safety_engine.record_failure(
                question_id=question_id,
                failure_type=f"MISSING:{missing_assess.category.value}",
                severity=FailureSeverity.MEDIUM if not missing_assess.is_explicit_pass else FailureSeverity.LOW,
            )
            if handoff:
                self.handoff_packet = handoff

            # For explicit passes or exhausted retries, advance to next question
            is_advance = (
                missing_assess.is_explicit_pass
                or (decision and decision.action == ClarificationAction.POLITE_SKIP)
                or (decision and decision.retry_budget_remaining == 0)
            )

            prompt = (
                decision.prompt_message
                if decision
                else (missing_assess.recovery_prompt or "Let's move on to the next topic.")
            )

            # Record turn in audit trail
            self.safety_engine.record_turn("candidate", utterance, {"flags": audit_flags})
            self.safety_engine.record_turn("agent", prompt, {"tier": tier.value})

            return ResilientTurnResult(
                turn_id=turn_id,
                original_text=utterance,
                normalized_text=normalized_text,
                audio_telemetry=telemetry,
                code_switch_result=code_switch,
                missing_answer_result=missing_assess,
                retry_decision=decision,
                safety_tier=tier,
                is_safe_to_advance=is_advance,
                system_response=prompt,
                audit_flags=audit_flags,
            )

        # ----------------------------------------------------
        # STAGE 4: Informative, Valid Answer Captured
        # ----------------------------------------------------
        self.consecutive_missing = 0
        self.safety_engine.record_success(question_id)

        response = "Thank you for explaining that. Let's proceed."
        self.safety_engine.record_turn("candidate", utterance, {"flags": audit_flags})
        self.safety_engine.record_turn("agent", response, {"status": "SUCCESS"})

        return ResilientTurnResult(
            turn_id=turn_id,
            original_text=utterance,
            normalized_text=normalized_text,
            audio_telemetry=telemetry,
            code_switch_result=code_switch,
            missing_answer_result=missing_assess,
            retry_decision=None,
            safety_tier=SafetyDegradationTier.NORMAL_FLOW,
            is_safe_to_advance=True,
            system_response=response,
            audit_flags=audit_flags + ["NORMAL_ADVANCE"],
        )

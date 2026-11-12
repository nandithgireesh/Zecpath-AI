"""
Day 31: Audio Condition & Noise Gate Handler
============================================
Analyzes acoustic telemetry in real time:
- Evaluates Signal-to-Noise Ratio (SNR), amplitude, clipping, and packet loss.
- Categorizes background noise (Stationary hum, Traffic honking, Office babble, Typing).
- Calculates acoustic confidence discounts to protect candidates from unfair scoring penalties.
- Generates targeted telephonic clarification prompts based on acoustic root cause.
"""

from typing import Tuple, Dict, Any, Optional
from screening_ai.failure_models import (
    AudioTelemetry,
    AudioDegradationType,
    NoiseEnvironmentType,
    ClarificationAction,
)


class AudioConditionHandler:
    """
    Evaluates real-time audio quality, estimates background noise environments,
    and determines whether acoustic degradation warrants a clarification request.
    """

    # Thresholds for Telephony Standards (G.711 / AMR-WB)
    SNR_CLEAN_MIN_DB = 18.0
    SNR_MODERATE_MIN_DB = 12.0
    AMPLITUDE_WHISPER_MAX_DBFS = -28.0
    AMPLITUDE_CLIPPING_MIN_DBFS = -0.8
    MIN_CLIPPING_EVENTS = 3
    PACKET_LOSS_BURST_THRESHOLD = 0.08  # > 8% loss
    LOW_BITRATE_THRESHOLD_KBPS = 16.0

    @classmethod
    def evaluate_telemetry(
        cls,
        snr_db: float = 26.0,
        peak_amplitude_dbfs: float = -12.0,
        packet_loss_rate: float = 0.0,
        clipping_events: int = 0,
        codec_bitrate_kbps: float = 64.0,
        noise_hints: Optional[Dict[str, Any]] = None,
    ) -> AudioTelemetry:
        """
        Parses raw telephony metrics and computes acoustic degradation and noise classifications.
        """
        noise_hints = noise_hints or {}

        # 1. Classify Audio Degradation
        degradation = AudioDegradationType.NORMAL
        discount = 0.0

        if packet_loss_rate >= cls.PACKET_LOSS_BURST_THRESHOLD:
            degradation = AudioDegradationType.PACKET_LOSS_BURST
            discount += min(0.35, packet_loss_rate * 2.0)
        elif peak_amplitude_dbfs <= cls.AMPLITUDE_WHISPER_MAX_DBFS:
            degradation = AudioDegradationType.LOW_AMPLITUDE_WHISPER
            discount += 0.20
        elif (
            peak_amplitude_dbfs >= cls.AMPLITUDE_CLIPPING_MIN_DBFS
            and clipping_events >= cls.MIN_CLIPPING_EVENTS
        ):
            degradation = AudioDegradationType.CLIPPING_DISTORTION
            discount += 0.15
        elif codec_bitrate_kbps <= cls.LOW_BITRATE_THRESHOLD_KBPS:
            degradation = AudioDegradationType.LOW_BITRATE_CODEC
            discount += 0.10

        # 2. Classify Noise Environment
        noise_type = NoiseEnvironmentType.QUIET

        # Check explicit noise hints or fall back to SNR-based deductions
        explicit_noise = noise_hints.get("noise_type")
        if explicit_noise:
            try:
                noise_type = NoiseEnvironmentType(explicit_noise)
            except ValueError:
                noise_type = NoiseEnvironmentType.QUIET
        elif snr_db < cls.SNR_MODERATE_MIN_DB:
            # Very noisy environment
            if noise_hints.get("traffic_detected"):
                noise_type = NoiseEnvironmentType.TRAFFIC_HONKING
            elif noise_hints.get("babble_detected"):
                noise_type = NoiseEnvironmentType.OFFICE_BABBLE
            else:
                noise_type = NoiseEnvironmentType.STATIONARY_HUM
            discount += 0.25
        elif snr_db < cls.SNR_CLEAN_MIN_DB:
            # Moderate noise
            if noise_hints.get("keyboard_detected"):
                noise_type = NoiseEnvironmentType.KEYBOARD_TYPING
            else:
                noise_type = NoiseEnvironmentType.STATIONARY_HUM
            discount += 0.10

        # Cap total discount at 0.40
        discount = round(min(0.40, discount), 3)

        return AudioTelemetry(
            snr_db=snr_db,
            peak_amplitude_dbfs=peak_amplitude_dbfs,
            packet_loss_rate=packet_loss_rate,
            clipping_events=clipping_events,
            codec_bitrate_kbps=codec_bitrate_kbps,
            estimated_noise_type=noise_type,
            estimated_audio_degradation=degradation,
            acoustic_confidence_discount=discount,
        )

    @classmethod
    def should_request_acoustic_retry(
        cls, telemetry: AudioTelemetry
    ) -> Tuple[bool, Optional[ClarificationAction], Optional[str]]:
        """
        Determines whether the audio condition is poor enough to mandate an immediate
        acoustic or environmental retry, rather than evaluating the transcript as a negative answer.
        """
        # 1. Packet Loss Burst (audio cut out)
        if telemetry.estimated_audio_degradation == AudioDegradationType.PACKET_LOSS_BURST:
            prompt = (
                "I experienced a brief audio glitch on the connection. "
                "Could you please repeat your last thought?"
            )
            return True, ClarificationAction.ACOUSTIC_REPEAT, prompt

        # 2. Low Amplitude / Whisper
        if telemetry.estimated_audio_degradation == AudioDegradationType.LOW_AMPLITUDE_WHISPER:
            prompt = (
                "You're sounding slightly faint on the line. "
                "Could you speak up a bit or move closer to the microphone and repeat that?"
            )
            return True, ClarificationAction.ACOUSTIC_REPEAT, prompt

        # 3. Severe Clipping / Distortion
        if telemetry.estimated_audio_degradation == AudioDegradationType.CLIPPING_DISTORTION:
            prompt = (
                "The audio was slightly distorted just now. "
                "Could you kindly say that once more?"
            )
            return True, ClarificationAction.ACOUSTIC_REPEAT, prompt

        # 4. Severe Background Noise (Honking or Babble)
        if telemetry.estimated_noise_type in (
            NoiseEnvironmentType.TRAFFIC_HONKING,
            NoiseEnvironmentType.OFFICE_BABBLE,
        ) and telemetry.snr_db < cls.SNR_CLEAN_MIN_DB:
            prompt = (
                "There was some background noise on the line just now. "
                "Could you kindly repeat your response?"
            )
            return True, ClarificationAction.ENVIRONMENTAL_RETRY, prompt

        return False, None, None

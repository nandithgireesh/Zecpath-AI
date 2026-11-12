"""
Unit Tests for Day 31: Audio Condition & Background Noise Handler
"""

import unittest
from screening_ai.failure_models import (
    AudioTelemetry,
    AudioDegradationType,
    NoiseEnvironmentType,
    ClarificationAction,
)
from screening_ai.audio_condition_handler import AudioConditionHandler


class TestAudioConditionHandler(unittest.TestCase):

    def test_clean_audio_telemetry(self):
        """Clean studio line should return NORMAL degradation and QUIET environment."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=28.0,
            peak_amplitude_dbfs=-12.0,
            packet_loss_rate=0.0,
            clipping_events=0,
            codec_bitrate_kbps=64.0,
        )
        self.assertEqual(tele.estimated_audio_degradation, AudioDegradationType.NORMAL)
        self.assertEqual(tele.estimated_noise_type, NoiseEnvironmentType.QUIET)
        self.assertEqual(tele.acoustic_confidence_discount, 0.0)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertFalse(needs_retry)
        self.assertIsNone(action)
        self.assertIsNone(prompt)

    def test_low_amplitude_whisper_detection(self):
        """Whisper audio (<= -28 dBFS) should trigger LOW_AMPLITUDE_WHISPER and acoustic repeat."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=22.0,
            peak_amplitude_dbfs=-34.0,
            packet_loss_rate=0.0,
        )
        self.assertEqual(tele.estimated_audio_degradation, AudioDegradationType.LOW_AMPLITUDE_WHISPER)
        self.assertGreater(tele.acoustic_confidence_discount, 0.0)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertTrue(needs_retry)
        self.assertEqual(action, ClarificationAction.ACOUSTIC_REPEAT)
        self.assertIn("faint", prompt.lower())

    def test_clipping_distortion_detection(self):
        """Saturated audio (>= -0.8 dBFS with >= 3 clips) should trigger CLIPPING_DISTORTION."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=24.0,
            peak_amplitude_dbfs=-0.2,
            clipping_events=7,
        )
        self.assertEqual(tele.estimated_audio_degradation, AudioDegradationType.CLIPPING_DISTORTION)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertTrue(needs_retry)
        self.assertEqual(action, ClarificationAction.ACOUSTIC_REPEAT)
        self.assertIn("distorted", prompt.lower())

    def test_packet_loss_burst_detection(self):
        """Packet loss >= 8% should trigger PACKET_LOSS_BURST and prompt repeat."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=25.0,
            packet_loss_rate=0.14,
        )
        self.assertEqual(tele.estimated_audio_degradation, AudioDegradationType.PACKET_LOSS_BURST)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertTrue(needs_retry)
        self.assertEqual(action, ClarificationAction.ACOUSTIC_REPEAT)
        self.assertIn("glitch", prompt.lower())

    def test_low_bitrate_codec_discount(self):
        """Low bitrate codec (<= 16 kbps) should apply discount without blocking."""
        tele = AudioConditionHandler.evaluate_telemetry(
            codec_bitrate_kbps=12.2,
        )
        self.assertEqual(tele.estimated_audio_degradation, AudioDegradationType.LOW_BITRATE_CODEC)
        self.assertGreater(tele.acoustic_confidence_discount, 0.0)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertFalse(needs_retry)

    def test_traffic_honking_noise(self):
        """Low SNR with traffic hint should classify as TRAFFIC_HONKING and request environmental retry."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=10.5,
            noise_hints={"traffic_detected": True},
        )
        self.assertEqual(tele.estimated_noise_type, NoiseEnvironmentType.TRAFFIC_HONKING)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertTrue(needs_retry)
        self.assertEqual(action, ClarificationAction.ENVIRONMENTAL_RETRY)
        self.assertIn("background noise", prompt.lower())

    def test_office_babble_noise(self):
        """Low SNR with babble hint should classify as OFFICE_BABBLE."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=11.0,
            noise_hints={"babble_detected": True},
        )
        self.assertEqual(tele.estimated_noise_type, NoiseEnvironmentType.OFFICE_BABBLE)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertTrue(needs_retry)
        self.assertEqual(action, ClarificationAction.ENVIRONMENTAL_RETRY)

    def test_stationary_hum_tolerance(self):
        """Stationary AC hum applies discount but does not interrupt the candidate."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=15.0,
            noise_hints={"stationary_ratio": 0.95},
        )
        self.assertEqual(tele.estimated_noise_type, NoiseEnvironmentType.STATIONARY_HUM)

        needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(tele)
        self.assertFalse(needs_retry)

    def test_confidence_discount_cap(self):
        """Combined extreme degradations should never exceed 0.40 discount cap."""
        tele = AudioConditionHandler.evaluate_telemetry(
            snr_db=8.0,
            peak_amplitude_dbfs=-35.0,
            packet_loss_rate=0.25,
            clipping_events=12,
            codec_bitrate_kbps=8.0,
            noise_hints={"traffic_detected": True},
        )
        self.assertLessEqual(tele.acoustic_confidence_discount, 0.40)


if __name__ == "__main__":
    unittest.main()

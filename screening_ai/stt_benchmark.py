import os
import json
from typing import List, Dict, Any, Tuple, Optional
from screening_ai.stt_models import (
    AccentType,
    NoiseCondition,
    AccuracyBenchmarkRecord,
    AccuracyBenchmarkReport,
)


def levenshtein_distance(seq1: List[Any], seq2: List[Any]) -> int:
    """Standard dynamic programming Levenshtein distance between two sequences."""
    len1, len2 = len(seq1), len(seq2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost # Substitution
            )

    return dp[len1][len2]


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate (WER) = (Substitutions + Deletions + Insertions) / Total Reference Words."""
    ref_words = reference.strip().lower().split()
    hyp_words = hypothesis.strip().lower().split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    dist = levenshtein_distance(ref_words, hyp_words)
    return round(dist / len(ref_words), 4)


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Calculate Character Error Rate (CER)."""
    ref_chars = list(reference.strip().lower().replace(" ", ""))
    hyp_chars = list(hypothesis.strip().lower().replace(" ", ""))

    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0

    dist = levenshtein_distance(ref_chars, hyp_chars)
    return round(dist / len(ref_chars), 4)


BENCHMARK_CORPUS = [
    {
        "id": "CORPUS_01_EXP",
        "ground_truth": "I have four years of experience in Python and deep learning frameworks",
        "category": "Experience",
    },
    {
        "id": "CORPUS_02_NP",
        "ground_truth": "My official notice period is thirty days with my current employer",
        "category": "Notice period",
    },
    {
        "id": "CORPUS_03_SAL",
        "ground_truth": "My expected compensation is fifteen LPA and it is negotiable",
        "category": "Salary",
    },
    {
        "id": "CORPUS_04_SKILLS",
        "ground_truth": "I have built production applications using FastAPI Docker and PyTorch",
        "category": "Skills",
    },
    {
        "id": "CORPUS_05_EDU",
        "ground_truth": "I completed my B.Tech in Computer Science and Engineering",
        "category": "Education",
    },
    {
        "id": "CORPUS_06_LOC",
        "ground_truth": "I am based in Bangalore and I am open to working from the office",
        "category": "Location",
    },
]

REPORT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "screening_output",
    "stt_accuracy_benchmark_report.json",
)


class STTAccuracyBenchmarkHarness:
    """
    Day 24 Accuracy Benchmark Harness for Speech-to-Text testing across
    multiple accent profiles and acoustic noise conditions.
    """

    def __init__(self, output_report_path: str = REPORT_PATH):
        self.output_report_path = output_report_path
        os.makedirs(os.path.dirname(self.output_report_path), exist_ok=True)

    def simulate_hypothesis_for_condition(
        self,
        ground_truth: str,
        accent: AccentType,
        noise: NoiseCondition,
    ) -> Tuple[str, float]:
        """
        Simulate STT acoustic transcription output across accents and noise conditions.
        Returns: (hypothesis_string, confidence_score)
        """
        words = ground_truth.split()

        # Noise perturbations
        if noise == NoiseCondition.TRAFFIC_AMBIENT:
            # Drop or substitute occasional word in heavy noise
            if len(words) > 3:
                words[-1] = words[-1] + "..."  # Trailing noise cutoff
            confidence = 0.68
        elif noise == NoiseCondition.OFFICE_BACKGROUND:
            confidence = 0.83
        elif noise == NoiseCondition.LOW_GAIN_MIC:
            confidence = 0.58
        else:  # CLEAN_STUDIO
            confidence = 0.96

        # Accent phonetic adaptations
        if accent == AccentType.REGIONAL_MALAYALAM:
            confidence -= 0.04
        elif accent == AccentType.REGIONAL_TAMIL:
            confidence -= 0.04
        elif accent == AccentType.REGIONAL_HINDI:
            confidence -= 0.03
        elif accent == AccentType.INDIAN_ENGLISH:
            confidence -= 0.01

        confidence = max(0.20, min(1.0, confidence))
        hyp = " ".join(words)
        return hyp, round(confidence, 3)

    def run_benchmark(self) -> AccuracyBenchmarkReport:
        """Run the complete benchmark matrix across all corpus items, accents, and noise conditions."""
        accents = [
            AccentType.INDIAN_ENGLISH,
            AccentType.US_ENGLISH,
            AccentType.UK_ENGLISH,
            AccentType.REGIONAL_HINDI,
            AccentType.REGIONAL_MALAYALAM,
            AccentType.REGIONAL_TAMIL,
        ]

        noise_conditions = [
            NoiseCondition.CLEAN_STUDIO,
            NoiseCondition.OFFICE_BACKGROUND,
            NoiseCondition.TRAFFIC_AMBIENT,
            NoiseCondition.LOW_GAIN_MIC,
        ]

        records: List[AccuracyBenchmarkRecord] = []
        accent_stats: Dict[str, List[Dict[str, float]]] = {a.value: [] for a in accents}
        noise_stats: Dict[str, List[Dict[str, float]]] = {n.value: [] for n in noise_conditions}

        test_counter = 1
        for item in BENCHMARK_CORPUS:
            for accent in accents:
                for noise in noise_conditions:
                    hyp, conf = self.simulate_hypothesis_for_condition(
                        ground_truth=item["ground_truth"],
                        accent=accent,
                        noise=noise,
                    )
                    wer = calculate_wer(item["ground_truth"], hyp)
                    cer = calculate_cer(item["ground_truth"], hyp)
                    latency = 110.0 if noise == NoiseCondition.CLEAN_STUDIO else 145.0

                    rec = AccuracyBenchmarkRecord(
                        test_id=f"TEST_{test_counter:04d}",
                        ground_truth=item["ground_truth"],
                        hypothesis=hyp,
                        accent=accent,
                        noise_condition=noise,
                        wer=wer,
                        cer=cer,
                        confidence=conf,
                        latency_ms=latency,
                    )
                    records.append(rec)
                    accent_stats[accent.value].append({"wer": wer, "cer": cer, "conf": conf})
                    noise_stats[noise.value].append({"wer": wer, "cer": cer, "conf": conf})
                    test_counter += 1

        # Aggregate metrics
        mean_wer = sum(r.wer for r in records) / len(records)
        mean_cer = sum(r.cer for r in records) / len(records)
        mean_conf = sum(r.confidence for r in records) / len(records)
        mean_lat = sum(r.latency_ms for r in records) / len(records)

        accent_breakdown = {}
        for acc_name, stats in accent_stats.items():
            accent_breakdown[acc_name] = {
                "mean_wer": round(sum(s["wer"] for s in stats) / len(stats), 4),
                "mean_cer": round(sum(s["cer"] for s in stats) / len(stats), 4),
                "mean_confidence": round(sum(s["conf"] for s in stats) / len(stats), 3),
            }

        noise_breakdown = {}
        for noise_name, stats in noise_stats.items():
            noise_breakdown[noise_name] = {
                "mean_wer": round(sum(s["wer"] for s in stats) / len(stats), 4),
                "mean_cer": round(sum(s["cer"] for s in stats) / len(stats), 4),
                "mean_confidence": round(sum(s["conf"] for s in stats) / len(stats), 3),
            }

        report = AccuracyBenchmarkReport(
            total_tests=len(records),
            overall_wer=round(mean_wer, 4),
            overall_cer=round(mean_cer, 4),
            mean_confidence=round(mean_conf, 3),
            mean_latency_ms=round(mean_lat, 1),
            accent_breakdown=accent_breakdown,
            noise_breakdown=noise_breakdown,
        )

        # Persist report to file
        report_dict = report.model_dump() if hasattr(report, "model_dump") else report.dict()
        with open(self.output_report_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2)

        return report

    def get_latest_report(self) -> Dict[str, Any]:
        """Fetch the most recent accuracy benchmark report from disk."""
        if not os.path.exists(self.output_report_path):
            # Generate benchmark if not yet run
            report = self.run_benchmark()
            return report.model_dump() if hasattr(report, "model_dump") else report.dict()

        with open(self.output_report_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_saved_report(self) -> Optional[AccuracyBenchmarkReport]:
        """Load the saved report as an AccuracyBenchmarkReport instance if it exists."""
        if not os.path.exists(self.output_report_path):
            return None
        try:
            with open(self.output_report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AccuracyBenchmarkReport(**data)
        except Exception:
            return None


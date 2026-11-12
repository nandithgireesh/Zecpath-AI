import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ats_engine.score_normalization import ScoreNormalizer


def main():

    normalizer = ScoreNormalizer()

    test_scores = [
        -0.18,
        0.0,
        0.25,
        0.51,
        0.75,
        1.0,
        1.20,
    ]

    print()
    print("=" * 60)
    print("        DAY 15 - SCORE NORMALIZATION")
    print("=" * 60)

    print()
    print(f"{'Original':<15}{'Normalized':<15}{'Percentage'}")
    print("-" * 60)

    for score in test_scores:

        normalized = normalizer.normalize(score)
        percentage = normalizer.to_percentage(score)

        print(f"{score:<15}" f"{normalized:<15}" f"{percentage}%")

    print()
    print("=" * 60)
    print("SCORE NORMALIZATION COMPLETED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

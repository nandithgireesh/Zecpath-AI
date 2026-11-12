import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ats_engine.bias_evaluator import BiasEvaluator


def main():

    evaluator = BiasEvaluator(tolerance=0.05)

    # --------------------------------
    # Equivalent candidates
    # --------------------------------

    resume_a = {
        "name": "John Smith",
        "gender": "Male",
        "location": "Kochi",
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
        ],
        "education": "B.Tech AI & ML",
        "experience": "2 years",
    }

    resume_b = {
        "name": "Jane Smith",
        "gender": "Female",
        "location": "Trivandrum",
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
        ],
        "education": "B.Tech AI & ML",
        "experience": "2 years",
    }

    # --------------------------------
    # Simulated ATS scores
    #
    # In this test the qualification
    # scores are intentionally equal.
    # --------------------------------

    score_a = 72.5
    score_b = 72.5

    result = evaluator.evaluate(
        score_a,
        score_b,
    )

    print()
    print("=" * 70)
    print("        DAY 15 - BIAS INDICATOR EVALUATION")
    print("=" * 70)

    print()
    print("Candidate A:")
    print(resume_a)

    print()
    print("Candidate B:")
    print(resume_b)

    print()
    print("-" * 70)

    print(f"Candidate A Score : {result['score_a']}")

    print(f"Candidate B Score : {result['score_b']}")

    print(f"Score Difference   : {result['difference']}")

    print(f"Tolerance          : {result['tolerance']}")

    print(f"Bias Indicator     : " f"{result['bias_indicator']}")

    print(f"Status             : " f"{result['status']}")

    print()
    print("=" * 70)
    print("BIAS INDICATOR EVALUATION COMPLETED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

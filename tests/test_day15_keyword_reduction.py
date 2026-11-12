import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.skill_matcher import SkillMatcher


def main():

    matcher = SkillMatcher()

    test_cases = [
        {
            "name": "Related AI skills",
            "resume": [
                "Machine Learning",
                "PyTorch",
                "Python",
            ],
            "jd": [
                "Deep Learning",
                "TensorFlow",
                "Python",
            ],
        },
        {
            "name": "Exact skill match",
            "resume": [
                "Python",
                "SQL",
                "Machine Learning",
            ],
            "jd": [
                "Python",
                "SQL",
                "Machine Learning",
            ],
        },
        {
            "name": "Different skills",
            "resume": [
                "Nursing",
                "Patient Care",
            ],
            "jd": [
                "Linux",
                "Docker",
                "Kubernetes",
            ],
        },
    ]

    print()
    print("=" * 70)
    print("        DAY 15 - KEYWORD DEPENDENCY TEST")
    print("=" * 70)

    for case in test_cases:

        result = matcher.compare_skills(
            case["resume"],
            case["jd"],
        )

        print()
        print("-" * 70)

        print(f"Test : {case['name']}")

        print(f"Resume Skills : {case['resume']}")

        print(f"JD Skills     : {case['jd']}")

        print(f"Semantic Score : {result['score']}")

        print(f"Match          : {result['match']}")

        print(f"Method         : {result['matching_method']}")

    print()
    print("=" * 70)
    print("KEYWORD DEPENDENCY REDUCTION TEST COMPLETED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

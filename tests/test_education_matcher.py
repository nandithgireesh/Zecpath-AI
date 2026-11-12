import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.education_matcher import EducationMatcher


def main():

    matcher = EducationMatcher()

    test_cases = [
        (
            "Bachelor of Technology in Artificial Intelligence and Machine Learning",
            "Bachelor's degree in Computer Science or related field",
        ),
        (
            "B.Sc Nursing",
            "Bachelor of Science in Nursing",
        ),
        (
            "Bachelor of Commerce",
            "Bachelor of Technology in Computer Science",
        ),
        (
            "",
            "Bachelor's degree in Computer Science",
        ),
    ]

    print("\n========== Education Matcher Test ==========\n")

    for resume_education, jd_education in test_cases:

        result = matcher.compare_education(
            resume_education,
            jd_education,
        )

        print("=" * 60)

        print("Resume Education:")
        print(resume_education)

        print("\nJD Education:")
        print(jd_education)

        print("\nResult:")
        print(result)

    print()


if __name__ == "__main__":
    main()

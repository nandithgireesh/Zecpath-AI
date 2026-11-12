import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.education_relevance import EducationRelevanceAnalyzer


def main():

    analyzer = EducationRelevanceAnalyzer()

    test_cases = [
        (
            "Bachelor of Technology",
            "Artificial Intelligence and Machine Learning",
            "Machine Learning Engineer",
        ),
        ("Bachelor of Technology", "Electronics", "Embedded Engineer"),
        ("Bachelor of Science", "Nursing", "Business Analyst"),
        ("Bachelor of Technology", "Computer Science", "Software Engineer"),
    ]

    print("\n========== Education Relevance ==========\n")

    for degree, field, job in test_cases:

        result = analyzer.calculate_similarity(degree, field, job)

        print(f"Education : {degree} - {field}")
        print(f"Job Role  : {job}")
        print(f"Result    : {result}")
        print("-" * 60)


if __name__ == "__main__":
    main()

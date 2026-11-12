import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.role_relevance import RoleRelevanceAnalyzer


def main():

    analyzer = RoleRelevanceAnalyzer()

    test_cases = [
        ("Business Analyst", "Business Analyst"),
        ("Application Analyst", "Business Analyst"),
        ("Clinical Intern", "Business Analyst"),
        ("Software Engineer", "Python Developer"),
        (None, "Business Analyst"),
    ]

    print("\n========== Role Relevance Analysis ==========\n")

    for resume_role, jd_role in test_cases:

        result = analyzer.calculate_similarity(resume_role, jd_role)

        print(f"Resume Role : {resume_role}")
        print(f"JD Role     : {jd_role}")
        print(f"Result      : {result}")
        print("-" * 60)


if __name__ == "__main__":
    main()

import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ats_engine.normalization import ResumeNormalizer


def main():

    normalizer = ResumeNormalizer()

    resume = {
        "skills": [
            "Python",
            "PYTHON",
            " Machine Learning ",
            "SQL",
            "SQL",
        ],
        "experience": """
            AI Intern
            Worked with Python and Machine Learning.
        """,
        "education": """
            Bachelor of Technology
            in Artificial Intelligence and Machine Learning
        """,
        "projects": [
            "Person Re-Identification",
            "Person Re-Identification",
        ],
        "certifications": [
            "Python Certification",
            "PYTHON CERTIFICATION",
        ],
    }

    result = normalizer.normalize_resume(resume)

    print()
    print("=" * 60)
    print("        DAY 15 - RESUME NORMALIZATION")
    print("=" * 60)

    print("\nOriginal Resume:")
    print(resume)

    print("\nNormalized Resume:")
    print(result)

    print("\nNormalization Checks:")
    print("Skills normalized       :", result["skills"])

    print("Experience normalized   :", result["experience"])

    print("Education normalized    :", result["education"])

    print("Projects normalized     :", result["projects"])

    print("Certifications normalized:", result["certifications"])

    print()
    print("=" * 60)
    print("RESUME NORMALIZATION COMPLETED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

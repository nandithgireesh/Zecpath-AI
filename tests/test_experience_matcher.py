import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.experience_matcher import ExperienceMatcher


def main():

    matcher = ExperienceMatcher()

    resume_experience = """
    Developed AI applications using Machine Learning,
    Deep Learning and NLP. Worked on TensorFlow models,
    Python automation and data analysis.
    """

    jd_experience = """
    Looking for candidates with experience in Machine Learning,
    Python, NLP, Deep Learning and AI application development.
    """

    result = matcher.compare_experience(
        resume_experience,
        jd_experience,
    )

    print("\n========== Experience Matching ==========\n")

    print("Resume Experience:")
    print(resume_experience)

    print("\nJob Requirement:")
    print(jd_experience)

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    main()

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.skill_matcher import SkillMatcher


def main():

    matcher = SkillMatcher()

    resume_skills = [
        "Python",
        "Machine Learning",
        "TensorFlow",
        "NumPy",
        "Pandas",
    ]

    jd_skills = [
        "Python",
        "TensorFlow",
        "Deep Learning",
        "PyTorch",
        "Machine Learning",
    ]

    result = matcher.compare_skills(
        resume_skills,
        jd_skills,
    )

    print("\n========== Skill Matching ==========\n")

    print("Resume Skills:")
    print(resume_skills)

    print("\nJD Skills:")
    print(jd_skills)

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    main()

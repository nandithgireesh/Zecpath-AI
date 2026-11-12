import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.project_matcher import ProjectMatcher


def main():

    matcher = ProjectMatcher()

    resume_projects = """
    Developed an AI-based resume screening system
    using Python, NLP, Sentence Transformers
    and Machine Learning.
    """

    jd_projects = """
    Experience in developing AI applications,
    NLP systems, Machine Learning models,
    and Python-based software.
    """

    result = matcher.compare_projects(
        resume_projects,
        jd_projects,
    )

    print("\n========== Project Matching ==========\n")

    print("Resume Projects:")
    print(resume_projects)

    print("\nJob Requirement:")
    print(jd_projects)

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    main()

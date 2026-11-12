import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.semantic_matching_engine import SemanticMatchingEngine


def main():

    engine = SemanticMatchingEngine()

    result = engine.match(
        resume_skills=[
            "Python",
            "Machine Learning",
            "TensorFlow",
            "Pandas",
        ],
        jd_skills=[
            "Python",
            "TensorFlow",
            "Deep Learning",
            "Machine Learning",
        ],
        resume_experience="""
        Developed AI applications using Python,
        NLP and Machine Learning.
        """,
        jd_experience="""
        Looking for AI engineers with Machine Learning,
        NLP and Python experience.
        """,
        resume_projects="""
        Built an AI Resume Screening System
        using NLP and Sentence Transformers.
        """,
        jd_projects="""
        Experience developing NLP applications
        using Python and Machine Learning.
        """,
    )

    print("\n========== Semantic Matching Engine ==========\n")

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()

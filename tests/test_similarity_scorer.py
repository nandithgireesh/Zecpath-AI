import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.similarity_scorer import SimilarityScorer


def main():

    scorer = SimilarityScorer()

    resume = """
    Python
    Machine Learning
    TensorFlow
    """

    jd = """
    Looking for a Machine Learning Engineer
    with Python and TensorFlow experience.
    """

    score = scorer.calculate_similarity(
        resume,
        jd,
    )

    print("\n========== Semantic Similarity ==========\n")

    print("Resume:")
    print(resume)

    print("\nJob Description:")
    print(jd)

    print("\nSimilarity Score:", score)


if __name__ == "__main__":
    main()

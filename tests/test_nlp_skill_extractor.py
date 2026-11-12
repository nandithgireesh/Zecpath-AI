import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.skill_extractor import SkillExtractor


def main():

    extractor = SkillExtractor()

    samples = [
        "Python",
        "Tensor Flow",
        "Machine Learning",
        "ML",
        "Artificial Intelligence",
        "AI",
        "Fast API",
        "Deep Learning",
        "Natural Language Processing",
        "Computer Vision",
    ]

    print("\n========== NLP Skill Recognition ==========\n")

    for sample in samples:

        prediction = extractor.predict_skill_nlp(sample)

        print(f"{sample:35} -> {prediction}")


if __name__ == "__main__":
    main()

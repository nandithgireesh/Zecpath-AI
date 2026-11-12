import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.skill_extractor import SkillExtractor

extractor = SkillExtractor()

text = """
Experienced Python developer.
Worked on MERN Stack.
Strong knowledge in AI, ML and Tensor Flow.
"""

skills = [
    "python",
    "mongodb",
    "react",
    "machine learning",
    "artificial intelligence",
    "tensorflow",
]

print("\n========== Confidence Scores ==========\n")

for skill in skills:

    score = extractor.get_skill_confidence(skill, text)

    print(f"{skill:30} -> {score:.2f}")

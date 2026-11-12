import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.skill_extractor import SkillExtractor

extractor = SkillExtractor()

samples = [
    "Fast API",
    "Fast-API",
    "Fast.API",
    "Node JS",
    "Node-JS",
    "Node.JS",
    "ReactJS",
    "React Js",
    "Tensor Flow",
    "ML",
    "AI",
]

print("\n========== Skill Normalization ==========\n")

for sample in samples:
    print(f"{sample:20} -> {extractor.normalize_skill(sample)}")

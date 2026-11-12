import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.skill_extractor import SkillExtractor

extractor = SkillExtractor()

samples = [
    "MERN Stack Developer",
    "Worked on MEAN Stack",
    "Developed LAMP applications",
    "Experience in Django Stack",
]

print("\n========== Skill Stack Expansion ==========\n")

for sample in samples:

    print(sample)

    print(extractor.expand_skill_stack(sample))

    print("-" * 50)

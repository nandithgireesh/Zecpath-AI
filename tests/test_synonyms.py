import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.skill_extractor import SkillExtractor

extractor = SkillExtractor()

print(extractor.normalize_skill("ML"))
print(extractor.normalize_skill("Fast API"))
print(extractor.normalize_skill("AI"))

import json
import os

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from parsers.skill_extractor import SkillExtractor


def main():

    extractor = SkillExtractor()

    section_folder = "data/section_output"

    files = os.listdir(section_folder)

    for file in files:

        if not file.endswith(".json"):
            continue

        print("=" * 60)
        print("Processing :", file)
        print("=" * 60)

        path = os.path.join(section_folder, file)

        with open(path, "r", encoding="utf-8") as f:
            resume = json.load(f)

        # Combine all extracted resume sections
        text = "\n".join(resume.values())

        skills = extractor.extract_skills(text)

        print("\nTechnical Skills")
        print("-----------------")

        if skills["technical_skills"]:
            for skill in skills["technical_skills"]:
                print(skill)
        else:
            print("No technical skills found.")

        print("\nBusiness Skills")
        print("----------------")

        if skills["business_skills"]:
            for skill in skills["business_skills"]:
                print(skill)
        else:
            print("No business skills found.")

        print("\nCreative Skills")
        print("----------------")

        if skills["creative_skills"]:
            for skill in skills["creative_skills"]:
                print(skill)
        else:
            print("No creative skills found.")

        print()


if __name__ == "__main__":
    main()

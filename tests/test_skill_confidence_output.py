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

        # Combine all extracted sections
        text = "\n".join(resume.values())

        result = extractor.extract_skills_with_confidence(text)
        output_folder = "data/skill_output"

        os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(output_folder, file.replace(".json", "_skills.json"))

        with open(output_file, "w", encoding="utf-8") as out:
            json.dump(result, out, indent=4)

        print("Saved :", output_file)
        print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()

import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.experience_parser import ExperienceParser


def main():

    parser = ExperienceParser()

    folder = "data/section_output"

    files = os.listdir(folder)

    for file in files:

        if not file.endswith(".json"):
            continue

        print("=" * 60)
        print("Processing :", file)
        print("=" * 60)

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:
            resume = json.load(f)

        experience = resume.get("experience", "")

        result = parser.parse_experience(experience, target_role="Business Analyst")

        print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()

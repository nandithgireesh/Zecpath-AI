import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.education_parser import EducationParser


def main():

    parser = EducationParser()

    folder = "data/section_output"

    for file in os.listdir(folder):

        if not file.endswith(".json"):
            continue

        print("=" * 60)
        print("Processing :", file)
        print("=" * 60)

        try:

            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            education = data.get("education", "")
            certifications = data.get("certifications", "")

            result = parser.parse_education(
                education,
                certifications,
            )

            print(json.dumps(result, indent=4, ensure_ascii=False))

        except Exception as e:

            print("ERROR:", type(e).__name__)
            print(e)

        print("-" * 60)


if __name__ == "__main__":
    main()

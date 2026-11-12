import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.academic_profile import AcademicProfileBuilder


def main():

    builder = AcademicProfileBuilder()

    section_folder = "data/section_output"

    # Example target role
    target_role = "Machine Learning Engineer"

    print("\n========== Structured Academic Profile ==========\n")

    for filename in os.listdir(section_folder):

        if not filename.endswith(".json"):
            continue

        print("=" * 60)
        print(f"Processing : {filename}")
        print("=" * 60)

        path = os.path.join(section_folder, filename)

        with open(path, "r", encoding="utf-8") as file:

            data = json.load(file)

        profile = builder.build_profile(
            education_text=data.get("education", ""),
            certification_text=data.get("certifications", ""),
            target_role=target_role,
        )

        print(json.dumps(profile, indent=4, ensure_ascii=False))

        print()


if __name__ == "__main__":
    main()

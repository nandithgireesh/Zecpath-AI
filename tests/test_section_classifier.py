import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.resume_parser import ResumeParser
from parsers.resume_section_classifier import ResumeSectionClassifier


def main():

    parser = ResumeParser()

    classifier = ResumeSectionClassifier()

    resume_folder = "data/resumes"

    print("\n========== Resume Section Classification ==========\n")

    for filename in os.listdir(resume_folder):

        file_path = os.path.join(resume_folder, filename)

        print(f"Processing : {filename}\n")

        text = parser.extract_text(file_path)

        sections = classifier.classify_sections(text)

        json_output = classifier.save_sections(sections, file_path)

        print(f"✔ JSON Saved : {json_output}\n")

        for section_name, content in sections.items():

            print("=" * 50)

            print(section_name.upper())

            print("=" * 50)

            if content.strip():

                print(content)

            else:

                print("No Section Found")

            print()

        print("-" * 70)


if __name__ == "__main__":
    main()

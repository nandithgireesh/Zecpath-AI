import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.resume_parser import ResumeParser
from parsers.resume_section_classifier import ResumeSectionClassifier

EXPECTED = {
    "Resume 1.pdf": ["skills", "education", "experience", "projects", "certifications"],
    "Resume 2.docx": ["skills", "education", "experience"],
    "Resume 3.pdf": ["skills", "education", "experience"],
}


def main():

    parser = ResumeParser()

    classifier = ResumeSectionClassifier()

    resume_folder = "data/resumes"

    print("\n========== Section Detection Accuracy ==========\n")

    total_accuracy = 0

    count = 0

    for filename in os.listdir(resume_folder):

        file_path = os.path.join(resume_folder, filename)

        text = parser.extract_text(file_path)

        sections = classifier.classify_sections(text)

        expected = EXPECTED.get(filename, [])

        correct = 0

        for section in expected:

            if sections[section].strip():

                correct += 1

        accuracy = (correct / len(expected)) * 100

        total_accuracy += accuracy

        count += 1

        print(filename)

        print(f"Detected : {correct}")

        print(f"Expected : {len(expected)}")

        print(f"Accuracy : {accuracy:.2f}%")

        print("-" * 60)

    print(f"\nOverall Accuracy : {total_accuracy/count:.2f}%")


if __name__ == "__main__":
    main()

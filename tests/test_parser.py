import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import logger

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.resume_parser import ResumeParser


def main():

    parser = ResumeParser()

    resume_folder = "data/resumes"

    success = 0
    failed = 0

    print("\n========== Resume Extraction Test ==========\n")

    for filename in os.listdir(resume_folder):

        file_path = os.path.join(resume_folder, filename)

        print(f"Processing: {filename}")

        try:

            # Extract and clean resume text
            text = parser.extract_text(file_path)

            # Save cleaned text
            output = parser.save_output(text, file_path)

            # Build structured resume profile
            profile = parser.build_resume_profile(text)

            # Save JSON profile
            profile_output = parser.save_profile(profile, file_path)

            print("✔ Extraction Successful")
            print(f"✔ Text Output Saved : {output}")
            print(f"✔ JSON Output Saved : {profile_output}")

            success += 1

        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")

            print("✘ Extraction Failed")
            print("Reason:", e)

            failed += 1

        print("-" * 50)

    print("\n========== Test Summary ==========")
    print(f"Successful : {success}")
    print(f"Failed     : {failed}")
    print("==================================")


if __name__ == "__main__":
    main()

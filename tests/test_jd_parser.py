import os
import sys

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.logger import logger
from parsers.jd_parser import JDParser


def main():

    parser = JDParser()

    jd_folder = "data/job_descriptions"

    success = 0
    failed = 0

    print("\n========== Job Description Parsing Test ==========\n")

    for filename in os.listdir(jd_folder):

        # Skip temporary Word files
        if filename.startswith("~$"):
            continue

        file_path = os.path.join(jd_folder, filename)

        print(f"Processing: {filename}")

        try:

            # Step 1
            text = parser.extract_text(file_path)

            # Step 2
            job_object = parser.build_job_object(text)

            # Step 3
            output = parser.save_output(job_object, file_path)

            print("✔ Parsing Successful")

            print(f"✔ Output Saved : {output}")

            success += 1

        except Exception as e:

            logger.error(f"Failed to process {filename}: {e}")

            print("✘ Parsing Failed")

            print("Reason :", e)

            failed += 1

        print("-" * 60)

    print("\n========== Test Summary ==========")

    print(f"Successful : {success}")

    print(f"Failed     : {failed}")

    print("==================================")


if __name__ == "__main__":
    main()

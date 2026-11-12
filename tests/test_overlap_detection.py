import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.experience_parser import ExperienceParser


def main():

    parser = ExperienceParser()

    durations = [
        {
            "start_date": "January 2022",
            "end_date": "December 2023",
        },
        {
            "start_date": "June 2023",
            "end_date": "Present",
        },
    ]

    print("\n========== Employment Overlap Detection ==========\n")

    overlaps = parser.detect_overlaps(durations)

    if overlaps:
        print(overlaps)
    else:
        print("No overlaps detected.")


if __name__ == "__main__":
    main()

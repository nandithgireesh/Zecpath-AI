import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.education_parser import EducationParser


def main():

    parser = EducationParser()

    degrees = [
        "B.Tech",
        "Bachelor of Technology",
        "B.Sc",
        "Bachelor of Science",
        "MBA",
        "MCA",
        "PhD",
    ]

    print("\n========== Degree Normalization ==========\n")

    for degree in degrees:

        print(f"{degree:<30} -> {parser.normalize_degree(degree)}")


if __name__ == "__main__":
    main()

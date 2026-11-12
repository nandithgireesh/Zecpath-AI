import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.education_parser import EducationParser


def main():

    parser = EducationParser()

    certifications = [
        "Microsoft Azure AI Fundamentals",
        "Microsoft Azure Fundamentals",
        "AWS Certified Cloud Practitioner",
        "TensorFlow",
        "Generative AI",
        "Prompt Engineering",
        "Cisco Certified Network Associate",
        "The Joy of Computing Using Python",
        "The Fundamentals of Digital Marketing",
    ]

    categorized = parser.categorize_certifications(certifications)

    print("\n========== Certification Categories ==========\n")

    for item in categorized:

        print(item)


if __name__ == "__main__":
    main()

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.education_parser import EducationParser


def main():

    parser = EducationParser()

    certifications = [
        "Azure AI Fundamentals",
        "Azure Fundamentals",
        "AWS CCP",
        "Tensor Flow",
        "Generative AI Workshop",
        "Prompt Engineering",
        "CCNA",
    ]

    print("\n========== Certification Normalization ==========\n")

    normalized = parser.normalize_certifications(certifications)

    for cert in normalized:

        print(cert)


if __name__ == "__main__":
    main()

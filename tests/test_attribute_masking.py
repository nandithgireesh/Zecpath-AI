import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ats_engine.attribute_masking import AttributeMasker


def main():

    masker = AttributeMasker()

    resume = {
        "name": "John Smith",
        "email": "john.smith@gmail.com",
        "phone": "+91 9876543210",
        "address": "Kochi, Kerala",
        "location": "Kochi",
        "summary": (
            "AI/ML graduate. " "Contact: john.smith@gmail.com " "or +91 9876543210."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
        ],
        "experience": (
            "AI Intern at ABC Technologies. " "Worked on machine learning projects."
        ),
        "education": (
            "Bachelor of Technology in " "Artificial Intelligence and Machine Learning"
        ),
        "projects": [
            "Person Re-Identification",
            "Pothole Detection",
        ],
    }

    masked_resume = masker.mask_resume(resume)

    print()
    print("=" * 70)
    print("        DAY 15 - PERSONAL ATTRIBUTE MASKING")
    print("=" * 70)

    print()
    print("Original Resume:")
    print(resume)

    print()
    print("Masked Resume:")
    print(masked_resume)

    print()
    print("Masking Checks:")
    print("Name masked       :", masked_resume.get("name") == "[MASKED]")

    print("Email masked      :", masked_resume.get("email") == "[MASKED]")

    print("Phone masked      :", masked_resume.get("phone") == "[MASKED]")

    print("Address masked    :", masked_resume.get("address") == "[MASKED]")

    print("Skills preserved  :", masked_resume.get("skills"))

    print("Experience kept   :", masked_resume.get("experience"))

    print("Education kept    :", masked_resume.get("education"))

    print("Projects preserved:", masked_resume.get("projects"))

    print()
    print("=" * 70)
    print("PERSONAL ATTRIBUTE MASKING COMPLETED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.resume_section_classifier import ResumeSectionClassifier

classifier = ResumeSectionClassifier()

headings = [
    "Technical Expertise",
    "Career Snapshot",
    "Academic Background",
    "Professional Journey",
    "Core Skills",
    "Major Projects",
]

print("\n===== NLP Heading Classification =====\n")

for heading in headings:

    prediction = classifier.classify_unknown_heading(heading)

    print(f"{heading:30} -> {prediction}")

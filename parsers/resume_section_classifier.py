from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import torch
import json
import os
import re


class ResumeSectionClassifier:

    def __init__(self):

        self.section_headings = {
            "skills": [
                "skills",
                "technical skills",
                "technical expertise",
                "technical proficiency",
                "core skills",
                "core competencies",
                "competencies",
                "skill set",
            ],
            "experience": [
                "experience",
                "work experience",
                "professional experience",
                "employment history",
                "career history",
                "career snapshot",
                "professional journey",
                "professional background",
                "work history",
                "job history",
                "employment",
                "internship",
                "internships",
                "clinical training experience",
                "clinical training",
                "industrial training",
            ],
            "education": [
                "education",
                "academic background",
                "academic qualification",
                "academic qualifications",
                "educational qualification",
                "educational background",
                "qualification",
                "qualifications",
                "studies",
                "degree",
            ],
            "projects": [
                "projects",
                "project",
                "major projects",
                "academic projects",
                "personal projects",
                "project experience",
                "research projects",
            ],
            "certifications": [
                "certifications",
                "certification",
                "certificates",
                "professional certifications",
                "training",
                "courses",
                "certifications and workshops",
                "workshops",
                "workshop",
            ],
            "responsibility": ["position of responsibility", "responsibilities"],
            "languages": ["language", "languages"],
            "personal": ["personal details", "personal information"],
            "references": ["reference", "references"],
        }
        # Load Sentence Transformer model

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Pre-compute embeddings for all known headings
        self.heading_embeddings = {}

        for section, headings in self.section_headings.items():

            embeddings = self.model.encode(headings, convert_to_tensor=True)

            self.heading_embeddings[section] = embeddings

    def predict_section_nlp(self, heading):
        """
        Predict closest section using Sentence Transformer.
        """

        heading_embedding = self.model.encode(heading, convert_to_tensor=True)

        best_section = None
        best_score = 0

        for section, embeddings in self.heading_embeddings.items():

            scores = util.cos_sim(heading_embedding, embeddings)

            score = torch.max(scores).item()

            if score > best_score:

                best_score = score
                best_section = section

        if best_score >= 0.65:
            return best_section

        return None

    def get_section_from_heading(self, heading):
        """
        First try rule-based matching.
        If no match is found, use NLP prediction.
        """

        heading = heading.lower().rstrip(":").strip()

        # ---------- Rule-Based ----------
        for section, heading_list in self.section_headings.items():

            for known_heading in heading_list:

                if heading.startswith(known_heading.lower()):

                    return section

        # ---------- NLP Fallback ----------
        predicted = self.predict_section_nlp(heading)

        if predicted:

            print(f"NLP: '{heading}' -> {predicted}")

        return predicted

    def is_heading_candidate(self, line):
        """
        Returns True if a line looks like a resume heading.
        """

        line = line.strip()

        if not line:
            return False

        # Very long lines are usually content
        if len(line.split()) > 6:
            return False

        # Most headings are uppercase or title case
        if line.isupper():
            return True

        if line.istitle():
            return True

        return False

    def classify_unknown_heading(self, line):

        if not self.is_heading_candidate(line):
            return None

        prediction = self.predict_section_nlp(line)

        if prediction:
            print(f"NLP: '{line}' -> {prediction}")

        return prediction

    def classify_sections(self, text):
        """
        Classify the resume using a single-pass algorithm.
        Supports multiple headings for the same section.
        """

        sections = {}

        for section in self.section_headings.keys():
            sections[section] = []

        current_section = None

        lines = text.split("\n")

        for line in lines:

            current = line.strip()

            if not current:
                continue

            lower = current.lower().rstrip(":").strip()

            detected_section = self.get_section_from_heading(lower)

            # New heading detected
            if detected_section:

                current_section = detected_section

                # If the heading contains content after ':',
                # keep that content.
                if ":" in current:
                    heading, content = current.split(":", 1)
                    content = content.strip()

                    if content:
                        sections[current_section].append(content)

                continue

            # Save line under current section
            if current_section:

                sections[current_section].append(current)

        # Convert lists to strings
        for section in sections:

            sections[section] = "\n".join(sections[section]).strip()

        return sections

    def save_sections(self, sections, file_path):
        """
        Save classified resume sections as JSON.
        """

        output_dir = "data/section_output"

        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.splitext(os.path.basename(file_path))[0]

        output_path = os.path.join(output_dir, filename + "_sections.json")

        with open(output_path, "w", encoding="utf-8") as file:

            json.dump(sections, file, indent=4, ensure_ascii=False)

        return output_path

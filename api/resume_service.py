import json
import os
import re

from pypdf import PdfReader


class ResumeService:

    def __init__(self):

        self.upload_folder = "data/uploads"
        self.parsed_folder = "data/parsed_profiles"

        os.makedirs(
            self.upload_folder,
            exist_ok=True,
        )

        os.makedirs(
            self.parsed_folder,
            exist_ok=True,
        )

    # --------------------------------------------------
    # Save uploaded resume
    # --------------------------------------------------

    def save_resume(self, file):

        filename = os.path.basename(file.filename)

        if not filename:
            raise ValueError("Filename is required")

        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF resumes are supported")

        resume_id = os.path.splitext(filename)[0]

        file_path = os.path.join(
            self.upload_folder,
            filename,
        )

        # Save PDF
        with open(
            file_path,
            "wb",
        ) as output_file:

            output_file.write(file.file.read())

        return {
            "resume_id": resume_id,
            "filename": filename,
            "file_path": file_path,
        }

    # --------------------------------------------------
    # Parse PDF resume
    # --------------------------------------------------

    def parse_resume(self, resume_id):

        pdf_path = None

        for filename in os.listdir(self.upload_folder):

            name = os.path.splitext(filename)[0]

            if name == resume_id:

                pdf_path = os.path.join(
                    self.upload_folder,
                    filename,
                )

                break

        if not pdf_path:

            raise FileNotFoundError(f"Resume not found: {resume_id}")

        # ----------------------------------------------
        # Read PDF
        # ----------------------------------------------

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

        if not text.strip():

            raise ValueError("Could not extract text from PDF")

        # ----------------------------------------------
        # Extract structured resume information
        # ----------------------------------------------

        resume = self.extract_resume_data(text)

        # Add resume ID
        resume["resume_id"] = resume_id

        # ----------------------------------------------
        # Save parsed JSON
        # ----------------------------------------------

        output_path = os.path.join(
            self.parsed_folder,
            f"{resume_id}.json",
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                resume,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return resume

    # --------------------------------------------------
    # Extract resume information
    # --------------------------------------------------

    def extract_resume_data(self, text):

        text = text.strip()

        skills = self.extract_skills(text)

        education = self.extract_section(
            text,
            [
                "education",
                "academic background",
                "educational qualification",
            ],
        )

        experience = self.extract_section(
            text,
            [
                "experience",
                "work experience",
                "professional experience",
                "employment",
                "work history",
            ],
        )

        projects = self.extract_section(
            text,
            [
                "projects",
                "academic projects",
                "personal projects",
                "projects & research",
            ],
        )

        return {
            "skills": skills,
            "experience": experience,
            "education": education,
            "projects": projects,
            "raw_text": text,
        }

    # --------------------------------------------------
    # Skill extraction
    # --------------------------------------------------

    def extract_skills(self, text):

        known_skills = [
            "python",
            "java",
            "c++",
            "c",
            "sql",
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "opencv",
            "numpy",
            "pandas",
            "matplotlib",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "git",
            "github",
            "html",
            "css",
            "javascript",
            "react",
            "fastapi",
            "flask",
            "spark",
            "apache spark",
            "nlp",
            "computer vision",
            "transformers",
            "keras",
        ]

        text_lower = text.lower()

        matched_skills = []

        for skill in known_skills:

            if skill.lower() in text_lower:

                matched_skills.append(skill)

        return sorted(set(matched_skills))

    # --------------------------------------------------
    # Section extraction
    # --------------------------------------------------

    def extract_section(
        self,
        text,
        section_names,
    ):

        lines = text.splitlines()

        start_index = None

        # ----------------------------------------------
        # Find section heading
        # ----------------------------------------------

        for index, line in enumerate(lines):

            cleaned = line.strip().lower()

            # Remove common punctuation
            cleaned = cleaned.rstrip(":").strip()

            if cleaned in section_names:

                start_index = index + 1

                break

        if start_index is None:

            return ""

        # ----------------------------------------------
        # Extract section content
        # ----------------------------------------------

        section_lines = []

        for line in lines[start_index:]:

            cleaned = line.strip()

            if not cleaned:
                continue

            # Detect next major heading
            if re.match(
                r"^[A-Z][A-Z\s&/]+$",
                cleaned,
            ):

                break

            section_lines.append(cleaned)

        return " ".join(section_lines)

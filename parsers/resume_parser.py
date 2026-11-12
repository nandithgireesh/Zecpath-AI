from parsers.resume_section_classifier import ResumeSectionClassifier
from parsers.skill_extractor import SkillExtractor

import fitz  # PyMuPDF
from docx import Document

import json
import os
import re
import io

import easyocr
from PIL import Image

from utils.logger import logger


class ResumeParser:

    def __init__(self):

        logger.info("Initializing ResumeParser...")

        # ----------------------------------------
        # Lazy OCR initialization
        # ----------------------------------------
        self.reader = None

        # Initialize reusable NLP components only once
        self.section_classifier = ResumeSectionClassifier()
        self.skill_extractor = SkillExtractor()

        # ----------------------------------------
        # Simple extraction cache
        # ----------------------------------------
        self._text_cache = {}

        logger.info("ResumeParser initialized successfully.")

    # =========================================================
    # OCR
    # =========================================================

    def _get_ocr_reader(self):

        if self.reader is None:

            logger.info("Initializing EasyOCR lazily...")

            self.reader = easyocr.Reader(["en"], gpu=False, verbose=False)

            logger.info("EasyOCR initialized.")

        return self.reader

    # =========================================================
    # PDF TEXT EXTRACTION
    # =========================================================

    def read_pdf(self, file_path):

        logger.info(f"Opening PDF: {file_path}")

        text_parts = []

        try:

            with fitz.open(file_path) as doc:

                for page_number, page in enumerate(doc, start=1):

                    blocks = page.get_text("blocks")

                    if not blocks:
                        continue

                    # ----------------------------------------
                    # Sort blocks efficiently
                    # ----------------------------------------

                    blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

                    page_width = page.rect.width
                    center = page_width / 2

                    left_blocks = []
                    right_blocks = []

                    for block in blocks:

                        block_text = block[4].strip()

                        if not block_text:
                            continue

                        if block[0] < center:
                            left_blocks.append(block_text)
                        else:
                            right_blocks.append(block_text)

                    # ----------------------------------------
                    # Preserve two-column reading order
                    # ----------------------------------------

                    text_parts.extend(left_blocks)
                    text_parts.extend(right_blocks)

            text = "\n\n".join(text_parts)

            if text.strip():

                logger.info(f"PDF text extraction successful: {file_path}")

                return text

            # ----------------------------------------
            # No selectable text → OCR
            # ----------------------------------------

            logger.warning(f"No selectable text found. Switching to OCR: {file_path}")

            return self.read_pdf_ocr(file_path)

        except Exception as e:

            logger.error(f"PDF extraction failed: {file_path} | {e}")

            raise

    # =========================================================
    # DOCX EXTRACTION
    # =========================================================

    def read_docx(self, file_path):

        logger.info(f"Opening DOCX: {file_path}")

        text_parts = []

        try:

            doc = Document(file_path)

            # Paragraphs
            for para in doc.paragraphs:

                text = para.text.strip()

                if text:
                    text_parts.append(text)

            # Tables
            for table in doc.tables:

                for row in table.rows:

                    row_text = []

                    for cell in row.cells:

                        cell_text = cell.text.strip()

                        if cell_text:
                            row_text.append(cell_text)

                    if row_text:
                        text_parts.append(" | ".join(row_text))

            text = "\n".join(text_parts)

            logger.info(f"DOCX extraction successful: {file_path}")

            return text

        except Exception as e:

            logger.error(f"DOCX extraction failed: {file_path} | {e}")

            raise

    # =========================================================
    # OCR EXTRACTION
    # =========================================================

    def read_pdf_ocr(self, file_path):

        logger.info(f"Using OCR for: {file_path}")

        text_parts = []

        reader = self._get_ocr_reader()

        try:

            with fitz.open(file_path) as doc:

                for page_number, page in enumerate(doc, start=1):

                    logger.info(f"OCR processing page {page_number}")

                    # ----------------------------------------
                    # Lower DPI than previous 300 DPI
                    # ----------------------------------------
                    pix = page.get_pixmap(dpi=200, alpha=False)

                    image = Image.open(io.BytesIO(pix.tobytes("png")))

                    results = reader.readtext(image, detail=1)

                    for result in results:

                        if len(result) >= 2:

                            recognized_text = result[1].strip()

                            if recognized_text:
                                text_parts.append(recognized_text)

            text = "\n".join(text_parts)

            logger.info(f"OCR extraction completed: {file_path}")

            return text

        except Exception as e:

            logger.error(f"OCR extraction failed: {file_path} | {e}")

            raise

    # =========================================================
    # TEXT CLEANING
    # =========================================================

    def clean_text(self, text):

        if not text:
            return ""

        # Remove common contact emojis
        text = re.sub(r"[📍📞📧]", "", text)

        # Normalize dashes
        text = text.replace("–", "-")
        text = text.replace("—", "-")

        # Normalize bullets
        text = re.sub(r"[•●○▪►*✓■]", "-", text)

        # Normalize tabs
        text = text.replace("\t", " ")

        # Normalize spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Normalize blank lines
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        heading_map = {
            "ACADEMIC DETAILS": "Education",
            "EDUCATION": "Education",
            "EDUCATIONAL QUALIFICATION": "Education",
            "WORK EXPERIENCE": "Experience",
            "PROFESSIONAL EXPERIENCE": "Experience",
            "EMPLOYMENT HISTORY": "Experience",
            "EXPERIENCE": "Experience",
            "TECHNICAL SKILLS": "Skills",
            "CORE COMPETENCIES": "Skills",
            "SKILLS & TOOLS": "Skills",
            "SKILLS": "Skills",
            "PROJECTS": "Projects",
            "CERTIFICATIONS": "Certifications",
            "ACHIEVEMENTS": "Achievements",
            "LANGUAGES": "Languages",
        }

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            normalized_heading = heading_map.get(line.upper())

            if normalized_heading:
                line = normalized_heading

            lines.append(line)

        return "\n".join(lines).strip()

    # =========================================================
    # MAIN TEXT EXTRACTION
    # =========================================================

    def extract_text(self, file_path):

        # ----------------------------------------
        # Cache based on file modification time
        # ----------------------------------------

        try:
            modified_time = os.path.getmtime(file_path)
        except OSError:
            modified_time = None

        cache_key = (file_path, modified_time)

        if cache_key in self._text_cache:

            logger.info(f"Using cached resume text: {file_path}")

            return self._text_cache[cache_key]

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":

            text = self.read_pdf(file_path)

        elif extension == ".docx":

            text = self.read_docx(file_path)

        else:

            raise ValueError("Unsupported File Type")

        text = self.clean_text(text)

        # Keep cache small
        if len(self._text_cache) >= 20:
            self._text_cache.pop(next(iter(self._text_cache)))

        self._text_cache[cache_key] = text

        return text

    # =========================================================
    # SECTION EXTRACTION
    # =========================================================

    def extract_section(self, text, headings):

        lines = text.splitlines()

        section = []

        capture = False

        stop_headings = {
            "education",
            "experience",
            "skills",
            "projects",
            "certifications",
            "achievements",
            "languages",
            "internship",
            "profile",
            "professional profile",
            "academic qualifications",
            "core competencies",
            "technical skills",
            "personal details",
            "reference",
            "position of responsibility",
        }

        target_headings = {h.lower() for h in headings}

        for line in lines:

            normalized = line.strip()

            if not normalized:
                continue

            lower_line = normalized.lower()

            if any(lower_line.startswith(h.lower()) for h in headings):

                capture = True
                continue

            if capture:

                if lower_line in stop_headings and lower_line not in target_headings:
                    break

                section.append(normalized)

        return "\n".join(section)

    # =========================================================
    # SAVE OUTPUT
    # =========================================================

    def save_output(self, text, input_file):

        output_folder = "data/output"

        os.makedirs(output_folder, exist_ok=True)

        filename = os.path.splitext(os.path.basename(input_file))[0]

        output_file = os.path.join(output_folder, filename + ".txt")

        with open(output_file, "w", encoding="utf-8") as file:

            file.write(text)

        logger.info(f"Saved output to {output_file}")

        return output_file

    # =========================================================
    # BUILD PROFILE
    # =========================================================

    def build_resume_profile(self, text):

        logger.info("Building Resume Profile")

        sections = self.section_classifier.classify_sections(text)

        skills_text = "\n".join(
            filter(
                None,
                [
                    sections.get("skills", ""),
                    sections.get("experience", ""),
                    sections.get("projects", ""),
                ],
            )
        )

        profile = {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(skills_text),
            "education": self.extract_education(sections.get("education", "")),
            "experience": self.extract_experience(sections.get("experience", "")),
            "projects": self.extract_projects(sections.get("projects", "")),
            "certifications": self.extract_certifications(
                sections.get("certifications", "")
            ),
        }

        return profile

    # =========================================================
    # BASIC EXTRACTION
    # =========================================================

    def extract_email(self, text):

        pattern = r"[A-Za-z0-9._%+-]+" r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

        match = re.search(pattern, text)

        return match.group() if match else ""

    def extract_phone(self, text):

        pattern = r"(?:\+91[- ]?)?" r"[6-9]\d{9}"

        match = re.search(pattern, text)

        return match.group() if match else ""

    def extract_name(self, text):

        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if (
                line
                and len(line.split()) <= 4
                and "@" not in line
                and not re.search(r"\d", line)
            ):

                return line

        return ""

    # =========================================================
    # SKILLS
    # =========================================================

    def extract_skills(self, text):

        if not text:
            return []

        extracted = self.skill_extractor.extract_skills(text)

        skills = (
            extracted.get("technical_skills", [])
            + extracted.get("business_skills", [])
            + extracted.get("creative_skills", [])
        )

        return sorted(set(skills), key=str.lower)

    # =========================================================
    # EDUCATION
    # =========================================================

    def extract_education(self, text):

        if not text:
            return []

        degree_map = {
            "Bachelor of Technology": "B.Tech",
            "Bachelor of Engineering": "B.E",
            "Bachelor of Science": "B.Sc",
            "Bachelor of Computer Applications": "BCA",
            "Master of Technology": "M.Tech",
            "Master of Computer Applications": "MCA",
            "Master of Business Administration": "MBA",
            "B.Tech": "B.Tech",
            "B.E": "B.E",
            "B.Sc": "B.Sc",
            "BCA": "BCA",
            "M.Tech": "M.Tech",
            "MCA": "MCA",
            "MBA": "MBA",
            "Diploma": "Diploma",
            "SSLC": "SSLC",
            "Higher Secondary": "Higher Secondary",
            "Plus Two": "Higher Secondary",
        }

        education = []

        for key, value in degree_map.items():

            if re.search(re.escape(key), text, re.IGNORECASE):

                education.append(value)

        return list(dict.fromkeys(education))

    # =========================================================
    # EXPERIENCE
    # =========================================================

    def extract_experience(self, text):

        if not text:
            return ""

        return text.strip()

    # =========================================================
    # PROJECTS
    # =========================================================

    def extract_projects(self, text):

        if not text:
            return []

        projects = []

        for line in text.splitlines():

            line = line.strip()

            line = line.lstrip("-•* ")

            if not line:
                continue

            if line.lower().startswith("github"):
                continue

            if len(line.split()) > 10:
                continue

            projects.append(line)

        return list(dict.fromkeys(projects))

    # =========================================================
    # CERTIFICATIONS
    # =========================================================

    def extract_certifications(self, text):

        if not text:
            return []

        certifications = []

        for line in text.splitlines():

            line = line.strip()

            line = line.lstrip("-•* ")

            if line:
                certifications.append(line)

        return list(dict.fromkeys(certifications))

    # =========================================================
    # SAVE PROFILE
    # =========================================================

    def save_profile(self, profile, file_path):

        output_dir = "data/parsed_profiles"

        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.splitext(os.path.basename(file_path))[0]

        output_path = os.path.join(output_dir, filename + ".json")

        with open(output_path, "w", encoding="utf-8") as f:

            json.dump(profile, f, indent=4)

        logger.info(f"Profile Saved: {output_path}")

        return output_path



from email.mime import text

import fitz  # PyMuPDF
from docx import Document
import os
import re
import easyocr
from PIL import Image
import io
from utils.logger import logger


class ResumeParser:
    def __init__(self):
        logger.info("Initializing EasyOCR...")


        self.reader = easyocr.Reader(['en'])

    def read_pdf(self, file_path):

        logger.info(f"Opening PDF: {file_path}")

        text = ""

        doc = fitz.open(file_path)

        for page in doc:

            blocks = page.get_text("blocks")

            if not blocks:
                continue

        # Sort blocks by vertical position then horizontal position
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

            page_width = page.rect.width
            center = page_width / 2

            left_blocks = []
            right_blocks = []

            for block in blocks:

                x0 = block[0]

                if x0 < center:
                    left_blocks.append(block)
                else:
                    right_blocks.append(block)

        # Read left column first
            for block in left_blocks:

                block_text = block[4].strip()

                if block_text:
                    text += block_text + "\n\n"

        # Then read right column
            for block in right_blocks:

                block_text = block[4].strip()

                if block_text:
                    text += block_text + "\n\n"

        doc.close()

        logger.info(f"Successfully extracted PDF: {file_path}")

        if text.strip():

            logger.info("Text extracted successfully using PyMuPDF")

            return text

        logger.warning("No selectable text found. Switching to OCR.")

        return self.read_pdf_ocr(file_path)
    def read_docx(self, file_path):

        logger.info(f"Opening DOCX: {file_path}")

        doc = Document(file_path)

        text = ""

        for para in doc.paragraphs:

            if para.text.strip():
                text += para.text + "\n"

        logger.info(f"Successfully extracted DOCX: {file_path}")

        return text

    def read_pdf_ocr(self, file_path):

        logger.info(f"Using OCR for: {file_path}")

        text = ""

        doc = fitz.open(file_path)

        for page_number, page in enumerate(doc, start=1):

            logger.info(f"Processing OCR on page {page_number}")

        # Convert PDF page to image
            pix = page.get_pixmap(dpi=300)

            image = Image.open(io.BytesIO(pix.tobytes("png")))

        # Perform OCR
            results = self.reader.readtext(image)

        # Extract recognized text
            for result in results:

                text += result[1] + "\n"

        doc.close()

        logger.info(f"OCR extraction completed: {file_path}")

        return text

    def clean_text(self, text):
        """
        Clean and normalize extracted resume text.
        """

    # Remove emojis
        text = re.sub(r"[📍📞📧]", "", text)

    # Replace fancy dashes
        text = text.replace("–", "-")
        text = text.replace("—", "-")

    # Normalize bullets
        bullet_symbols = ["•", "●", "○", "▪", "►", "*", "✓", "■"]

        for bullet in bullet_symbols:
            text = text.replace(bullet, "-")

    # Replace tabs with spaces
        text = text.replace("\t", " ")

    # Remove extra spaces
        text = re.sub(r"[ ]{2,}", " ", text)

    # Remove extra blank lines
        text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Normalize section headings
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
            "LANGUAGES": "Languages"
        }

        lines = []

        for line in text.split("\n"):

            line = line.strip()

            upper_line = line.upper()

            if upper_line in heading_map:
                line = heading_map[upper_line]

            lines.append(line)

        text = "\n".join(lines)

        return text.strip()
    
    def extract_text(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            text = self.read_pdf(file_path)

        elif extension == ".docx":
            text = self.read_docx(file_path)

        else:
            raise ValueError("Unsupported File Type")

        return self.clean_text(text)

    def save_output(self, text, input_file):

        output_folder = "data/output"

        os.makedirs(output_folder, exist_ok=True)

        filename = os.path.splitext(os.path.basename(input_file))[0]

        output_file = os.path.join(output_folder, filename + ".txt")

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(text)

        logger.info(f"Saved output to {output_file}")

        return output_file
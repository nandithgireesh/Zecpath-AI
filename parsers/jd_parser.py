import os
import re
import json
import fitz  # PyMuPDF
from docx import Document
from utils.logger import logger


class JDParser:

    def __init__(self):
        """
        Initialize Job Description Parser.
        """

        logger.info("JD Parser Initialized")

    def read_txt(self, file_path):
        """
        Read job description from TXT file.
        """

        logger.info(f"Opening TXT: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        logger.info(f"Successfully extracted TXT: {file_path}")

        return text

    def read_pdf(self, file_path):
        """
        Read Job Description from PDF using PyMuPDF.
        Supports multi-column layouts.
        """

        logger.info(f"Opening PDF: {file_path}")

        text = ""

        doc = fitz.open(file_path)

        for page in doc:

            blocks = page.get_text("blocks")

            if not blocks:
                continue

            # Sort blocks from top to bottom, then left to right
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

            # Read right column
            for block in right_blocks:

                block_text = block[4].strip()

                if block_text:
                    text += block_text + "\n\n"

        doc.close()

        logger.info(f"Successfully extracted PDF: {file_path}")

        return text

    def read_docx(self, file_path):
        """
        Read Job Description from DOCX.
        """

        logger.info(f"Opening DOCX: {file_path}")

        doc = Document(file_path)

        text = ""

        for para in doc.paragraphs:

            if para.text.strip():

                text += para.text + "\n"

        logger.info(f"Successfully extracted DOCX: {file_path}")

        return text

    def extract_text(self, file_path):
        """
        Extract text from Job Description.
        Automatically detects TXT, PDF and DOCX.
        """

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".txt":

            text = self.read_txt(file_path)

        elif extension == ".pdf":

            text = self.read_pdf(file_path)

        elif extension == ".docx":

            text = self.read_docx(file_path)

        else:

            raise ValueError("Unsupported File Type")

        return self.clean_text(text)

    def clean_text(self, text):
        """
        Clean and normalize Job Description text.
        """

        # Remove common emojis
        text = re.sub(r"[📍📧📞]", "", text)

        # Replace fancy dashes
        text = text.replace("–", "-")
        text = text.replace("—", "-")

        # Normalize bullets
        bullet_symbols = ["•", "●", "○", "▪", "►", "*", "✓", "■"]

        for bullet in bullet_symbols:
            text = text.replace(bullet, "-")

        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Remove multiple spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Remove extra blank lines
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        # Normalize common headings
        heading_map = {
            "REQUIRED SKILLS": "Skills",
            "SKILLS REQUIRED": "Skills",
            "TECHNICAL SKILLS": "Skills",
            "SKILLS": "Skills",
            "JOB ROLE": "Role",
            "POSITION": "Role",
            "JOB TITLE": "Role",
            "QUALIFICATION": "Education",
            "EDUCATION": "Education",
            "EXPERIENCE": "Experience",
            "WORK EXPERIENCE": "Experience",
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

    def extract_role(self, text):
        """
        Extract Job Role from Job Description.
        """

        logger.info("Extracting Job Role")

        patterns = [
            r"Job\s*Title\s*:\s*(.+)",
            r"Position\s*:\s*(.+)",
            r"Role\s*:\s*(.+)",
            r"Designation\s*:\s*(.+)",
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                return match.group(1).strip()

        # Fallback: first non-empty line
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        if lines:
            return lines[0]

        return "Not Specified"

    def extract_skills(self, text):

        logger.info("Extracting Skills")

        skills_text = self.get_skills_section(text)

        skills = []

        known_skills = [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "TensorFlow",
            "PyTorch",
            "SQL",
            "Git",
            "Docker",
            "Linux",
            "AWS",
            "Azure",
            "Networking",
            "DNS",
            "Firewall",
            "Security",
            "Troubleshooting",
            "Communication",
            "Creativity",
            "Analytical Thinking",
            "Project Management",
            "Technical Knowledge",
            "SEO",
            "CRM",
            "Excel",
            "Power BI",
            "Business Analysis",
            "Requirement Gathering",
            "Data Analysis",
            "Stakeholder Management",
            "Patient Care",
            "Clinical Nursing",
            "Emergency Care",
            "Medication Administration",
            "Critical Care",
            "Documentation",
        ]

        for line in skills_text.split("\n"):

            line = line.strip().lstrip("•-* ")

            if not line:
                continue

            # Case 1: Communication: Excellent...
            if ":" in line:

                skills.append(line.split(":")[0].strip())

            # Case 2: Search known skills inside long sentence
            for skill in known_skills:

                if re.search(r"\b" + re.escape(skill) + r"\b", line, re.IGNORECASE):

                    skills.append(skill)

            # Case 3: Standalone short skill
            if len(line.split()) <= 4 and ":" not in line:

                skills.append(line)

        skills = list(dict.fromkeys(skills))

        logger.info(f"Skills Found: {skills}")

        return skills

    def extract_experience(self, text):
        """
        Extract the Experience section from the Job Description.
        """

        logger.info("Extracting Experience")

        lines = text.split("\n")

        experience = []
        capture = False

        stop_headers = [
            "Education",
            "Qualification",
            "Responsibilities",
            "Preferred Skills",
            "Preferred Certifications",
            "Employment Type",
            "Skills",
            "Required Skills",
            "Key Responsibilities",
        ]

        for line in lines:

            line = line.strip()
            match = re.match(r"Experience\s*:\s*(.+)", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            # Start capturing after the Experience heading
            if line.lower().startswith("experience"):
                capture = True
                continue

            if capture:

                # Stop when the next heading begins
                if any(line.lower().startswith(h.lower()) for h in stop_headers):
                    break

                if line:
                    experience.append(line)

        if experience:
            return " ".join(experience)

        return "Not Specified"

    def extract_education(self, text):
        """
        Extract education from Qualification section.
        """

        logger.info("Extracting Education")

        qualification_text = self.get_qualification_section(text)

        keywords = {
            "B.Tech": "B.Tech",
            "B.E": "B.E",
            "M.Tech": "M.Tech",
            "MCA": "MCA",
            "MBA": "MBA",
            "BCA": "BCA",
            "B.Sc": "B.Sc",
            "Engineering": "Engineering",
            "Computer Science": "Computer Science",
            "CS": "CS",
            "IT": "Information Technology",
            "Information Technology": "Information Technology",
            "UG": "UG",
            "PG": "PG",
            "Graduate": "Graduate",
            "Post Graduate": "Post Graduate",
        }

        education = []

        for key, value in keywords.items():

            if re.search(
                r"\b" + re.escape(key) + r"\b", qualification_text, re.IGNORECASE
            ):

                education.append(value)

        education = list(dict.fromkeys(education))

        logger.info(f"Education Found: {education}")

        return education

    def normalize_skills(self, skills):
        """
        Normalize extracted skills by replacing synonyms
        and removing duplicates.
        """

        logger.info("Normalizing Skills")

        skill_map = {
            "ML": "Machine Learning",
            "Machine Learning": "Machine Learning",
            "AI": "Artificial Intelligence",
            "Artificial Intelligence": "Artificial Intelligence",
            "DL": "Deep Learning",
            "Deep Learning": "Deep Learning",
            "JS": "JavaScript",
            "Java Script": "JavaScript",
            "Py": "Python",
            "Python": "Python",
            "SQL": "SQL",
            "MySQL": "MySQL",
            "PostgreSQL": "PostgreSQL",
            "TF": "TensorFlow",
            "Tensor Flow": "TensorFlow",
            "TensorFlow": "TensorFlow",
            "CV": "Computer Vision",
            "NLP": "Natural Language Processing",
        }

        normalized = []

        for skill in skills:

            skill = skill.strip()

            if skill in skill_map:

                normalized.append(skill_map[skill])

            else:

                normalized.append(skill)

        # Remove duplicates while preserving order
        normalized = list(dict.fromkeys(normalized))

        logger.info(f"Normalized Skills: {normalized}")

        return normalized

    def normalize_role(self, role):
        """
        Normalize different job role names.
        """

        logger.info("Normalizing Job Role")

        role_map = {
            "Software Engineer": "Software Developer",
            "Software Developer": "Software Developer",
            "Backend Engineer": "Backend Developer",
            "Backend Developer": "Backend Developer",
            "Frontend Engineer": "Frontend Developer",
            "Frontend Developer": "Frontend Developer",
            "Full Stack Engineer": "Full Stack Developer",
            "Full Stack Developer": "Full Stack Developer",
            "ML Engineer": "Machine Learning Engineer",
            "Machine Learning Engineer": "Machine Learning Engineer",
            "AI Engineer": "Artificial Intelligence Engineer",
            "Artificial Intelligence Engineer": "Artificial Intelligence Engineer",
            "Data Engineer": "Data Engineer",
            "Data Scientist": "Data Scientist",
            "Python Developer": "Python Developer",
            "DevOps Engineer": "DevOps Engineer",
        }

        role = role.strip()

        if role in role_map:

            normalized_role = role_map[role]

        else:

            normalized_role = role

        logger.info(f"Normalized Role: {normalized_role}")

        return normalized_role

    def build_job_object(self, text):
        """
        Build structured Job Requirement Object.
        """

        logger.info("Building Job Requirement Object")

        role = self.extract_role(text)

        role = self.normalize_role(role)

        skills = self.extract_skills(text)

        skills = self.normalize_skills(skills)

        experience = self.extract_experience(text)

        education = self.extract_education(text)

        job_object = {
            "role": role,
            "skills": skills,
            "experience": experience,
            "education": education,
        }

        logger.info("Job Requirement Object Created Successfully")

        return job_object

    def save_output(self, job_object, input_file):

        logger.info("Saving Job Requirement Object")

        output_folder = "data/jd_output"

        os.makedirs(output_folder, exist_ok=True)

        filename = os.path.splitext(os.path.basename(input_file))[0]

        output_file = os.path.join(output_folder, filename + ".json")

        with open(output_file, "w", encoding="utf-8") as file:

            json.dump(job_object, file, indent=4, ensure_ascii=False)

        logger.info(f"Output Saved: {output_file}")

        return output_file

    def get_qualification_section(self, text):
        """
        Extract only the Qualification/Education section.
        """

        lines = text.split("\n")

        section = []

        capture = False

        stop_headers = [
            "Responsibilities",
            "Required Skills",
            "Preferred Skills",
            "Benefits",
            "Job Description",
            "Experience",
            "Employment Type",
            "Location",
            "Company",
        ]

        for line in lines:

            line = line.strip()

            # Start capturing
            if line.lower().startswith(("qualification", "education", "eligibility")):
                capture = True
                continue

            if capture:

                # Stop when another heading starts
                if any(line.lower().startswith(h.lower()) for h in stop_headers):
                    break

                if line:
                    section.append(line)

        return "\n".join(section)

    def get_skills_section(self, text):
        """
        Extract only the Skills section.
        """

        lines = text.split("\n")

        section = []

        capture = False

        start_headers = [
            "Skills",
            "Required Skills",
            "Required Skills & Qualifications",
            "Preferred Skills",
            "Technical Skills",
        ]

        stop_headers = [
            "Qualification",
            "Qualifications",
            "Education",
            "Experience",
            "Responsibilities",
            "Benefits",
            "Employment Type",
            "Location",
            "Company",
            "Work Flexibility",
            "Support Requirements",
            "Application Process",
            "About Company",
            "How to Apply",
            "Job Description",
        ]

        for line in lines:

            line = line.strip()

            if any(line.lower().startswith(h.lower()) for h in start_headers):
                capture = True
                continue

            if capture:

                if any(line.lower().startswith(h.lower()) for h in stop_headers):
                    break

                if line:
                    section.append(line)

        return "\n".join(section)

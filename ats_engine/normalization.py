import re


class ResumeNormalizer:

    def __init__(self):
        pass

    def normalize_text(self, text):
        """
        Normalize general text:
        - Handle empty values
        - Convert to lowercase
        - Remove extra whitespace
        - Remove unnecessary punctuation
        """

        if not text:
            return ""

        text = str(text).lower()

        # Replace newlines and tabs with spaces
        text = re.sub(r"[\n\r\t]+", " ", text)

        # Remove unnecessary punctuation
        text = re.sub(r"[^\w\s+#.-]", " ", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def normalize_list(self, items):
        """
        Normalize a list such as skills or certifications.
        """

        if not items:
            return []

        normalized = []

        for item in items:

            value = self.normalize_text(item)

            if value and value not in normalized:
                normalized.append(value)

        return sorted(normalized)

    def normalize_resume(self, resume):
        """
        Convert a parsed resume into a standard format.
        """

        if not isinstance(resume, dict):
            return {}

        normalized_resume = {
            "skills": self.normalize_list(resume.get("skills", [])),
            "experience": self.normalize_text(resume.get("experience", "")),
            "education": self.normalize_text(resume.get("education", "")),
            "projects": self.normalize_list(resume.get("projects", [])),
            "certifications": self.normalize_list(resume.get("certifications", [])),
        }

        return normalized_resume

import re

from networkx import degree


class EducationParser:

    def __init__(self):

        self.degree_patterns = [
            r"\bBachelor of Technology\b",
            r"\bB\.?Tech\b",
            r"\bBachelor of Science\b",
            r"\bB\.?Sc\b",
            r"\bMaster of Technology\b",
            r"\bM\.?Tech\b",
            r"\bMaster of Science\b",
            r"\bM\.?Sc\b",
            r"\bBachelor of Engineering\b",
            r"\bB\.?E\b",
            r"\bMaster of Business Administration\b",
            r"\bMBA\b",
            r"\bMCA\b",
            r"\bBCA\b",
            r"\bDiploma\b",
            r"\bPhD\b",
            r"\bHigher Secondary\b",
            r"\bSSLC\b",
        ]

        self.field_patterns = [
            "Artificial Intelligence and Machine Learning",
            "Artificial Intelligence & Machine Learning",
            "AI & ML",
            "Machine Learning",
            "Artificial Intelligence",
            "Computer Science",
            "Computer Engineering",
            "Information Technology",
            "Data Science",
            "Electronics",
            "Electrical Engineering",
            "Mechanical Engineering",
            "Civil Engineering",
            "Business Administration",
            "Nursing",
        ]
        self.degree_mapping = {
            "b.tech": "Bachelor of Technology",
            "btech": "Bachelor of Technology",
            "b.e": "Bachelor of Engineering",
            "be": "Bachelor of Engineering",
            "b.sc": "Bachelor of Science",
            "bsc": "Bachelor of Science",
            "m.tech": "Master of Technology",
            "mtech": "Master of Technology",
            "m.sc": "Master of Science",
            "msc": "Master of Science",
            "mba": "Master of Business Administration",
            "mca": "Master of Computer Applications",
            "bca": "Bachelor of Computer Applications",
            "phd": "Doctor of Philosophy",
        }
        self.certification_mapping = {
            "azure ai fundamentals": "Microsoft Azure AI Fundamentals",
            "azure fundamentals": "Microsoft Azure Fundamentals",
            "aws ccp": "AWS Certified Cloud Practitioner",
            "aws certified cloud practitioner": "AWS Certified Cloud Practitioner",
            "tensorflow": "TensorFlow",
            "tensor flow": "TensorFlow",
            "gen ai": "Generative AI",
            "generative ai": "Generative AI",
            "prompt engineering": "Prompt Engineering",
            "ccna": "Cisco Certified Network Associate",
            "udemy": "Udemy",
            "coursera": "Coursera",
        }
        self.certification_categories = {
            "Artificial Intelligence": [
                "TensorFlow",
                "Generative AI",
                "Prompt Engineering",
                "Machine Learning",
                "Deep Learning",
                "NLP",
                "Computer Vision",
            ],
            "Cloud Computing": [
                "AWS Certified Cloud Practitioner",
                "Microsoft Azure Fundamentals",
                "Microsoft Azure AI Fundamentals",
            ],
            "Networking": ["Cisco Certified Network Associate"],
            "Programming": ["Python", "The Joy of Computing Using Python"],
            "Digital Marketing": ["The Fundamentals of Digital Marketing"],
        }

    def extract_degree(self, text):
        """
        Extract degree type.
        """

        for pattern in self.degree_patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:

                return match.group()

        return None

    def extract_field(self, text):
        """
        Extract field of study.
        """

        for field in self.field_patterns:

            if field.lower() in text.lower():

                return field

        return None

    def extract_graduation_year(self, text):
        """
        Extract graduation year for the highest degree.
        """

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for i, line in enumerate(lines):

            # Check if this line contains a degree
            if self.extract_degree(line):

                # Look at the next two lines for years
                for j in range(i + 1, min(i + 3, len(lines))):

                    years = re.findall(r"\b(?:19|20)\d{2}\b", lines[j])

                    if years:

                        return years[-1]

                    if "present" in lines[j].lower():

                        return "Present"

        return None

    import re

    def extract_institution(self, text):
        """
        Extract institution.
        """

        lines = text.split("\n")

        keywords = [
            "college",
            "university",
            "institute",
            "school",
            "academy",
        ]

        for line in lines:

            lower = line.lower()

            for keyword in keywords:

                if keyword in lower:

                    institution = line.strip()

                    # Remove appended year range if present
                    institution = re.sub(
                        r"\|\s*\d{4}\s*-\s*\d{4}", "", institution
                    ).strip()

                    return institution

        return None

    def extract_certifications(self, text):
        """
        Extract certifications from the certification section.
        """

        if not text:
            return []

        certifications = []

        # Split into individual lines
        lines = text.split("\n")

        for line in lines:

            line = line.strip(" -•\t")

            if not line:
                continue

            # Remove trailing year
            line = re.sub(r",?\s*\d{4}$", "", line).strip()

            certifications.append(line)

        return certifications

    def normalize_degree(self, degree):
        """
        Normalize degree names.
        """

        if not degree:
            return None

        value = degree.lower().replace(".", "").strip()

        if value in self.degree_mapping:
            return self.degree_mapping[value]

        return degree

    def normalize_certifications(self, certifications):
        """
        Normalize certification names.
        """

        normalized = []

        for cert in certifications:

            value = cert.lower().strip()

            found = False

            for key, standard in self.certification_mapping.items():

                if key in value:

                    normalized.append(standard)

                    found = True

                    break

            if not found:

                normalized.append(cert)

        return sorted(list(set(normalized)))

    def categorize_certifications(self, certifications):
        """
        Assign relevance categories to certifications.
        """

        categorized = []

        for cert in certifications:

            category = "Other"

            for cat, cert_list in self.certification_categories.items():

                for known_cert in cert_list:

                    if known_cert.lower() in cert.lower():

                        category = cat
                        break

                if category != "Other":
                    break

            categorized.append({"certification": cert, "category": category})

        return categorized

    def parse_education(self, education_text, certification_text=""):
        """
        Parse education and certifications.
        """

        degree = self.extract_degree(education_text)

        degree = self.normalize_degree(degree)
        certifications = self.extract_certifications(certification_text)

        certifications = self.normalize_certifications(certifications)
        certifications = self.categorize_certifications(certifications)
        return {
            "degree": degree,
            "field_of_study": self.extract_field(education_text),
            "institution": self.extract_institution(education_text),
            "graduation_year": self.extract_graduation_year(education_text),
            "certifications": certifications,
        }

import re
from datetime import datetime

from data.experience.job_titles import JOB_TITLES
from parsers.role_relevance import RoleRelevanceAnalyzer


class ExperienceParser:

    def __init__(self):
        self.role_analyzer = RoleRelevanceAnalyzer()

        self.job_titles = JOB_TITLES

    def extract_job_title(self, text):
        """
        Extract job title from experience text.
        Prefer the longest matching title.
        """

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Sort longest titles first
        titles = sorted(self.job_titles, key=len, reverse=True)

        for line in lines:

            lower = line.lower()

            for title in titles:

                if lower == title.lower():

                    return title.title()

                if title.lower() in lower:

                    return title.title()

        return None

    def is_internship(self, text):
        """
        Detect internship-related experience.
        """

        keywords = [
            "internship",
            "intern",
            "clinical intern",
            "industrial training",
            "summer internship",
            "winter internship",
            "trainee",
            "graduate trainee",
        ]

        lower = text.lower()

        for word in keywords:

            if word in lower:
                return True

        return False

    def extract_dates(self, text):
        """
        Extract employment date ranges.
        """

        pattern = r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\s*[-–]\s*(Present|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})"

        matches = re.findall(pattern, text, re.IGNORECASE)

        durations = []

        for start, end in matches:

            durations.append({"start_date": start, "end_date": end})
        return durations

    def extract_duration_text(self, text):
        """
        Extract durations like:
        6 Months
        2 Years
        """

        pattern = r"\b\d+\s+(?:Month|Months|Year|Years)\b"

        matches = re.findall(pattern, text, re.IGNORECASE)

        return matches

    def calculate_total_experience(self, durations):
        """
        Calculate total experience in years and months.
        """

        total_months = 0

        for duration in durations:

            # Handle internship durations like "6 Months"
            if "duration" in duration:

                value = duration["duration"]

                number = int(value.split()[0])

                if "month" in value.lower():

                    total_months += number

                elif "year" in value.lower():

                    total_months += number * 12

                continue

            # Handle normal employment dates
            start = duration["start_date"]
            end = duration["end_date"]

            try:

                start_date = datetime.strptime(start, "%B %Y")

                if end.lower() == "present":

                    end_date = datetime.today()

                else:

                    end_date = datetime.strptime(end, "%B %Y")

                months = (end_date.year - start_date.year) * 12 + (
                    end_date.month - start_date.month
                )

                total_months += months

            except Exception:
                continue
        years = total_months // 12
        months = total_months % 12

        return {"years": years, "months": months, "total_months": total_months}

    def detect_gaps(self, durations):
        """
        Detect employment gaps between jobs.
        """

        if len(durations) <= 1:
            return []

        parsed = []

        for duration in durations:

            try:

                start = datetime.strptime(duration["start_date"], "%B %Y")

                if duration["end_date"].lower() == "present":
                    end = datetime.today()
                else:
                    end = datetime.strptime(duration["end_date"], "%B %Y")

                parsed.append((start, end))

            except Exception:
                continue

        parsed.sort(key=lambda x: x[0])

        gaps = []

        for i in range(len(parsed) - 1):

            previous_end = parsed[i][1]
            next_start = parsed[i + 1][0]

            months = (next_start.year - previous_end.year) * 12 + (
                next_start.month - previous_end.month
            )

            if months > 1:

                gaps.append({"gap_months": months})

        return gaps

    def detect_overlaps(self, durations):
        """
        Detect overlapping employment periods.
        """

        if len(durations) <= 1:
            return []

        parsed = []

        for duration in durations:

            try:

                # Internship durations (e.g., "6 Months") are ignored
                if "duration" in duration:
                    continue

                start = datetime.strptime(duration["start_date"], "%B %Y")

                if duration["end_date"].lower() == "present":
                    end = datetime.today()
                else:
                    end = datetime.strptime(duration["end_date"], "%B %Y")

                parsed.append((start, end))

            except Exception:
                continue

        parsed.sort(key=lambda x: x[0])

        overlaps = []

        for i in range(len(parsed) - 1):

            current_start, current_end = parsed[i]
            next_start, next_end = parsed[i + 1]

            if next_start < current_end:

                overlaps.append(
                    {
                        "current_job": current_start.strftime("%B %Y")
                        + " - "
                        + current_end.strftime("%B %Y"),
                        "next_job": next_start.strftime("%B %Y")
                        + " - "
                        + next_end.strftime("%B %Y"),
                        "overlap": True,
                    }
                )

        return overlaps

    def extract_company(self, text):
        """
        Extract company or internship organization.
        """

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Case 1
        # Company | Job Title

        for line in lines:

            if "|" in line:

                return line.split("|")[0].strip()

        # Case 2
        # Internship

        if self.is_internship(text):

            for line in lines:

                if "hospital" in line.lower():
                    return line

                if "company" in line.lower():
                    return line

                if "technologies" in line.lower():
                    return line

                if "solutions" in line.lower():
                    return line

        return None

    def parse_experience(self, text, target_role=None):
        """
        Parse structured experience information.
        """

        durations = self.extract_dates(text)

        if not durations and self.is_internship(text):

            duration_text = self.extract_duration_text(text)

            if duration_text:

                durations = [{"duration": duration_text[0]}]

        job_title = self.extract_job_title(text)

        company = self.extract_company(text)

        relevance = self.role_analyzer.calculate_similarity(job_title, target_role)

        return {
            "job_title": job_title,
            "company": company,
            "employment_duration": durations,
            "total_experience": self.calculate_total_experience(durations),
            "employment_gaps": self.detect_gaps(durations),
            "employment_overlaps": self.detect_overlaps(durations),
            "role_relevance": relevance,
        }

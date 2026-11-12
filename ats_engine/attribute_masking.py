import re


class AttributeMasker:

    def __init__(self):
        pass

    def mask_email(self, text):
        """Mask email addresses."""

        if not text:
            return text

        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

        return re.sub(
            pattern,
            "[MASKED_EMAIL]",
            text,
        )

    def mask_phone(self, text):
        """Mask common phone number formats."""

        if not text:
            return text

        pattern = r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)"

        return re.sub(
            pattern,
            "[MASKED_PHONE]",
            text,
        )

    def mask_urls(self, text):
        """Mask personal/profile URLs."""

        if not text:
            return text

        pattern = r"(https?://\S+|www\.\S+)"

        return re.sub(
            pattern,
            "[MASKED_URL]",
            text,
        )

    def mask_personal_text(self, text):
        """
        Mask contact-related information from resume text.
        """

        if not text:
            return ""

        text = str(text)

        text = self.mask_email(text)
        text = self.mask_phone(text)
        text = self.mask_urls(text)

        return text

    def mask_resume(self, resume):
        """
        Create a copy of a resume with non-essential
        contact attributes masked.

        Qualification-related fields such as skills,
        experience, education and projects are preserved.
        """

        if not isinstance(resume, dict):
            return {}

        masked_resume = dict(resume)

        # --------------------------------
        # Mask direct personal fields
        # --------------------------------

        personal_fields = [
            "name",
            "full_name",
            "phone",
            "mobile",
            "email",
            "address",
            "location",
        ]

        for field in personal_fields:

            if field in masked_resume:

                masked_resume[field] = "[MASKED]"

        # --------------------------------
        # Mask contact information inside
        # text fields
        # --------------------------------

        text_fields = [
            "summary",
            "profile",
            "experience",
            "education",
        ]

        for field in text_fields:

            if isinstance(
                masked_resume.get(field),
                str,
            ):

                masked_resume[field] = self.mask_personal_text(masked_resume[field])

        return masked_resume

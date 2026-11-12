from parsers.education_parser import EducationParser
from parsers.education_relevance import EducationRelevanceAnalyzer


class AcademicProfileBuilder:

    def __init__(self):

        self.education_parser = EducationParser()
        self.education_relevance = EducationRelevanceAnalyzer()

    def build_profile(
        self,
        education_text,
        certification_text="",
        target_role=None,
    ):
        """
        Build a structured academic profile.
        """

        # Parse education details
        profile = self.education_parser.parse_education(
            education_text,
            certification_text,
        )

        # Add education relevance only if a target role is given
        if target_role:

            profile["education_relevance"] = (
                self.education_relevance.calculate_similarity(
                    profile["degree"],
                    profile["field_of_study"],
                    target_role,
                )
            )

        else:

            profile["education_relevance"] = {
                "score": None,
                "relevance": "Not Evaluated",
            }

        return profile

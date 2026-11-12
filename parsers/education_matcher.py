from parsers.similarity_scorer import SimilarityScorer


class EducationMatcher:

    def __init__(self):
        self.scorer = SimilarityScorer()

    def compare_education(
        self,
        resume_education,
        jd_education,
    ):
        """
        Compare resume education with JD education.
        """

        # Handle missing data
        if not resume_education or not jd_education:
            return {
                "score": 0.0,
                "match": "No Data",
            }

        # Convert lists to text if necessary
        if isinstance(resume_education, list):
            resume_education = " ".join(str(item) for item in resume_education)

        if isinstance(jd_education, list):
            jd_education = " ".join(str(item) for item in jd_education)

        # Semantic similarity
        score = self.scorer.calculate_similarity(
            resume_education,
            jd_education,
        )

        # Convert negative similarity to zero
        score = max(0.0, score)

        if score >= 0.75:
            level = "High"

        elif score >= 0.50:
            level = "Medium"

        else:
            level = "Low"

        return {
            "score": score,
            "match": level,
        }

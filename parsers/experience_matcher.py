from parsers.similarity_scorer import SimilarityScorer


class ExperienceMatcher:

    def __init__(self):

        self.scorer = SimilarityScorer()

    def compare_experience(self, resume_experience, jd_experience):
        """
        Compare resume experience summary with job experience requirement.
        """

        if not resume_experience or not jd_experience:

            return {"score": 0.0, "match": "No Data"}

        score = self.scorer.calculate_similarity(
            resume_experience,
            jd_experience,
        )

        if score >= 0.75:

            level = "High"

        elif score >= 0.50:

            level = "Medium"

        else:

            level = "Low"

        return {"score": score, "match": level}

from parsers.similarity_scorer import SimilarityScorer


class ProjectMatcher:

    def __init__(self):

        self.scorer = SimilarityScorer()

    def compare_projects(self, resume_projects, jd_projects):
        """
        Compare resume project descriptions with
        job description project requirements.
        """

        if not resume_projects or not jd_projects:

            return {"score": 0.0, "match": "No Data"}

        score = self.scorer.calculate_similarity(
            resume_projects,
            jd_projects,
        )

        if score >= 0.70:

            level = "High"

        elif score >= 0.45:

            level = "Medium"

        else:

            level = "Low"

        return {"score": score, "match": level}

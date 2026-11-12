from parsers.similarity_scorer import SimilarityScorer


class SkillMatcher:

    def __init__(self):
        self.scorer = SimilarityScorer()

    def compare_skills(self, resume_skills, jd_skills):
        """
        Compare resume skills with JD skills using
        semantic similarity rather than relying only
        on exact keyword matching.
        """

        # --------------------------------
        # Handle empty data
        # --------------------------------

        if not resume_skills or not jd_skills:

            return {
                "score": 0.0,
                "match": "No Data",
                "matching_method": "semantic",
            }

        # --------------------------------
        # Convert lists to text
        # --------------------------------

        if isinstance(resume_skills, list):

            resume_skills = " ".join(
                str(skill).strip() for skill in resume_skills if skill
            )

        if isinstance(jd_skills, list):

            jd_skills = " ".join(str(skill).strip() for skill in jd_skills if skill)

        # --------------------------------
        # Semantic similarity
        # --------------------------------

        score = self.scorer.calculate_similarity(
            resume_skills,
            jd_skills,
        )

        # --------------------------------
        # Safety normalization
        # --------------------------------

        score = max(
            0.0,
            min(1.0, float(score)),
        )

        # --------------------------------
        # Match level
        # --------------------------------

        if score >= 0.75:

            level = "High"

        elif score >= 0.50:

            level = "Medium"

        else:

            level = "Low"

        return {
            "score": round(score, 2),
            "match": level,
            "matching_method": "semantic",
        }

from sentence_transformers import SentenceTransformer
from sentence_transformers import util


class RoleRelevanceAnalyzer:

    def __init__(self):

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def calculate_similarity(self, resume_role, jd_role):
        """
        Calculate semantic similarity between
        resume role and job description role.
        """

        if not resume_role or not jd_role:

            return {"score": 0.0, "relevance": "No Experience"}

        resume_embedding = self.model.encode(resume_role, convert_to_tensor=True)

        jd_embedding = self.model.encode(jd_role, convert_to_tensor=True)

        score = util.cos_sim(resume_embedding, jd_embedding).item()

        if score >= 0.75:
            level = "High"
        elif score >= 0.45:
            level = "Medium"
        else:
            level = "Low"

        return {"score": round(score, 2), "relevance": level}

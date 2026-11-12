from sentence_transformers import SentenceTransformer
from sentence_transformers import util


class EducationRelevanceAnalyzer:

    def __init__(self):

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def calculate_similarity(self, degree, field, target_role):
        """
        Compare education with the target job role.
        """

        if not target_role:
            return {"score": 0.0, "relevance": "Unknown"}

        education = ""

        if degree:
            education += degree + " "

        if field:
            education += field

        if not education.strip():
            return {"score": 0.0, "relevance": "No Education"}

        education_embedding = self.model.encode(education, convert_to_tensor=True)

        job_embedding = self.model.encode(target_role, convert_to_tensor=True)

        score = util.cos_sim(education_embedding, job_embedding).item()

        if score >= 0.60:
            level = "High"

        elif score >= 0.40:
            level = "Medium"

        else:
            level = "Low"

        return {"score": round(score, 2), "relevance": level}

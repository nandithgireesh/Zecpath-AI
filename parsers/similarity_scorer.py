from sentence_transformers import util

from parsers.semantic_matcher import SemanticMatcher


class SimilarityScorer:

    def __init__(self):
        self.matcher = SemanticMatcher()

    def calculate_similarity(self, resume_text, jd_text):
        """
        Calculate semantic similarity between resume and JD.

        Supports both:
        - single strings
        - lists of strings

        Returns a single score between 0.0 and 1.0.
        """

        if not resume_text or not jd_text:
            return 0.0

        # --------------------------------
        # Convert lists to text
        # --------------------------------

        if isinstance(resume_text, list):
            resume_text = " ".join(str(item) for item in resume_text)

        if isinstance(jd_text, list):
            jd_text = " ".join(str(item) for item in jd_text)

        # Make sure both are strings
        resume_text = str(resume_text)
        jd_text = str(jd_text)

        # --------------------------------
        # Generate embeddings
        # --------------------------------

        resume_embedding = self.matcher.get_embedding(resume_text)

        jd_embedding = self.matcher.get_embedding(jd_text)

        # --------------------------------
        # Cosine similarity
        # --------------------------------

        cosine_tensor = util.cos_sim(
            resume_embedding,
            jd_embedding,
        )

        # cos_sim should now be [1, 1]
        cosine_score = cosine_tensor.squeeze().item()

        # --------------------------------
        # Normalize
        # --------------------------------

        normalized_score = (cosine_score + 1.0) / 2.0

        # --------------------------------
        # Safety boundary
        # --------------------------------

        normalized_score = max(
            0.0,
            min(1.0, normalized_score),
        )

        return round(
            normalized_score,
            2,
        )

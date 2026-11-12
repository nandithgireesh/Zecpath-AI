from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_semantic_model():
    """
    Load the SentenceTransformer model only once and reuse it.
    This reduces repeated model loading and improves memory handling.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


class SemanticMatcher:

    def __init__(self):
        self.model = get_semantic_model()

    def get_embedding(self, text):
        """
        Convert text into semantic embedding.
        """

        if not text:
            text = ""

        # Convert list into a single text string
        if isinstance(text, list):
            text = " ".join(str(item) for item in text)

        text = str(text)

        return self.model.encode(text, convert_to_tensor=True)

class ScoreNormalizer:

    def normalize(self, score):
        """
        Normalize a score to the range 0.0 - 1.0.
        """

        if score is None:
            return 0.0

        try:
            score = float(score)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(1.0, score))

    def to_percentage(self, score):
        """
        Convert normalized score (0.0 - 1.0)
        to percentage (0 - 100).
        """

        normalized_score = self.normalize(score)

        return round(normalized_score * 100, 2)

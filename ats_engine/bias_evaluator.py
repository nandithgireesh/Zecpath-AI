class BiasEvaluator:

    def __init__(self, tolerance=0.05):
        """
        tolerance:
        Maximum acceptable score difference between
        equivalent resumes.
        """

        self.tolerance = tolerance

    def calculate_difference(self, score_a, score_b):
        """Calculate absolute difference between two scores."""

        return round(
            abs(float(score_a) - float(score_b)),
            4,
        )

    def evaluate(self, score_a, score_b):
        """
        Evaluate whether two equivalent candidates have
        a significant score difference.
        """

        difference = self.calculate_difference(
            score_a,
            score_b,
        )

        if difference <= self.tolerance:
            status = "PASS"
            indicator = "Low Bias"
        else:
            status = "REVIEW"
            indicator = "Potential Bias"

        return {
            "score_a": round(float(score_a), 2),
            "score_b": round(float(score_b), 2),
            "difference": difference,
            "tolerance": self.tolerance,
            "status": status,
            "bias_indicator": indicator,
        }

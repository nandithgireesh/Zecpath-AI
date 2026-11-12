import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ats_engine.weights import get_weights


class ATSScorer:

    def __init__(self, role=None):

        self.role = role
        self.weights = get_weights(role)

    def calculate_score(
        self,
        skill_score,
        experience_score,
        education_score,
        semantic_score,
    ):
        """
        Calculate final ATS score.

        All input scores should be between 0.0 and 1.0.
        """

        # Handle missing values
        skill_score = skill_score or 0.0
        experience_score = experience_score or 0.0
        education_score = education_score or 0.0
        semantic_score = semantic_score or 0.0

        # Calculate weighted score
        final_score = (
            skill_score * self.weights["skill"]
            + experience_score * self.weights["experience"]
            + education_score * self.weights["education"]
            + semantic_score * self.weights["semantic"]
        )

        # Convert to percentage
        final_score = round(final_score * 100, 2)

        return final_score

    def get_score_level(self, score):
        """
        Convert ATS score into a readable level.
        """

        if score >= 80:
            return "Excellent"

        elif score >= 70:
            return "Good"

        elif score >= 50:
            return "Average"

        else:
            return "Poor"

    def generate_report(
        self,
        skill_score,
        experience_score,
        education_score,
        semantic_score,
    ):
        """
        Generate explainable ATS scoring report.
        """

        final_score = self.calculate_score(
            skill_score,
            experience_score,
            education_score,
            semantic_score,
        )

        level = self.get_score_level(final_score)

        return {
            "role": self.role,
            "skill_score": round(skill_score * 100, 2),
            "experience_score": round(experience_score * 100, 2),
            "education_score": round(education_score * 100, 2),
            "semantic_score": round(semantic_score * 100, 2),
            "final_ats_score": final_score,
            "level": level,
            "weights": self.weights,
        }


if __name__ == "__main__":

    scorer = ATSScorer("Machine Learning Engineer")

    report = scorer.generate_report(
        skill_score=0.80,
        experience_score=0.70,
        education_score=1.00,
        semantic_score=0.65,
    )

    print("\n========== ATS Score ==========\n")

    print("Role:", report["role"])
    print("Skill Score:", report["skill_score"])
    print("Experience Score:", report["experience_score"])
    print("Education Score:", report["education_score"])
    print("Semantic Score:", report["semantic_score"])

    print("\nWeights:")
    print(report["weights"])

    print("\nFinal ATS Score:", report["final_ats_score"], "/ 100")
    print("Level:", report["level"])

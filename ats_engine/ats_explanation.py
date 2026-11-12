class ATSExplanation:

    def generate(
        self,
        skill_result,
        experience_result,
        education_result,
        semantic_score,
    ):
        """
        Generate an explainable ATS analysis.
        """

        strengths = []
        improvements = []

        # --------------------------------
        # Skill Analysis
        # --------------------------------

        skill_score = skill_result.get("overall_score", skill_result.get("score", 0.0))

        matched_skills = skill_result.get("matched_skills", [])

        missing_skills = skill_result.get("missing_skills", [])

        if skill_score >= 0.75:
            strengths.append("Strong skill match")

        elif skill_score >= 0.50:
            strengths.append("Moderate skill match")

        else:
            improvements.append("Improve alignment with required skills")

        # --------------------------------
        # Experience Analysis
        # --------------------------------

        experience_score = experience_result.get("score", 0.0)

        if experience_score >= 0.75:
            strengths.append("Strong experience match")

        elif experience_score >= 0.50:
            strengths.append("Moderate experience match")

        else:
            improvements.append("Experience does not strongly match the JD")

        # --------------------------------
        # Education Analysis
        # --------------------------------

        education_score = education_result.get("score", 0.0)

        if education_score >= 0.75:
            strengths.append("Strong education match")

        elif education_score >= 0.50:
            strengths.append("Moderate education match")

        else:
            improvements.append("Education has low similarity to the requirement")

        # --------------------------------
        # Semantic Analysis
        # --------------------------------

        semantic_score = max(0.0, min(1.0, semantic_score))

        if semantic_score >= 0.75:
            strengths.append("Strong semantic similarity with the JD")

        elif semantic_score >= 0.50:
            strengths.append("Moderate semantic similarity with the JD")

        else:
            improvements.append(
                "Resume content has low semantic similarity with the JD"
            )

        # --------------------------------
        # Missing Skills
        # --------------------------------

        if missing_skills:

            improvements.append("Missing skills: " + ", ".join(missing_skills))

        return {
            "strengths": strengths,
            "areas_to_improve": improvements,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        }

from parsers.skill_matcher import SkillMatcher
from parsers.experience_matcher import ExperienceMatcher
from parsers.project_matcher import ProjectMatcher
from parsers.similarity_scorer import SimilarityScorer


class SemanticMatchingEngine:

    def __init__(self):

        self.skill_matcher = SkillMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.project_matcher = ProjectMatcher()
        self.semantic_scorer = SimilarityScorer()

    def match(
        self,
        resume_skills,
        jd_skills,
        resume_experience,
        jd_experience,
        resume_projects,
        jd_projects,
        resume_education="",
        jd_education="",
        jd_role="",
    ):

        # --------------------------------
        # Skill Matching
        # --------------------------------

        skill_result = self.skill_matcher.compare_skills(
            resume_skills,
            jd_skills,
        )

        # --------------------------------
        # Experience Matching
        # --------------------------------

        experience_result = self.experience_matcher.compare_experience(
            resume_experience,
            jd_experience,
        )

        # --------------------------------
        # Project Matching
        # --------------------------------

        project_result = self.project_matcher.compare_projects(
            resume_projects,
            jd_projects,
        )

        # --------------------------------
        # Individual scores
        # --------------------------------

        skill_score = skill_result.get(
            "overall_score",
            skill_result.get("score", 0.0),
        )

        experience_score = experience_result.get(
            "score",
            0.0,
        )

        project_score = project_result.get(
            "score",
            0.0,
        )

        # Keep scores between 0 and 1
        skill_score = max(0.0, min(1.0, skill_score))
        experience_score = max(0.0, min(1.0, experience_score))
        project_score = max(0.0, min(1.0, project_score))

        # --------------------------------
        # Build Resume Semantic Text
        # --------------------------------

        resume_text = " ".join(
            [
                str(resume_skills or ""),
                str(resume_experience or ""),
                str(resume_education or ""),
                str(resume_projects or ""),
            ]
        ).strip()

        # --------------------------------
        # Build JD Semantic Text
        # --------------------------------

        jd_text = " ".join(
            [
                str(jd_role or ""),
                str(jd_skills or ""),
                str(jd_experience or ""),
                str(jd_education or ""),
                str(jd_projects or ""),
            ]
        ).strip()

        # --------------------------------
        # Semantic Similarity
        # --------------------------------

        if resume_text and jd_text:

            semantic_score = self.semantic_scorer.calculate_similarity(
                resume_text,
                jd_text,
            )

            semantic_score = max(
                0.0,
                min(1.0, semantic_score),
            )

        else:

            semantic_score = 0.0

        # --------------------------------
        # Day 12 Overall Similarity
        # --------------------------------
        #
        # Keep this for Day 12 compatibility.
        # --------------------------------

        overall_score = round(
            (skill_score * 0.4 + experience_score * 0.4 + project_score * 0.2),
            2,
        )

        if overall_score >= 0.70:

            overall_match = "Excellent"

        elif overall_score >= 0.50:

            overall_match = "Good"

        else:

            overall_match = "Poor"

        return {
            "skill_similarity": skill_result,
            "experience_similarity": experience_result,
            "project_similarity": project_result,
            "semantic_similarity": {
                "score": semantic_score,
                "match": (
                    "High"
                    if semantic_score >= 0.75
                    else "Medium" if semantic_score >= 0.50 else "Low"
                ),
            },
            "overall_similarity": {
                "score": overall_score,
                "match": overall_match,
            },
        }

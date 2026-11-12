from parsers.semantic_matching_engine import SemanticMatchingEngine
from parsers.education_matcher import EducationMatcher

from ats_engine.ats_score import ATSScorer
from ats_engine.ranking_engine import CandidateRankingEngine


class ATSService:
    """
    Integration service for the ATS system.

    Connects:
        Semantic Matching
        Education Matching
        ATS Scoring
        Candidate Ranking
        Shortlisting
    """

    def __init__(self):
        self.matcher = SemanticMatchingEngine()
        self.education_matcher = EducationMatcher()
        self.ranking_engine = CandidateRankingEngine()

    # --------------------------------------------------
    # Calculate ATS score
    # --------------------------------------------------

    def calculate_score(self, resume, jd):

        semantic_result = self.matcher.match(
            resume.get("skills", []),
            jd.get("skills", []),
            resume.get("experience", ""),
            jd.get("experience", ""),
            resume.get("projects", []),
            jd.get("projects", []),
            resume.get("education", ""),
            jd.get("education", ""),
            jd.get("role", ""),
        )

        # Skill score
        skill_score = semantic_result["skill_similarity"].get(
            "overall_score",
            semantic_result["skill_similarity"].get("score", 0.0),
        )

        skill_score = max(0.0, min(1.0, skill_score))

        # Experience score
        experience_score = semantic_result["experience_similarity"].get(
            "score",
            0.0,
        )

        experience_score = max(
            0.0,
            min(1.0, experience_score),
        )

        # Semantic score
        semantic_score = semantic_result["semantic_similarity"].get(
            "score",
            0.0,
        )

        semantic_score = max(
            0.0,
            min(1.0, semantic_score),
        )

        # Education score
        education_result = self.education_matcher.compare_education(
            resume.get("education", ""),
            jd.get("education", ""),
        )

        education_score = education_result.get(
            "score",
            0.0,
        )

        education_score = max(
            0.0,
            min(1.0, education_score),
        )

        # ATS scoring
        scorer = ATSScorer(jd.get("role", "Unknown Role"))

        report = scorer.generate_report(
            skill_score=skill_score,
            experience_score=experience_score,
            education_score=education_score,
            semantic_score=semantic_score,
        )

        return report

    # --------------------------------------------------
    # Rank candidates
    # --------------------------------------------------

    def rank_candidates(self, candidates):

        return self.ranking_engine.rank_candidates(candidates)

    # --------------------------------------------------
    # Shortlist candidates
    # --------------------------------------------------

    def shortlist_candidates(self, ranked_candidates):

        shortlisted = []
        review = []
        rejected = []

        for candidate in ranked_candidates:

            score = candidate["ats_score"]

            if score >= 40:
                candidate["status"] = "SHORTLIST"
                shortlisted.append(candidate)

            elif score >= 25:
                candidate["status"] = "REVIEW"
                review.append(candidate)

            else:
                candidate["status"] = "REJECT"
                rejected.append(candidate)

        return {
            "shortlisted": shortlisted,
            "review": review,
            "rejected": rejected,
        }

    # --------------------------------------------------
    # Complete ranking + shortlisting
    # --------------------------------------------------

    def process_candidates(
        self,
        candidates,
        jd,
    ):

        scored_candidates = []

        for candidate in candidates:

            report = self.calculate_score(
                candidate["resume"],
                jd,
            )

            scored_candidates.append(
                {
                    "resume_id": candidate["resume_id"],
                    "ats_score": report["final_ats_score"],
                    "level": report["level"],
                }
            )

        ranked = self.rank_candidates(scored_candidates)

        result = self.shortlist_candidates(ranked)

        return result

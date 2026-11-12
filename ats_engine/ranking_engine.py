# ats_engine/ranking_engine.py

from ats_engine.shortlisting import ShortlistingEngine


class CandidateRankingEngine:

    def __init__(self):

        self.shortlisting_engine = ShortlistingEngine()

    def rank_candidates(self, candidates):
        """
        Sort candidates from highest ATS score
        to lowest ATS score and assign ranks.
        """

        if not candidates:
            return []

        # --------------------------------
        # Sort by ATS score
        # --------------------------------

        sorted_candidates = sorted(
            candidates,
            key=lambda candidate: float(candidate.get("ats_score", 0.0)),
            reverse=True,
        )

        # --------------------------------
        # Add rank
        # --------------------------------

        ranked_candidates = []

        for index, candidate in enumerate(
            sorted_candidates,
            start=1,
        ):

            result = candidate.copy()

            result["rank"] = index

            ranked_candidates.append(result)

        # --------------------------------
        # Add candidate status
        # --------------------------------

        ranked_candidates = self.shortlisting_engine.process_candidates(
            ranked_candidates
        )

        return ranked_candidates

    def get_top_candidates(
        self,
        ranked_candidates,
        top_n=3,
    ):
        """
        Return top N candidates.
        """

        return ranked_candidates[:top_n]

    def generate_summary(self, ranked_candidates):
        """
        Generate recruiter-friendly summary.
        """

        shortlisted = [
            candidate
            for candidate in ranked_candidates
            if candidate["status"] == "SHORTLIST"
        ]

        review = [
            candidate
            for candidate in ranked_candidates
            if candidate["status"] == "REVIEW"
        ]

        rejected = [
            candidate
            for candidate in ranked_candidates
            if candidate["status"] == "REJECT"
        ]

        return {
            "total_candidates": len(ranked_candidates),
            "shortlisted": len(shortlisted),
            "review": len(review),
            "rejected": len(rejected),
            "top_candidate": (ranked_candidates[0] if ranked_candidates else None),
        }

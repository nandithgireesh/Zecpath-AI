# ats_engine/shortlisting.py

from ats_engine.thresholds import get_candidate_status


class ShortlistingEngine:

    def __init__(self):
        pass

    def classify_candidate(self, score):
        """
        Classify a candidate based on ATS score.
        """

        status = get_candidate_status(score)

        return status

    def process_candidates(self, candidates):
        """
        Add status to every candidate.
        """

        processed = []

        for candidate in candidates:

            score = float(candidate.get("ats_score", 0.0))

            status = self.classify_candidate(score)

            candidate_result = candidate.copy()

            candidate_result["status"] = status

            processed.append(candidate_result)

        return processed

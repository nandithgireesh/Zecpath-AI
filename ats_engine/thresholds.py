# ats_engine/thresholds.py


# ----------------------------------------
# Candidate Shortlisting Thresholds
# ----------------------------------------

SHORTLIST_THRESHOLD = 40.0
REVIEW_THRESHOLD = 25.0


def get_candidate_status(score):
    """
    Determine candidate status based on ATS score.
    """

    score = float(score)

    if score >= SHORTLIST_THRESHOLD:
        return "SHORTLIST"

    elif score >= REVIEW_THRESHOLD:
        return "REVIEW"

    else:
        return "REJECT"

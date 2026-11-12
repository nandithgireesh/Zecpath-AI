import os
import sys
import json

# ----------------------------------------
# Add project root to Python path
# ----------------------------------------

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from parsers.semantic_matching_engine import SemanticMatchingEngine

from parsers.education_matcher import EducationMatcher

from ats_engine.ats_score import ATSScorer

from ats_engine.ranking_engine import CandidateRankingEngine


def calculate_ats_score(
    matcher,
    education_matcher,
    resume,
    jd,
):
    """
    Calculate ATS score for one Resume ↔ JD pair.
    """

    # --------------------------------
    # Semantic matching
    # --------------------------------

    semantic_result = matcher.match(
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

    # --------------------------------
    # Skill score
    # --------------------------------

    skill_score = semantic_result["skill_similarity"].get(
        "overall_score",
        semantic_result["skill_similarity"].get("score", 0.0),
    )

    skill_score = max(
        0.0,
        min(1.0, skill_score),
    )

    # --------------------------------
    # Experience score
    # --------------------------------

    experience_score = semantic_result["experience_similarity"].get(
        "score",
        0.0,
    )

    experience_score = max(
        0.0,
        min(1.0, experience_score),
    )

    # --------------------------------
    # Semantic score
    # --------------------------------

    semantic_score = semantic_result["semantic_similarity"].get(
        "score",
        0.0,
    )

    semantic_score = max(
        0.0,
        min(1.0, semantic_score),
    )

    # --------------------------------
    # Education
    # --------------------------------

    education_result = education_matcher.compare_education(
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

    # --------------------------------
    # ATS scoring
    # --------------------------------

    role = jd.get(
        "role",
        "Unknown Role",
    )

    scorer = ATSScorer(role)

    report = scorer.generate_report(
        skill_score=skill_score,
        experience_score=experience_score,
        education_score=education_score,
        semantic_score=semantic_score,
    )

    return report


def main():

    resume_folder = "data/parsed_profiles"
    jd_folder = "data/jd_output"

    # --------------------------------
    # Initialize engines
    # --------------------------------

    matcher = SemanticMatchingEngine()

    education_matcher = EducationMatcher()

    ranking_engine = CandidateRankingEngine()

    # --------------------------------
    # Load files
    # --------------------------------

    resume_files = sorted(
        [file for file in os.listdir(resume_folder) if file.endswith(".json")]
    )

    jd_files = sorted(
        [file for file in os.listdir(jd_folder) if file.endswith(".json")]
    )

    print()
    print("========== DAY 14 ==========")
    print("Candidate Ranking & Shortlisting")
    print("=============================")
    print()

    final_report = []

    # --------------------------------
    # Process each JD
    # --------------------------------

    for jd_file in jd_files:

        jd_path = os.path.join(
            jd_folder,
            jd_file,
        )

        with open(
            jd_path,
            "r",
            encoding="utf-8",
        ) as file:

            jd = json.load(file)

        role = jd.get(
            "role",
            "Unknown Role",
        )

        candidates = []

        # --------------------------------
        # Score every resume
        # --------------------------------

        for resume_file in resume_files:

            resume_path = os.path.join(
                resume_folder,
                resume_file,
            )

            with open(
                resume_path,
                "r",
                encoding="utf-8",
            ) as file:

                resume = json.load(file)

            report = calculate_ats_score(
                matcher,
                education_matcher,
                resume,
                jd,
            )

            candidates.append(
                {
                    "resume": resume_file,
                    "ats_score": report["final_ats_score"],
                    "level": report["level"],
                }
            )

        # --------------------------------
        # Rank candidates
        # --------------------------------

        ranked_candidates = ranking_engine.rank_candidates(candidates)

        # --------------------------------
        # Top candidates
        # --------------------------------

        top_candidates = ranking_engine.get_top_candidates(
            ranked_candidates,
            top_n=3,
        )

        # --------------------------------
        # Summary
        # --------------------------------

        summary = ranking_engine.generate_summary(ranked_candidates)

        # --------------------------------
        # Display
        # --------------------------------

        print("=" * 75)

        print(f"JD     : {jd_file}")

        print(f"Role   : {role}")

        print("=" * 75)

        print(
            f"{'Rank':<8}" f"{'Resume':<22}" f"{'Score':<12}" f"{'Level':<12}" f"Status"
        )

        print("-" * 75)

        for candidate in ranked_candidates:

            print(
                f"{candidate['rank']:<8}"
                f"{candidate['resume']:<22}"
                f"{candidate['ats_score']:<12}"
                f"{candidate['level']:<12}"
                f"{candidate['status']}"
            )

        print("-" * 75)

        print(f"Shortlisted : " f"{summary['shortlisted']}")

        print(f"Review      : " f"{summary['review']}")

        print(f"Rejected    : " f"{summary['rejected']}")

        if top_candidates:

            print()
            print("TOP CANDIDATES")

            for candidate in top_candidates:

                print(
                    f"{candidate['rank']}. "
                    f"{candidate['resume']} "
                    f"→ "
                    f"{candidate['ats_score']} "
                    f"({candidate['status']})"
                )

        # --------------------------------
        # Save report data
        # --------------------------------

        final_report.append(
            {
                "jd": jd_file,
                "role": role,
                "ranked_candidates": ranked_candidates,
                "summary": summary,
            }
        )

        print()

    # --------------------------------
    # Save JSON report
    # --------------------------------

    output_folder = "data/ats_output"

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    output_path = os.path.join(
        output_folder,
        "day14_candidate_ranking.json",
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_report,
            file,
            indent=4,
        )

    print("=" * 75)

    print("DAY 14 COMPLETED SUCCESSFULLY")

    print(f"Report Saved : {output_path}")

    print("=" * 75)


if __name__ == "__main__":
    main()

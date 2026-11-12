import os
import sys
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.semantic_matching_engine import SemanticMatchingEngine
from parsers.education_matcher import EducationMatcher
from ats_engine.ats_score import ATSScorer
from ats_engine.ats_explanation import ATSExplanation


def main():

    # --------------------------------
    # Initialize components
    # --------------------------------

    matcher = SemanticMatchingEngine()
    education_matcher = EducationMatcher()
    explainer = ATSExplanation()

    resume_folder = "data/parsed_profiles"
    jd_folder = "data/jd_output"
    output_folder = "data/ats_output"

    os.makedirs(output_folder, exist_ok=True)

    resume_files = sorted([f for f in os.listdir(resume_folder) if f.endswith(".json")])

    jd_files = sorted([f for f in os.listdir(jd_folder) if f.endswith(".json")])

    all_results = []

    print()
    print("=" * 80)
    print("                 ATS CANDIDATE RANKING")
    print("=" * 80)
    print()

    # ================================================
    # Process each JD
    # ================================================

    for jd_file in jd_files:

        jd_path = os.path.join(jd_folder, jd_file)

        with open(jd_path, "r", encoding="utf-8") as file:

            jd = json.load(file)

        role = jd.get("role", "Unknown Role")

        jd_results = []

        # ============================================
        # Compare all resumes with current JD
        # ============================================

        for resume_file in resume_files:

            resume_path = os.path.join(resume_folder, resume_file)

            with open(resume_path, "r", encoding="utf-8") as file:

                resume = json.load(file)

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
                role,
            )

            # --------------------------------
            # Skill score
            # --------------------------------

            skill_score = semantic_result["skill_similarity"].get(
                "overall_score", semantic_result["skill_similarity"].get("score", 0.0)
            )

            skill_score = max(0.0, min(1.0, skill_score))

            # --------------------------------
            # Experience score
            # --------------------------------

            experience_score = semantic_result["experience_similarity"].get(
                "score", 0.0
            )

            experience_score = max(0.0, min(1.0, experience_score))

            # --------------------------------
            # Semantic score
            # --------------------------------

            semantic_score = semantic_result["semantic_similarity"].get("score", 0.0)

            semantic_score = max(0.0, min(1.0, semantic_score))

            # --------------------------------
            # Education score
            # --------------------------------

            education_result = education_matcher.compare_education(
                resume.get("education", ""),
                jd.get("education", ""),
            )

            education_score = education_result.get("score", 0.0)

            education_score = max(0.0, min(1.0, education_score))

            # --------------------------------
            # ATS scoring
            # --------------------------------

            scorer = ATSScorer(role)

            report = scorer.generate_report(
                skill_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
                semantic_score=semantic_score,
            )

            # --------------------------------
            # Explanation
            # --------------------------------

            explanation = explainer.generate(
                skill_result=semantic_result["skill_similarity"],
                experience_result=semantic_result["experience_similarity"],
                education_result=education_result,
                semantic_score=semantic_score,
            )

            # --------------------------------
            # Store candidate result
            # --------------------------------

            result = {
                "resume": resume_file,
                "jd": jd_file,
                "role": role,
                "skill_score": report["skill_score"],
                "experience_score": report["experience_score"],
                "education_score": report["education_score"],
                "semantic_score": report["semantic_score"],
                "final_ats_score": report["final_ats_score"],
                "level": report["level"],
                "education_match": (education_result.get("match", "No Data")),
                "strengths": explanation["strengths"],
                "areas_to_improve": (explanation["areas_to_improve"]),
            }

            jd_results.append(result)

        # ============================================
        # Rank candidates
        # ============================================

        jd_results.sort(key=lambda x: x["final_ats_score"], reverse=True)

        # Add ranking
        for index, result in enumerate(jd_results, start=1):

            result["rank"] = index

        # ============================================
        # Find top candidate
        # ============================================

        top_candidate = jd_results[0]

        # ============================================
        # Store JD results
        # ============================================

        all_results.append(
            {
                "jd": jd_file,
                "role": role,
                "top_candidate": {
                    "resume": top_candidate["resume"],
                    "score": top_candidate["final_ats_score"],
                    "level": top_candidate["level"],
                },
                "candidates": jd_results,
            }
        )

        # ============================================
        # Display ranking
        # ============================================

        print("=" * 80)

        print(f"JD   : {jd_file}")

        print(f"ROLE : {role}")

        print("-" * 80)

        print(f"{'Rank':<8}" f"{'Resume':<22}" f"{'ATS Score':<15}" f"{'Level'}")

        print("-" * 80)

        for result in jd_results:

            print(
                f"{result['rank']:<8}"
                f"{result['resume']:<22}"
                f"{result['final_ats_score']:<15}"
                f"{result['level']}"
            )

        print()

        print(f"TOP CANDIDATE : " f"{top_candidate['resume']}")

        print(f"TOP ATS SCORE : " f"{top_candidate['final_ats_score']} / 100")

        print()

    # ================================================
    # Final Summary
    # ================================================

    print()
    print("=" * 80)
    print("                    FINAL SUMMARY")
    print("=" * 80)

    print()

    print(f"{'JD':<12}" f"{'Role':<35}" f"{'Best Resume':<20}" f"{'Score'}")

    print("-" * 80)

    for result in all_results:

        print(
            f"{result['jd']:<12}"
            f"{result['role'][:33]:<35}"
            f"{result['top_candidate']['resume']:<20}"
            f"{result['top_candidate']['score']}"
        )

    print()

    # ================================================
    # Save JSON report
    # ================================================

    output_path = os.path.join(output_folder, "ats_ranking_report.json")

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(all_results, file, indent=4)

    print("=" * 80)

    print("ATS RANKING COMPLETED SUCCESSFULLY")

    print(f"Report Saved : {output_path}")

    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

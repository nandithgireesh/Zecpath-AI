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

    resume_files = sorted([f for f in os.listdir(resume_folder) if f.endswith(".json")])

    jd_files = sorted([f for f in os.listdir(jd_folder) if f.endswith(".json")])

    print("\n========== Real Resume ↔ JD ATS Scoring ==========\n")

    # --------------------------------
    # Compare every Resume with
    # every JD
    # --------------------------------

    for resume_file in resume_files:

        resume_path = os.path.join(resume_folder, resume_file)

        with open(resume_path, "r", encoding="utf-8") as file:

            resume = json.load(file)

        for jd_file in jd_files:

            jd_path = os.path.join(jd_folder, jd_file)

            with open(jd_path, "r", encoding="utf-8") as file:

                jd = json.load(file)

            # --------------------------------
            # Day 12 Semantic Matching
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
            # Skill Score
            # --------------------------------

            skill_score = semantic_result["skill_similarity"].get(
                "overall_score", semantic_result["skill_similarity"].get("score", 0.0)
            )

            skill_score = max(0.0, min(1.0, skill_score))

            # --------------------------------
            # Experience Score
            # --------------------------------

            experience_score = semantic_result["experience_similarity"].get(
                "score", 0.0
            )

            experience_score = max(0.0, min(1.0, experience_score))

            # --------------------------------
            # Semantic Score
            # --------------------------------

            semantic_score = semantic_result["semantic_similarity"].get("score", 0.0)

            semantic_score = max(0.0, min(1.0, semantic_score))

            # --------------------------------
            # Education Matching
            # --------------------------------

            resume_education = resume.get("education", "")

            jd_education = jd.get("education", "")

            education_result = education_matcher.compare_education(
                resume_education,
                jd_education,
            )

            education_score = education_result.get("score", 0.0)

            education_score = max(0.0, min(1.0, education_score))

            # --------------------------------
            # Detect JD Role
            # --------------------------------

            role = jd.get("role", "Unknown Role")

            # --------------------------------
            # Day 13 ATS Scoring
            # --------------------------------

            scorer = ATSScorer(role)

            report = scorer.generate_report(
                skill_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
                semantic_score=semantic_score,
            )

            # --------------------------------
            # Generate Explanation
            # --------------------------------

            explanation = explainer.generate(
                skill_result=semantic_result["skill_similarity"],
                experience_result=semantic_result["experience_similarity"],
                education_result=education_result,
                semantic_score=semantic_score,
            )

            # --------------------------------
            # Display Result
            # --------------------------------

            print("=" * 70)

            print(f"Resume : {resume_file}")

            print(f"JD     : {jd_file}")

            print(f"Role   : {role}")

            print("-" * 70)

            print(f"Skill Score       : " f"{report['skill_score']}%")

            print(f"Experience Score  : " f"{report['experience_score']}%")

            print(f"Education Score   : " f"{report['education_score']}%")

            print(f"Semantic Score    : " f"{report['semantic_score']}%")

            print(f"Education Match   : " f"{education_result.get('match', 'No Data')}")

            print("-" * 70)

            print(f"FINAL ATS SCORE   : " f"{report['final_ats_score']} / 100")

            print(f"LEVEL             : " f"{report['level']}")

            # --------------------------------
            # Explainable ATS Analysis
            # --------------------------------

            print("-" * 70)

            print("STRENGTHS:")

            if explanation["strengths"]:

                for strength in explanation["strengths"]:

                    print(f"  ✓ {strength}")

            else:

                print("  None identified")

            print()

            print("AREAS TO IMPROVE:")

            if explanation["areas_to_improve"]:

                for improvement in explanation["areas_to_improve"]:

                    print(f"  ✗ {improvement}")

            else:

                print("  None identified")

            print()


if __name__ == "__main__":
    main()

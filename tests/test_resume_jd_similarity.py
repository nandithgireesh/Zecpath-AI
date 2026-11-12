import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parsers.semantic_matching_engine import SemanticMatchingEngine


def main():

    matcher = SemanticMatchingEngine()

    resume_folder = "data/parsed_profiles"
    jd_folder = "data/jd_output"

    resume_files = sorted([f for f in os.listdir(resume_folder) if f.endswith(".json")])

    jd_files = sorted([f for f in os.listdir(jd_folder) if f.endswith(".json")])

    # Store all comparison results
    results = []

    print("\n========== Resume ↔ JD Similarity ==========\n")

    for resume_file in resume_files:

        with open(
            os.path.join(resume_folder, resume_file),
            "r",
            encoding="utf-8",
        ) as f:

            resume = json.load(f)

        for jd_file in jd_files:

            with open(
                os.path.join(jd_folder, jd_file),
                "r",
                encoding="utf-8",
            ) as f:

                jd = json.load(f)

            result = matcher.match(
                resume.get("skills", []),
                jd.get("skills", []),
                resume.get("experience", ""),
                jd.get("experience", ""),
                resume.get("projects", []),
                "",
            )

            print("=" * 70)
            print(f"Resume : {resume_file}")
            print(f"JD      : {jd_file}")
            print("=" * 70)
            print(result)
            print()

            # Save comparison result
            results.append(
                {
                    "resume": resume_file,
                    "jd": jd_file,
                    "score": result["overall_similarity"]["score"],
                    "match": result["overall_similarity"]["match"],
                }
            )

    # ===========================
    # Matching Accuracy Report
    # ===========================

    print("\n========== Matching Accuracy Report ==========\n")

    total_resumes = len(resume_files)
    total_jds = len(jd_files)
    total_comparisons = len(results)

    average_score = round(
        sum(r["score"] for r in results) / total_comparisons,
        2,
    )

    highest = max(results, key=lambda x: x["score"])
    lowest = min(results, key=lambda x: x["score"])

    print(f"Total Resumes Tested : {total_resumes}")
    print(f"Total JDs Tested     : {total_jds}")
    print(f"Total Comparisons    : {total_comparisons}")

    print("\nHighest Match")
    print("----------------------------")
    print(f"Resume : {highest['resume']}")
    print(f"JD     : {highest['jd']}")
    print(f"Score  : {highest['score']}")

    print("\nLowest Match")
    print("----------------------------")
    print(f"Resume : {lowest['resume']}")
    print(f"JD     : {lowest['jd']}")
    print(f"Score  : {lowest['score']}")

    print(f"\nAverage Similarity : {average_score}")

    # ===========================
    # Save Report
    # ===========================

    report = {
        "total_resumes": total_resumes,
        "total_jds": total_jds,
        "total_comparisons": total_comparisons,
        "average_similarity": average_score,
        "highest_match": highest,
        "lowest_match": lowest,
        "all_results": results,
    }

    output_dir = "data/matching_report"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        "matching_accuracy_report.json",
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"\n✔ Report Saved : {output_path}")


if __name__ == "__main__":
    main()

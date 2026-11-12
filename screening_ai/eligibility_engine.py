import os
import sys
import re
import json
from typing import Dict, List, Any, Optional, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screening_ai.eligibility_config import (
    EligibilityRuleConfig,
    get_rule_config_for_role,
)
from data.skills.skill_dictionary import SKILL_SYNONYMS, SKILL_STACKS
from utils.logger import logger


class EligibilityDecisionEngine:
    """
    Day 21 - Eligibility Decision Engine.
    
    Evaluates candidates against recruiter-defined eligibility criteria and ATS
    scores to decide whether they are ready for automated AI screening calls.
    """

    def __init__(self, default_rule_config: Optional[EligibilityRuleConfig] = None):
        self.default_rule_config = default_rule_config or EligibilityRuleConfig()
        self.skill_synonyms = SKILL_SYNONYMS
        self.skill_stacks = SKILL_STACKS
        logger.info("EligibilityDecisionEngine initialized.")

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill string for exact & synonym comparison."""
        if not skill:
            return ""
        s = skill.lower().strip()
        s = s.replace("-", " ").replace(".", " ")
        s = " ".join(s.split())
        return self.skill_synonyms.get(s, s)

    def extract_experience_years(self, exp_val: Any) -> float:
        """Safely parse experience into numeric float years."""
        if exp_val is None:
            return 0.0
        if isinstance(exp_val, (int, float)):
            # If accidentally passed a calendar year like 2023
            if exp_val > 1900:
                return 0.0
            return float(exp_val)
        
        # If passed a list of experience entries
        if isinstance(exp_val, list):
            total = 0.0
            for item in exp_val:
                if isinstance(item, dict):
                    dur = item.get("duration") or item.get("years") or item.get("duration_months")
                    if dur:
                        total += self.extract_experience_years(dur)
                else:
                    total += self.extract_experience_years(item)
            return round(total, 2)

        text = str(exp_val).lower().strip()
        text = text.replace("–", "-").replace("—", "-")

        # Check for year ranges like "2020 - 2023" or "2019 - Present"
        range_match = re.findall(r"(20\d\d|19\d\d)\s*(?:-|to)\s*(20\d\d|present|current)", text)
        if range_match:
            total_range_years = 0.0
            for start_yr, end_yr in range_match:
                start_val = float(start_yr)
                end_val = 2026.0 if end_yr in ["present", "current"] else float(end_yr)
                diff = max(0.0, end_val - start_val)
                total_range_years += diff
            if total_range_years > 0:
                return min(30.0, round(total_range_years, 2))

        # Look for explicit pattern like "3.5 years" or "2 yrs"
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+|-\s*\d+)?\s*(?:year|yr|y)", text)
        if match:
            val = float(match.group(1))
            if val < 50:  # sanity check against year like 2023
                return val

        # Look for months like "18 months"
        month_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:month|mo|m)", text)
        if month_match:
            m_val = float(month_match.group(1))
            return round(m_val / 12.0, 2)
        
        # Fallback standalone small number
        num_match = re.search(r"\b(\d+(?:\.\d+)?)\b", text)
        if num_match:
            val = float(num_match.group(1))
            if val < 40 and val != 20:  # avoid 20xx / calendar year noise
                return val
        
        return 0.0

    def check_mandatory_skills(
        self, candidate_skills: List[str], mandatory_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Verify if candidate has all mandatory skills, resolving synonyms and stacks.
        """
        if not mandatory_skills:
            return {
                "passed": True,
                "missing_skills": [],
                "matched_skills": list(candidate_skills),
                "match_rate": 1.0,
            }

        normalized_candidate_skills = {
            self.normalize_skill(s) for s in candidate_skills if s
        }

        # Expand stacks in candidate skills (e.g. MERN -> React, Node.js, MongoDB)
        expanded_candidate_skills = set(normalized_candidate_skills)
        for s in candidate_skills:
            lower_s = s.lower().strip()
            if lower_s in self.skill_stacks:
                for sub_skill in self.skill_stacks[lower_s]:
                    expanded_candidate_skills.add(self.normalize_skill(sub_skill))

        missing = []
        matched = []

        for req in mandatory_skills:
            norm_req = self.normalize_skill(req)
            if norm_req in expanded_candidate_skills:
                matched.append(req)
            else:
                # Check substring match
                found = False
                for c_skill in expanded_candidate_skills:
                    if norm_req in c_skill or c_skill in norm_req:
                        matched.append(req)
                        found = True
                        break
                if not found:
                    missing.append(req)

        match_rate = len(matched) / len(mandatory_skills) if mandatory_skills else 1.0
        passed = len(missing) == 0

        return {
            "passed": passed,
            "missing_skills": missing,
            "matched_skills": matched,
            "match_rate": round(match_rate, 2),
        }

    def evaluate_candidate(
        self,
        candidate_data: Dict[str, Any],
        rule_config: Optional[Union[EligibilityRuleConfig, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a single candidate against rule configurations.
        
        Returns a structured dictionary with:
        - status: ELIGIBLE | REVIEW | REJECTED
        - call_priority: HIGH | MEDIUM | LOW | NONE
        - reason: explainable verdict breakdown
        """
        # Resolve rule config
        if rule_config is None:
            config = self.default_rule_config
        elif isinstance(rule_config, dict):
            config = EligibilityRuleConfig.from_dict(rule_config)
        else:
            config = rule_config

        candidate_id = (
            candidate_data.get("candidate_id")
            or candidate_data.get("resume_id")
            or candidate_data.get("name")
            or "Unknown Candidate"
        )
        
        ats_score = float(candidate_data.get("ats_score", 0.0))
        skills = candidate_data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]

        # 1. Mandatory Skills Check
        skill_res = self.check_mandatory_skills(skills, config.mandatory_skills)
        missing_skills = skill_res["missing_skills"]

        # 2. Experience Range Check
        exp_years = self.extract_experience_years(
            candidate_data.get("total_experience")
            or candidate_data.get("experience_years")
            or candidate_data.get("experience")
        )
        
        exp_passed = True
        exp_reason = []
        if exp_years < config.min_experience_years:
            exp_passed = False
            exp_reason.append(
                f"Experience ({exp_years} yrs) below minimum required ({config.min_experience_years} yrs)"
            )
        if config.max_experience_years and exp_years > config.max_experience_years:
            # Overqualification might be a review point rather than immediate hard rejection
            exp_reason.append(
                f"Experience ({exp_years} yrs) exceeds target range maximum ({config.max_experience_years} yrs)"
            )

        # 3. Location & Remote Check
        candidate_loc = str(
            candidate_data.get("location")
            or candidate_data.get("address")
            or ""
        ).strip()
        
        location_passed = True
        if config.allowed_locations and candidate_loc:
            norm_loc = candidate_loc.lower()
            loc_matched = False
            for allowed in config.allowed_locations:
                allowed_norm = allowed.lower()
                if (
                    allowed_norm == "any"
                    or allowed_norm in norm_loc
                    or norm_loc in allowed_norm
                    or (config.allow_remote and "remote" in norm_loc)
                ):
                    loc_matched = True
                    break
            if not loc_matched and not config.allow_remote:
                location_passed = False

        # 4. Notice Period Check
        notice_days = candidate_data.get("notice_period_days")
        notice_passed = True
        if (
            config.max_notice_period_days is not None
            and notice_days is not None
            and int(notice_days) > config.max_notice_period_days
        ):
            notice_passed = False

        # 5. ATS Score Cutoff Check
        ats_eligible = ats_score >= config.min_ats_score
        ats_review = (
            config.review_ats_score <= ats_score < config.min_ats_score
        )

        # ----------------------------------------------------
        # DECISION SYNTHESIS & REASONING
        # ----------------------------------------------------
        reasons = []
        status = "REJECTED"
        call_priority = "NONE"

        checks = {
            "mandatory_skills_passed": skill_res["passed"],
            "experience_range_passed": exp_passed,
            "location_passed": location_passed,
            "notice_period_passed": notice_passed,
            "ats_score_cutoff_met": ats_eligible,
        }

        # Case A: Fully Qualified (ELIGIBLE)
        if ats_eligible and skill_res["passed"] and exp_passed and location_passed and notice_passed:
            status = "ELIGIBLE"
            call_priority = "HIGH" if ats_score >= 80.0 else "MEDIUM"
            reasons.append(
                f"Candidate meets all criteria with strong ATS score of {ats_score:.1f}%."
            )
            if skill_res["matched_skills"]:
                reasons.append(
                    f"Matched mandatory skills: {', '.join(skill_res['matched_skills'])}."
                )

        # Case B: Review Tier
        elif (
            (ats_eligible or ats_review)
            and len(missing_skills) <= 1
            and location_passed
        ):
            status = "REVIEW"
            call_priority = "LOW"
            if ats_review:
                reasons.append(
                    f"Borderline ATS score ({ats_score:.1f}%) within review band [{config.review_ats_score}% - {config.min_ats_score}%]."
                )
            if missing_skills:
                reasons.append(
                    f"Missing single mandatory skill: {', '.join(missing_skills)}."
                )
            if not exp_passed:
                reasons.extend(exp_reason)

        # Case C: Rejected
        else:
            status = "REJECTED"
            call_priority = "NONE"
            if ats_score < config.review_ats_score:
                reasons.append(
                    f"ATS score ({ats_score:.1f}%) below minimum cutoff threshold ({config.review_ats_score}%)."
                )
            if missing_skills:
                reasons.append(
                    f"Missing mandatory skills: {', '.join(missing_skills)}."
                )
            if not exp_passed:
                reasons.extend(exp_reason)
            if not location_passed:
                reasons.append(
                    f"Candidate location '{candidate_loc}' not in allowed locations: {config.allowed_locations}."
                )
            if not notice_passed:
                reasons.append(
                    f"Notice period ({notice_days} days) exceeds maximum allowed ({config.max_notice_period_days} days)."
                )

        return {
            "candidate_id": candidate_id,
            "status": status,
            "call_priority": call_priority,
            "ats_score": round(ats_score, 2),
            "role_evaluated": config.role_name,
            "checks": checks,
            "missing_mandatory_skills": missing_skills,
            "matched_mandatory_skills": skill_res["matched_skills"],
            "experience_years": exp_years,
            "decision_reason": " ".join(reasons),
        }

    def batch_evaluate(
        self,
        candidates: List[Dict[str, Any]],
        rule_config: Optional[Union[EligibilityRuleConfig, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a list/pool of candidates and produce grouped cohorts & analytics.
        """
        if rule_config is None:
            config = self.default_rule_config
        elif isinstance(rule_config, dict):
            config = EligibilityRuleConfig.from_dict(rule_config)
        else:
            config = rule_config

        results = []
        eligible_list = []
        review_list = []
        rejected_list = []

        for cand in candidates:
            eval_res = self.evaluate_candidate(cand, config)
            results.append(eval_res)

            if eval_res["status"] == "ELIGIBLE":
                eligible_list.append(eval_res)
            elif eval_res["status"] == "REVIEW":
                review_list.append(eval_res)
            else:
                rejected_list.append(eval_res)

        # Sort eligible candidates descending by ATS score for priority call queueing
        eligible_list.sort(key=lambda x: x["ats_score"], reverse=True)
        review_list.sort(key=lambda x: x["ats_score"], reverse=True)

        total = len(candidates)
        eligible_count = len(eligible_list)
        review_count = len(review_list)
        rejected_count = len(rejected_list)

        eligibility_rate = (eligible_count / total * 100.0) if total > 0 else 0.0

        summary = {
            "role": config.role_name,
            "total_candidates_evaluated": total,
            "eligible_count": eligible_count,
            "review_count": review_count,
            "rejected_count": rejected_count,
            "eligibility_rate_percentage": round(eligibility_rate, 2),
            "rule_cutoffs_applied": config.to_dict(),
        }

        return {
            "summary": summary,
            "eligible_candidates": eligible_list,
            "review_candidates": review_list,
            "rejected_candidates": rejected_list,
            "all_results": results,
        }

    def save_report(
        self,
        report_data: Dict[str, Any],
        output_path: str = "data/screening_output/eligibility_decision_report.json",
    ) -> str:
        """Persist structured eligibility report to disk."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Eligibility decision report saved to {output_path}")
        return output_path

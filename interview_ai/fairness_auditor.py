"""
Day 43 Deliverable 2: Fairness & Disparate Impact Auditor
=========================================================
Implements algorithmic fairness evaluations conforming to the EEOC Uniform
Guidelines on Employee Selection Procedures (29 CFR § 1607) and NYC Local Law 144:
- 4/5ths Rule (80% Rule) Adverse Impact Ratio (AIR)
- Statistical Parity Difference (SPD)
- Impact Ratio across protected demographic groups (Gender, Age ADEA, Ethnicity/Region)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class GroupMetric:
    group_name: str
    total_evaluated: int
    total_selected: int
    selection_rate: float
    mean_score: float
    score_variance: float


@dataclass
class FairnessAuditReport:
    benchmark_group: str
    protected_group: str
    protected_attribute_category: str  # Gender, Age, Ethnicity/Region
    benchmark_selection_rate: float
    protected_selection_rate: float
    adverse_impact_ratio: float  # AIR = protected_rate / benchmark_rate
    statistical_parity_difference: float  # protected_rate - benchmark_rate
    four_fifths_rule_compliant: bool  # AIR >= 0.80
    disparate_impact_detected: bool
    confidence_level: float = 0.95
    p_value: Optional[float] = None
    compliance_summary: str = ""


class FairnessAuditor:
    """
    Audits HR AI hiring scores across demographic cohorts to detect disparate impact,
    ensure compliance with the 4/5ths rule, and generate empirical bias metrics.
    """

    FOUR_FIFTHS_THRESHOLD = 0.80

    def evaluate_cohort_disparate_impact(
        self,
        category: str,
        benchmark_name: str,
        protected_name: str,
        benchmark_candidates: List[Tuple[float, bool]],  # (score, is_selected)
        protected_candidates: List[Tuple[float, bool]],
    ) -> FairnessAuditReport:
        """
        Calculates selection rates, adverse impact ratio, and statistical parity difference
        between benchmark (privileged) and protected (unprivileged) demographic cohorts.
        """
        b_total = len(benchmark_candidates)
        p_total = len(protected_candidates)

        if b_total == 0 or p_total == 0:
            raise ValueError("Cohort size must be non-zero for statistical audit.")

        b_selected = sum(1 for _, sel in benchmark_candidates if sel)
        p_selected = sum(1 for _, sel in protected_candidates if sel)

        b_rate = b_selected / b_total
        p_rate = p_selected / p_total

        # Adverse Impact Ratio (EEOC 4/5ths Rule)
        if b_rate == 0:
            air = 1.0 if p_rate == 0 else 2.0
        else:
            air = p_rate / b_rate

        spd = p_rate - b_rate
        compliant = air >= self.FOUR_FIFTHS_THRESHOLD
        disparate_impact = not compliant

        # Approximate Two-Proportion Z-Test p-value
        pooled_p = (b_selected + p_selected) / (b_total + p_total)
        if 0 < pooled_p < 1:
            se = math.sqrt(pooled_p * (1 - pooled_p) * (1 / b_total + 1 / p_total))
            z = (p_rate - b_rate) / se if se > 0 else 0
            # Two-tailed p-value approximation via standard error function
            p_val = math.erfc(abs(z) / math.sqrt(2))
        else:
            p_val = 1.0

        if compliant:
            summary = (
                f"PASS: Adverse Impact Ratio is {air:.3f} (>= 0.800 threshold). "
                f"Selection rates ({p_rate * 100:.1f}% vs {b_rate * 100:.1f}%) satisfy the EEOC 4/5ths rule."
            )
        else:
            summary = (
                f"ALERT: Disparate Impact Detected. AIR is {air:.3f} (< 0.800 threshold). "
                f"Protected group selection rate ({p_rate * 100:.1f}%) is statistically lower than benchmark ({b_rate * 100:.1f}%)."
            )

        return FairnessAuditReport(
            benchmark_group=benchmark_name,
            protected_group=protected_name,
            protected_attribute_category=category,
            benchmark_selection_rate=round(b_rate, 4),
            protected_selection_rate=round(p_rate, 4),
            adverse_impact_ratio=round(air, 4),
            statistical_parity_difference=round(spd, 4),
            four_fifths_rule_compliant=compliant,
            disparate_impact_detected=disparate_impact,
            p_value=round(p_val, 4),
            compliance_summary=summary,
        )

    def run_multi_demographic_audit(
        self,
        eval_records: List[Dict],  # [{score: float, selected: bool, gender: str, age_group: str, region: str}]
    ) -> Dict[str, FairnessAuditReport]:
        """
        Executes a comprehensive fairness audit across all three core protected categories:
        1. Gender (Male vs Female / Non-binary)
        2. Age (Under 40 vs 40+ ADEA)
        3. Regional / Linguistic Dialect (Native NA/UK vs Non-Native International)
        """
        results: Dict[str, FairnessAuditReport] = {}

        # 1. Gender Audit
        male_cand = [(r["score"], r["selected"]) for r in eval_records if r.get("gender") == "MALE"]
        fem_cand = [(r["score"], r["selected"]) for r in eval_records if r.get("gender") in ("FEMALE", "NON_BINARY")]
        if male_cand and fem_cand:
            results["GENDER"] = self.evaluate_cohort_disparate_impact(
                category="Gender",
                benchmark_name="Male Applicants",
                protected_name="Female & Non-Binary Applicants",
                benchmark_candidates=male_cand,
                protected_candidates=fem_cand,
            )

        # 2. Age Audit (ADEA 40+ Protections)
        younger = [(r["score"], r["selected"]) for r in eval_records if r.get("age_group") == "UNDER_40"]
        older = [(r["score"], r["selected"]) for r in eval_records if r.get("age_group") == "40_AND_OLDER"]
        if younger and older:
            results["AGE_ADEA"] = self.evaluate_cohort_disparate_impact(
                category="Age (ADEA)",
                benchmark_name="Under 40 Years",
                protected_name="40 Years and Older",
                benchmark_candidates=younger,
                protected_candidates=older,
            )

        # 3. Regional / Linguistic Origin
        domestic = [(r["score"], r["selected"]) for r in eval_records if r.get("region") == "DOMESTIC_STANDARD"]
        international = [(r["score"], r["selected"]) for r in eval_records if r.get("region") == "INTERNATIONAL_ESL"]
        if domestic and international:
            results["REGIONAL_DIALECT"] = self.evaluate_cohort_disparate_impact(
                category="Regional / Dialect",
                benchmark_name="Standard Domestic English",
                protected_name="International / Multilingual Speakers",
                benchmark_candidates=domestic,
                protected_candidates=international,
            )

        return results

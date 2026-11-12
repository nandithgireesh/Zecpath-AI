"""
Day 63: Curated Multi-Turn Candidate Responses Dataset
Platform: Zecpath Automated Hiring Platform
"""

from typing import Dict
from demo_dataset_ai.models import TurnResponseSet

CURATED_CANDIDATE_RESPONSES: Dict[str, TurnResponseSet] = {
    "CAND-ARCH-01": TurnResponseSet(
        candidate_id="CAND-ARCH-01",
        technical_answer=(
            "In our payment infrastructure, we deployed Apache Kafka with replica set to prevent partition loss. "
            "We optimized latency vs throughput by tuning batch size to 64KB, achieving 25ms p99 latency under "
            "45000 RPS. To prevent race conditions during high write heavy transactions, we utilized distributed "
            "mutex locks in Redis and decoupled workers via thread pool buffers."
        ),
        behavioral_star_answer=(
            "During our Black Friday deployment, our primary PostgreSQL connection pool hit saturation causing a 40% "
            "latency spike. As incident commander, my task was to stabilize checkout within 15 minutes without dropping "
            "orders. I activated our circuit breaker to divert non-critical analytics queries and spun up 4 read replicas. "
            "As a result, transaction latency dropped back to 32ms and zero transactions were dropped."
        ),
        machine_test_code="""
def solve_two_sum(nums, target):
    # Optimal O(N) hash map approach with O(N) space
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""",
        formulation_pause_sec=2.4,
        hesitation_filler_count=1,
    ),
    "CAND-MID-02": TurnResponseSet(
        candidate_id="CAND-MID-02",
        technical_answer=(
            "We used Docker containers and FastAPI to build REST endpoints. For data consistency, we relied on "
            "PostgreSQL transactions with proper indexes on foreign keys to avoid slow queries. We used Celery for "
            "background email notifications."
        ),
        behavioral_star_answer=(
            "We had a situation where a frontend team needed an API urgently. My task was to provide the endpoints by "
            "evening. I prioritized the critical fields, created mock response models, and documented them in Swagger. "
            "This allowed the frontend team to unblock their work on schedule."
        ),
        machine_test_code="""
def solve_two_sum(nums, target):
    # O(N^2) brute force solution with nested loop
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""",
        formulation_pause_sec=1.2,
        hesitation_filler_count=3,
    ),
    "CAND-JUNIOR-03": TurnResponseSet(
        candidate_id="CAND-JUNIOR-03",
        technical_answer="I have learned Python and basic web concepts. We wrote basic loops and functions.",
        behavioral_star_answer="Um, when I was in college, like, we had a team project and, you know, we divided the slides.",
        machine_test_code="""
def solve_two_sum(nums, target):
    pass
""",
        formulation_pause_sec=0.5,
        hesitation_filler_count=7,
    ),
    "CAND-MISMATCH-04": TurnResponseSet(
        candidate_id="CAND-MISMATCH-04",
        technical_answer="I design visual interfaces and layouts in Figma and Adobe Photoshop.",
        behavioral_star_answer="I managed client brand expectations by showing them color palettes and mood boards.",
        machine_test_code="""
# Not a programmer
print('Hello World')
""",
        formulation_pause_sec=0.2,
        hesitation_filler_count=2,
    ),
}


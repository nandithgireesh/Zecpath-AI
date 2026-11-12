"""
Day 29: Fallback & Rephrasing Question Bank
===========================================
Defines pre-mapped fallback hierarchies (Primary, Simplified, Paraphrase, Scenario)
and natural language prompt templates for silence nudges, confusion handling,
and polite transitions.
"""

from typing import Dict, List, Optional
from screening_ai.flow_models import FallbackQuestion, NudgeLevel


# -----------------------------------------------------------------------------
# 1. Competency Fallback Repository
# -----------------------------------------------------------------------------
FALLBACK_QUESTIONS: Dict[str, FallbackQuestion] = {
    "sys_design_scalability": FallbackQuestion(
        primary_id="sys_design_scalability",
        category="System Architecture",
        primary_text="How do you architect distributed backend services to handle sudden traffic spikes and maintain low latency?",
        simplified_text="When a website gets hit with lots of sudden users at the same time, what are some basic things you do to keep it from crashing or slowing down?",
        paraphrase_text="Could you describe your approach to scaling backend servers when traffic suddenly surges?",
        applied_scenario="Imagine a flash sale where traffic jumps 10x in five minutes. What caching, load balancing, or queueing would you put in place?",
        hint_keywords=["caching", "redis", "load balancer", "horizontal scaling", "queues"]
    ),
    "microservices_communication": FallbackQuestion(
        primary_id="microservices_communication",
        category="Microservices",
        primary_text="Can you explain the trade-offs between synchronous REST/gRPC and asynchronous event-driven messaging using Kafka or RabbitMQ?",
        simplified_text="When two microservices need to talk to each other, when do you prefer sending an immediate request versus publishing a background message?",
        paraphrase_text="How do you decide between direct REST calls and message queues like Kafka when connecting microservices?",
        applied_scenario="If an order service needs to update inventory and send confirmation emails without blocking the user, how would you design that communication?",
        hint_keywords=["decoupling", "latency", "async", "kafka", "resilience"]
    ),
    "database_optimization": FallbackQuestion(
        primary_id="database_optimization",
        category="Databases",
        primary_text="What strategies and profiling techniques do you use to diagnose and optimize slow-running SQL queries in production databases?",
        simplified_text="If a database query is taking too long to return data, what steps do you take to find out why and make it faster?",
        paraphrase_text="How do you investigate and speed up slow database queries when users report sluggish pages?",
        applied_scenario="Suppose an analytics dashboard page takes 8 seconds to load due to a large table join. How would you analyze the query execution plan and fix it?",
        hint_keywords=["indexes", "explain plan", "joins", "normalization", "connection pooling"]
    ),
    "concurrency_async": FallbackQuestion(
        primary_id="concurrency_async",
        category="Programming Fundamentals",
        primary_text="How does Python's asyncio event loop operate under the hood, and how does it compare to multi-threading or multi-processing for I/O bound workloads?",
        simplified_text="In simple terms, how does asynchronous programming or asyncio help a program handle multiple tasks without freezing?",
        paraphrase_text="Could you explain how non-blocking I/O or async code works in Python when waiting on network or database calls?",
        applied_scenario="If you need to fetch data from 50 external APIs at the same time, how would you write that in Python so it finishes in 2 seconds instead of 50 seconds?",
        hint_keywords=["event loop", "non-blocking", "coroutines", "threads", "tasks"]
    ),
    "cloud_kubernetes": FallbackQuestion(
        primary_id="cloud_kubernetes",
        category="Cloud & DevOps",
        primary_text="How do you manage zero-downtime rolling deployments, health probes, and resource quotas in Kubernetes production clusters?",
        simplified_text="How do you ensure that when you deploy a new version of an app to Kubernetes, existing users don't experience any downtime or errors?",
        paraphrase_text="Could you walk me through how rolling updates and readiness probes work in containerized environments?",
        applied_scenario="If a new code deployment crashes immediately upon startup, how do Kubernetes readiness probes prevent bad containers from serving live customer traffic?",
        hint_keywords=["rolling update", "readiness probe", "liveness probe", "rollback", "pods"]
    ),
    "salary_expectation": FallbackQuestion(
        primary_id="salary_expectation",
        category="Operational Constraints",
        primary_text="What are your compensation expectations for this role in terms of fixed base and variable incentives?",
        simplified_text="Could you share a ballpark salary or CTC figure you are aiming for in your next position?",
        paraphrase_text="What compensation range or annual package are you expecting for this opportunity?",
        applied_scenario="To help us ensure our client's allocated budget aligns with your expectations, what annual CTC range would make you comfortable moving forward?",
        hint_keywords=["ctc", "lpa", "fixed", "budget", "salary"]
    ),
    "notice_period_availability": FallbackQuestion(
        primary_id="notice_period_availability",
        category="Operational Constraints",
        primary_text="What is your contractual notice period at your current organization, and can it be negotiated or bought out?",
        simplified_text="How soon would you be able to join if selected, and how many days notice do you need to serve?",
        paraphrase_text="What is your current notice period timeline, and is an early release possible?",
        applied_scenario="Our hiring team is aiming for a start date within 30 to 45 days. Where do you stand regarding your current company's exit formalities?",
        hint_keywords=["notice", "days", "immediate", "buyout", "joining date"]
    )
}

# -----------------------------------------------------------------------------
# 2. Silence Nudge Prompt Library
# -----------------------------------------------------------------------------
SILENCE_NUDGES: Dict[NudgeLevel, List[str]] = {
    NudgeLevel.GENTLE_CHECK: [
        "Are you still with me? Take your time, there is no rush.",
        "Take a moment to collect your thoughts. I'm listening whenever you're ready.",
        "Take your time, I'm right here."
    ],
    NudgeLevel.ASSIST_REPHRASE: [
        "I didn't catch that. Would you like me to repeat the question, or would you prefer me to rephrase it?",
        "No worries if you're thinking. Would it help if I rephrased the question into simpler terms?",
        "Still with me? If the question was unclear, just let me know and I can rephrase it."
    ],
    NudgeLevel.TIMEOUT_TRANSITION: [
        "It seems we might have a brief audio pause. Let's move on to the next question so we make good use of our time.",
        "No problem at all! Let's keep things moving and proceed to the next topic. We can always return to this later."
    ]
}

# -----------------------------------------------------------------------------
# 3. Confusion & Clarification Templates
# -----------------------------------------------------------------------------
CONFUSION_RESPONSES: List[str] = [
    "No problem at all, let me break that down into simpler terms for you.",
    "Happy to clarify! Let's look at this from a more practical, day-to-day perspective.",
    "Of course! Let me rephrase that question so it's clearer."
]

# -----------------------------------------------------------------------------
# 4. Repetition Pivot Templates
# -----------------------------------------------------------------------------
REPETITION_PIVOTS: List[str] = [
    "Understood, thanks for reiterating that. Let's delve into a slightly different angle.",
    "Got it, you mentioned that earlier. Building on that foundation, let's talk about...",
    "Thanks for confirming that point again. Let's move forward to see how you handle..."
]

# -----------------------------------------------------------------------------
# 5. Polite Failure & Transition Bridges
# -----------------------------------------------------------------------------
POLITE_SKIP_BRIDGES: List[str] = [
    "That's completely fine, let's keep moving forward. We can always touch on that later.",
    "No worries whatsoever, that's fine! Let's keep moving forward to the next area.",
    "All good, that's completely fine. Let's keep moving forward and discuss another aspect of your experience."
]

DISCONNECT_WRAPUP: str = (
    "It seems we are experiencing persistent connection or audio difficulties today. "
    "Rather than continuing with choppy audio, let's pause our session here. "
    "Our talent acquisition team will reach out shortly to reschedule at your convenience. "
    "Thank you so much for your time today!"
)


# -----------------------------------------------------------------------------
# 6. Helper Lookup Functions
# -----------------------------------------------------------------------------
def get_fallback_for_question(question_id: str) -> Optional[FallbackQuestion]:
    """Retrieve structured fallback record by question ID."""
    return FALLBACK_QUESTIONS.get(question_id)


def get_simplified_question(question_id: str, default_text: Optional[str] = None) -> str:
    """Get simpler low-jargon question."""
    q = FALLBACK_QUESTIONS.get(question_id)
    if q:
        return q.simplified_text
    return default_text or "Could you explain your experience in this area using a simple real-world example?"


def get_paraphrase(question_id: str, default_text: Optional[str] = None) -> str:
    """Get rephrased version for clarity."""
    q = FALLBACK_QUESTIONS.get(question_id)
    if q:
        return q.paraphrase_text
    return default_text or "In other words, could you describe how you approach this in your current role?"


def get_scenario(question_id: str, default_text: Optional[str] = None) -> str:
    """Get applied scenario question."""
    q = FALLBACK_QUESTIONS.get(question_id)
    if q:
        return q.applied_scenario
    return default_text or "Can you walk me through a specific project where you tackled a similar challenge?"


def get_silence_nudge(level: NudgeLevel, index: int = 0) -> str:
    """Retrieve an appropriate silence prompt based on severity tier."""
    options = SILENCE_NUDGES.get(level, SILENCE_NUDGES[NudgeLevel.GENTLE_CHECK])
    return options[index % len(options)]

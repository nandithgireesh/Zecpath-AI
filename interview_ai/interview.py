"""
Day 33: HR Interview AI Module Entry Point
==========================================
Provides unified access to the AI HR Interview System:
- HR Categories, Experience Tiers, Role Tracks, and Phases
- Role-based Question Generator and Curated Question Bank
- Conversation Flow Engine and State Controller
"""

from interview_ai.hr_models import (
    HRCategory,
    ExperienceTier,
    RoleTrack,
    InterviewPhase,
    FollowUpTriggerReason,
    HRQuestionTemplate,
    InterviewTurnState,
    HRInterviewConfig,
    HRInterviewSession,
)
from interview_ai.hr_question_generator import (
    HRQuestionBank,
    HRQuestionGenerator,
)
from interview_ai.hr_flow_engine import HRInterviewFlowEngine


def interview():
    """CLI test harness for starting an interactive HR interview."""
    print("=" * 60)
    print("   ZECPATH-AI: HR INTERVIEW ENGINE (DAY 33 DESIGN)")
    print("=" * 60)
    
    engine = HRInterviewFlowEngine()
    config = HRInterviewConfig.auto_classify(
        candidate_id="cand_test_01",
        candidate_name="Priya Patel",
        job_role="Software Development Engineer",
        experience_years=1.0,
        target_skills=["Python", "Data Structures", "Django"],
    )
    session = engine.start_session(config)
    print(f"Session Created   : {session.session_id}")
    print(f"Experience Tier   : {session.config.experience_tier.value}")
    print(f"Role Track        : {session.config.role_track.value}")
    print(f"Initial Phase     : {session.current_phase.value}")
    print(f"First Prompt (AI) : {session.turns[0].ai_prompt}")
    print("=" * 60)
    return session


if __name__ == "__main__":
    interview()
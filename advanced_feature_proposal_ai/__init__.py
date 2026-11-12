"""
Day 58: Advanced Feature Proposal AI Suite
==========================================
Platform: Zecpath Enterprise Automated Hiring Platform
Package export of models, video emotion engine, coaching engine,
interview analytics dashboard, and roadmap architect.
"""

from .models import (
    HorizonLevel, InnovationArea, EmotionState,
    VideoAnalysisTelemetry, EmotionAnalysisTelemetry,
    RealTimeFeedbackSignal, CandidateCoachingRecommendation,
    InterviewAnalyticsMetrics, RoadmapMilestone
)
from .video_emotion_engine import VideoEmotionAnalysisEngine
from .ai_coaching_engine import AICoachingEngine
from .interview_analytics_dashboard import InterviewAnalyticsDashboard
from .ai_roadmap_architect import AIRoadmapArchitect

__all__ = [
    "HorizonLevel",
    "InnovationArea",
    "EmotionState",
    "VideoAnalysisTelemetry",
    "EmotionAnalysisTelemetry",
    "RealTimeFeedbackSignal",
    "CandidateCoachingRecommendation",
    "InterviewAnalyticsMetrics",
    "RoadmapMilestone",
    "VideoEmotionAnalysisEngine",
    "AICoachingEngine",
    "InterviewAnalyticsDashboard",
    "AIRoadmapArchitect"
]

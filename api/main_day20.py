import logging
import time
import uuid
import gc
import os
import json
from typing import Optional, Dict, List, Any


from starlette.concurrency import run_in_threadpool

from pydantic import BaseModel

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    BackgroundTasks,
)

from api.resume_service import ResumeService

from api.schemas import (
    ATSScoreRequest,
    ATSScoreResponse,
    RankingRequest,
    RankingResponse,
    RankedCandidate,
    ShortlistResponse,
    CandidateEligibilityRequest,
    BatchEligibilityRequest,
    EligibilityRuleSchema,
    QuestionRenderRequest,
    CallScriptRequest,
    TranscriptNormalizeRequest,
    TranscriptNormalizeResponse,
    TranscriptIngestResponse,
    MetadataStandardsResponse,
    STTCleanRequest,
    STTCleanResponse,
    STTTranscribeRequest,
    STTTranscribeResponse,
    STTBenchmarkReportResponse,
    IntentClassifyRequest,
    IntentClassifyResponse,
    AnswerUnderstandRequest,
    AnswerUnderstandResponse,
    DialogueBatchUnderstandRequest,
    DialogueBatchUnderstandResponse,
    ScoreQuestionRequest,
    ScoreQuestionResponse,
    ScoreSessionRequest,
    ScoreSessionResponse,
    ScoringWeightsConfigResponse,
    BehavioralTurnRequest,
    BehavioralTurnResponse,
    BehavioralSessionRequest,
    BehavioralSessionResponse,
    BehavioralBenchmarksResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    ExportReportRequest,
    ExportReportResponse,
    SampleReportsResponse,
    FlowStartRequest,
    FlowStartResponse,
    FlowStepRequest,
    FlowStepResponse,
    FlowEventRequest,
    FlowEventResponse,
    FlowStateResponse,
    SimulateCallRequest,
    SimulateCallResponse,
    BenchmarkEvaluateRequest,
    BenchmarkEvaluateResponse,
    TuneThresholdsRequest,
    TuneThresholdsResponse,
    OptimizationMetricsResponse,
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    LanguageNormalizeRequest,
    LanguageNormalizeResponse,
    EvaluateTurnEdgeCaseRequest,
    EvaluateTurnEdgeCaseResponse,
    EdgeCaseBenchmarkRunResponse,
    ProductionStartSessionRequest,
    ProductionStartSessionResponse,
    ProductionTurnRequest,
    ProductionTurnResponse,
    ProductionFinalizeRequest,
    ProductionFinalizeResponse,
    ProductionHealthResponse,
    ProductionManifestResponse,
)

from screening_ai.production_screening_system import ProductionScreeningSystem
from screening_ai.production_models import ProductionSessionConfig, ScreeningTurnInput
from api.services import ATSService
from screening_ai.eligibility_engine import EligibilityDecisionEngine
from screening_ai.eligibility_config import EligibilityRuleConfig, get_rule_config_for_role
from screening_ai.question_bank import ScreeningQuestionBank
from screening_ai.transcript_models import VoiceTranscriptPayload
from screening_ai.transcript_normalizer import TranscriptNormalizer
from screening_ai.transcript_db import TranscriptDatabaseManager
from screening_ai.transcript_storage import TranscriptStorageManager
from screening_ai.stt_models import AccentType, NoiseCondition
from screening_ai.stt_service import SpeechToTextService
from screening_ai.stt_cleaner import CleanTranscriptProcessor
from screening_ai.stt_benchmark import STTAccuracyBenchmarkHarness
from screening_ai.intent_classifier import CandidateIntentClassifier
from screening_ai.answer_understanding import AnswerUnderstandingEngine
from screening_ai.scoring_engine import ScreeningScoringEngine
from screening_ai.scoring_models import ScoringDimension
from screening_ai.confidence_analyzer import ConfidenceAnalyzer
from screening_ai.sentiment_scorer import SentimentScorer
from screening_ai.behavioral_engine import BehavioralIndicatorsEngine
from screening_ai.behavioral_models import (
    PaceRating,
    SentimentPolarity,
    EngagementLevel,
    CommunicationGrade,
)
from screening_ai.report_models import ScreeningReport, HiringRecommendation
from screening_ai.report_builder import ScreeningReportBuilder
from screening_ai.sample_reports import generate_sample_reports
from screening_ai.call_flow_engine import AICallFlowEngine
from screening_ai.flow_models import DisruptionType
from screening_ai.optimization_models import ThresholdConfig
from screening_ai.simulation_engine import ScreeningSimulationEngine
from screening_ai.threshold_optimizer import ScreeningThresholdOptimizer
from screening_ai.system_evaluator import ScreeningSystemEvaluator
from screening_ai.audio_condition_handler import AudioConditionHandler
from screening_ai.language_mixing_normalizer import LanguageMixingNormalizer
from screening_ai.missing_answer_handler import MissingAnswerHandler
from screening_ai.safety_fallback_engine import SafetyFallbackEngine
from screening_ai.resilient_flow import ResilientCallFlowCoordinator



from api.job_manager import job_manager
from api.logging_config import setup_logging

# =====================================================
# LOGGING
# =====================================================

setup_logging()

logger = logging.getLogger("ZecpathATS")


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title="Zecpath ATS & Screening AI Core Engine",
    description="Unified API combining ATS parsing, ranking, eligibility screening, question bank, transcript pipeline, speech-to-text processing, and answer intent understanding.",
    version="1.0.0",
)

# =====================================================
# DAY-18 PERFORMANCE SETTINGS
# =====================================================

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Measure API processing time for Day-18 performance testing."""
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Process-Time-MS"] = f"{elapsed_ms:.2f}"
    logger.info(
        "API timing | method=%s | path=%s | status=%s | duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# =====================================================
# Initialize Services
# =====================================================

ats_service = ATSService()
resume_service = ResumeService()
eligibility_engine = EligibilityDecisionEngine()
question_bank = ScreeningQuestionBank()
transcript_normalizer = TranscriptNormalizer()
transcript_db = TranscriptDatabaseManager()
transcript_storage = TranscriptStorageManager()
stt_service = SpeechToTextService()
stt_cleaner = CleanTranscriptProcessor()
stt_benchmark = STTAccuracyBenchmarkHarness()
intent_classifier = CandidateIntentClassifier()
answer_engine = AnswerUnderstandingEngine()
scoring_engine = ScreeningScoringEngine()
confidence_analyzer = ConfidenceAnalyzer()
sentiment_scorer = SentimentScorer()
behavioral_engine = BehavioralIndicatorsEngine(
    confidence_analyzer=confidence_analyzer,
    sentiment_scorer=sentiment_scorer,
)
report_builder = ScreeningReportBuilder()
call_flow_engine = AICallFlowEngine()
threshold_optimizer = ScreeningThresholdOptimizer()
simulation_engine = ScreeningSimulationEngine(threshold_optimizer=threshold_optimizer)
system_evaluator = ScreeningSystemEvaluator(threshold_optimizer=threshold_optimizer)



# =====================================================
# SCORE PARSED RESUME AGAINST JOB DESCRIPTION
# =====================================================

class ATSScoreFromResumeRequest(BaseModel):
    """
    Score a previously uploaded/parsed resume using its resume_id
    and the supplied structured job description.
    """
    resume_id: str
    job_description: dict


# =====================================================
# BACKGROUND RESUME PROCESSING
# =====================================================


def process_resume_background(
    job_id: str,
    resume_id: str,
):
    """
    Parse a resume in the background.
    """

    try:

        logger.info(
            f"Background resume processing started | "
            f"job_id={job_id} | "
            f"resume_id={resume_id}"
        )

        # -------------------------------------------------
        # Update job status
        # -------------------------------------------------

        job_manager.update_job(
            job_id,
            status="PROCESSING",
            message="Resume parsing started",
        )

        # -------------------------------------------------
        # Parse resume
        # -------------------------------------------------

        resume = resume_service.parse_resume(resume_id)

        # -------------------------------------------------
        # Mark completed
        # -------------------------------------------------

        job_manager.update_job(
            job_id,
            status="COMPLETED",
            message="Resume parsing completed",
            result={
                "resume_id": resume_id,
                "resume": resume,
            },
        )

        logger.info(
            f"Background resume processing completed | "
            f"job_id={job_id} | "
            f"resume_id={resume_id}"
        )

    except Exception as error:

        logger.exception(f"Background resume processing failed | " f"job_id={job_id}")

        job_manager.update_job(
            job_id,
            status="FAILED",
            message="Resume parsing failed",
            error=str(error),
        )


# =====================================================
# BACKGROUND ATS PROCESSING
# =====================================================


def process_ats_background(
    job_id: str,
    request_data: dict,
):
    """
    Calculate ATS score in the background.
    """

    try:

        logger.info(f"Background ATS processing started | " f"job_id={job_id}")

        # -------------------------------------------------
        # Update job status
        # -------------------------------------------------

        job_manager.update_job(
            job_id,
            status="PROCESSING",
            message="ATS scoring started",
        )

        # -------------------------------------------------
        # Extract request data
        # -------------------------------------------------

        resume = request_data["resume"]
        job_description = request_data["job_description"]

        # -------------------------------------------------
        # Calculate ATS score
        # -------------------------------------------------

        report = ats_service.calculate_score(
            resume,
            job_description,
        )

        # -------------------------------------------------
        # Prepare result
        # -------------------------------------------------

        result = {
            "ats_score": report["final_ats_score"],
            "level": report["level"],
            "skill_score": report["skill_score"],
            "experience_score": report["experience_score"],
            "education_score": report["education_score"],
            "semantic_score": report["semantic_score"],
        }

        # -------------------------------------------------
        # Mark completed
        # -------------------------------------------------

        job_manager.update_job(
            job_id,
            status="COMPLETED",
            message="ATS scoring completed",
            result=result,
        )

        logger.info(
            f"Background ATS processing completed | "
            f"job_id={job_id} | "
            f"ats_score={report['final_ats_score']}"
        )

        # Release large request/report objects after processing.
        del request_data, resume, job_description, report, result
        gc.collect()

    except Exception as error:

        logger.exception(f"Background ATS processing failed | " f"job_id={job_id}")

        job_manager.update_job(
            job_id,
            status="FAILED",
            message="ATS scoring failed",
            error=str(error),
        )


# =====================================================
# ROOT
# =====================================================


@app.get("/")
def root():

    return {
        "message": "Zecpath AI ATS API",
        "status": "running",
        "version": "1.0.0",
    }


# =====================================================
# HEALTH CHECK
# =====================================================


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "ATS Engine",
    }


# =====================================================
# UPLOAD VALIDATION HELPERS
# =====================================================


def validate_pdf_upload(file: UploadFile):
    """Validate type and size before expensive parsing work."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Resume file is too large. Maximum allowed size is 10 MB.",
        )


# =====================================================
# UPLOAD + PARSE RESUME
# =====================================================


@app.post("/ats/upload")
async def upload_resume(
    file: UploadFile = File(...),
):

    try:

        validate_pdf_upload(file)

        # -------------------------------------------------
        # Save resume
        # -------------------------------------------------

        result = await run_in_threadpool(resume_service.save_resume, file)

        resume_id = result["resume_id"]

        # -------------------------------------------------
        # Parse resume
        # -------------------------------------------------

        resume = await run_in_threadpool(resume_service.parse_resume, resume_id)

        # -------------------------------------------------
        # Return parsed resume
        # -------------------------------------------------

        return {
            "resume_id": resume_id,
            "filename": result["filename"],
            "status": "PARSED",
            "resume": resume,
        }

    except HTTPException:

        raise

    except Exception as error:

        logger.exception("Resume upload failed")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# ASYNC RESUME UPLOAD
# =====================================================


@app.post("/ats/upload-async")
def upload_resume_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):

    try:

        validate_pdf_upload(file)

        # -------------------------------------------------
        # Save resume
        # -------------------------------------------------

        result = resume_service.save_resume(file)

        resume_id = result["resume_id"]

        # -------------------------------------------------
        # Create job
        # -------------------------------------------------

        job_id = str(uuid.uuid4())

        job_manager.create_job(job_id)

        logger.info(
            f"Resume upload accepted | " f"job_id={job_id} | " f"resume_id={resume_id}"
        )

        # -------------------------------------------------
        # Start background processing
        # -------------------------------------------------

        background_tasks.add_task(
            process_resume_background,
            job_id,
            resume_id,
        )

        # -------------------------------------------------
        # Return immediately
        # -------------------------------------------------

        return {
            "job_id": job_id,
            "resume_id": resume_id,
            "filename": result["filename"],
            "status": "PENDING",
            "message": "Resume uploaded. Processing started in background.",
        }

    except HTTPException:

        raise

    except Exception as error:

        logger.exception("Async resume upload failed")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# ASYNC ATS SCORING JOB
# =====================================================


@app.post("/ats/jobs")
def create_ats_job(
    request: ATSScoreRequest,
    background_tasks: BackgroundTasks,
):

    try:

        # -------------------------------------------------
        # Generate job ID
        # -------------------------------------------------

        job_id = str(uuid.uuid4())

        # -------------------------------------------------
        # Create job
        # -------------------------------------------------

        job_manager.create_job(job_id)

        logger.info(
            f"ATS job created | "
            f"job_id={job_id} | "
            f"role={request.job_description.role}"
        )

        # -------------------------------------------------
        # Convert Pydantic request to dictionary
        # -------------------------------------------------

        request_data = {
            "resume": request.resume.model_dump(),
            "job_description": (request.job_description.model_dump()),
        }

        # -------------------------------------------------
        # Start background ATS processing
        # -------------------------------------------------

        background_tasks.add_task(
            process_ats_background,
            job_id,
            request_data,
        )

        # -------------------------------------------------
        # Return immediately
        # -------------------------------------------------

        return {
            "job_id": job_id,
            "status": "PENDING",
            "message": "ATS job created successfully",
        }

    except Exception as error:

        logger.exception("Failed to create ATS job")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# JOB STATUS
# =====================================================


@app.get("/ats/jobs/{job_id}")
def get_job_status(
    job_id: str,
):

    job = job_manager.get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job


# =====================================================
# PARSE EXISTING RESUME
# =====================================================


@app.post("/ats/parse/{resume_id}")
async def parse_resume(
    resume_id: str,
):

    try:

        resume = await run_in_threadpool(resume_service.parse_resume, resume_id)

        return {
            "resume_id": resume_id,
            "status": "PARSED",
            "resume": resume,
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        logger.exception("Resume parsing failed")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# ATS SCORE - SYNCHRONOUS
# =====================================================


@app.post(
    "/ats/score",
    response_model=ATSScoreResponse,
)
async def calculate_ats_score(
    request: ATSScoreRequest,
):

    try:

        report = await run_in_threadpool(
            ats_service.calculate_score,
            request.resume.model_dump(),
            request.job_description.model_dump(),
        )

        return {
            "ats_score": report["final_ats_score"],
            "level": report["level"],
            "skill_score": report["skill_score"],
            "experience_score": report["experience_score"],
            "education_score": report["education_score"],
            "semantic_score": report["semantic_score"],
        }

    except Exception as error:

        logger.exception("ATS scoring failed")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# ATS SCORE - FROM UPLOADED/PARSED RESUME
# =====================================================

@app.post(
    "/ats/score-from-resume",
    response_model=ATSScoreResponse,
)
async def calculate_ats_score_from_resume(
    request: ATSScoreFromResumeRequest,
):
    """
    Score a previously uploaded resume against a job description.

    The client supplies only the resume_id returned by /ats/upload
    and the structured job description. The parsed resume is loaded
    automatically from ResumeService.
    """

    try:

        logger.info(
            "ATS score-from-resume requested | resume_id=%s | role=%s",
            request.resume_id,
            request.job_description.get("role", "Unknown Role"),
        )

        # -------------------------------------------------
        # Load the parsed resume automatically
        # -------------------------------------------------

        resume = await run_in_threadpool(
            resume_service.parse_resume,
            request.resume_id,
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Parsed resume not found",
            )

        # -------------------------------------------------
        # Calculate ATS score
        # -------------------------------------------------

        report = await run_in_threadpool(
            ats_service.calculate_score,
            resume,
            request.job_description,
        )

        return {
            "ats_score": report["final_ats_score"],
            "level": report["level"],
            "skill_score": report["skill_score"],
            "experience_score": report["experience_score"],
            "education_score": report["education_score"],
            "semantic_score": report["semantic_score"],
        }

    except HTTPException:
        raise

    except FileNotFoundError as error:

        logger.exception(
            "Resume not found | resume_id=%s",
            request.resume_id,
        )

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        logger.exception(
            "ATS score-from-resume failed | resume_id=%s",
            request.resume_id,
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )




# =====================================================
# RANK CANDIDATES
# =====================================================


@app.post(
    "/ats/rank",
    response_model=RankingResponse,
)
async def rank_candidates(
    request: RankingRequest,
):

    try:

        def calculate_and_rank():
            candidates = []
            for candidate in request.candidates:
                report = ats_service.calculate_score(
                    candidate.resume.model_dump(),
                    request.job_description.model_dump(),
                )
                candidates.append(
                    {
                        "resume": candidate.resume_id,
                        "ats_score": report["final_ats_score"],
                        "level": report["level"],
                    }
                )
            return ats_service.rank_candidates(candidates)

        ranked = await run_in_threadpool(calculate_and_rank)

        # -------------------------------------------------
        # Convert response
        # -------------------------------------------------

        formatted = []

        for candidate in ranked:

            formatted.append(
                RankedCandidate(
                    rank=candidate["rank"],
                    resume_id=candidate["resume"],
                    ats_score=candidate["ats_score"],
                    level=candidate["level"],
                    status=candidate.get(
                        "status",
                        "PENDING",
                    ),
                )
            )

        return {
            "role": request.job_description.role,
            "candidates": formatted,
        }

    except Exception as error:

        logger.exception("Candidate ranking failed")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# SHORTLIST CANDIDATES
# =====================================================


@app.post(
    "/ats/shortlist",
    response_model=ShortlistResponse,
)
async def shortlist_candidates(
    request: RankingRequest,
):

    try:

        def calculate_rank_and_shortlist():
            candidates = []
            for candidate in request.candidates:
                report = ats_service.calculate_score(
                    candidate.resume.model_dump(),
                    request.job_description.model_dump(),
                )
                candidates.append(
                    {
                        "resume": candidate.resume_id,
                        "ats_score": report["final_ats_score"],
                        "level": report["level"],
                    }
                )
            ranked = ats_service.rank_candidates(candidates)
            return ats_service.shortlist_candidates(ranked)

        result = await run_in_threadpool(calculate_rank_and_shortlist)

        # -------------------------------------------------
        # Convert result
        # -------------------------------------------------

        def convert(items):

            return [
                RankedCandidate(
                    rank=item["rank"],
                    resume_id=item["resume"],
                    ats_score=item["ats_score"],
                    level=item["level"],
                    status=item["status"],
                )
                for item in items
            ]

        return {
            "role": request.job_description.role,
            "shortlisted": convert(result["shortlisted"]),
            "review": convert(result["review"]),
            "rejected": convert(result["rejected"]),
        }

    except Exception as error:

        logger.exception("Candidate shortlisting failed")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# DAY 21: ELIGIBILITY DECISION ENGINE ENDPOINTS
# =====================================================


@app.post("/screening/eligibility/evaluate")
async def evaluate_candidate_eligibility(
    request: CandidateEligibilityRequest,
):
    """
    Day 21 - Evaluate single candidate against eligibility rules
    to decide if they qualify for AI voice screening calls.
    """
    try:
        def do_eval():
            config = None
            if request.rules:
                config = EligibilityRuleConfig.from_dict(request.rules.model_dump())
            elif request.role_name:
                config = get_rule_config_for_role(request.role_name)

            cand_data = {
                "candidate_id": request.candidate_id or request.resume_id or request.name,
                "ats_score": request.ats_score,
                "skills": request.skills,
                "total_experience": request.total_experience,
                "location": request.location,
                "notice_period_days": request.notice_period_days,
            }
            return eligibility_engine.evaluate_candidate(cand_data, config)

        result = await run_in_threadpool(do_eval)
        return result

    except Exception as error:
        logger.exception("Eligibility evaluation failed")
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@app.post("/screening/eligibility/batch")
async def batch_evaluate_eligibility_api(
    request: BatchEligibilityRequest,
):
    """
    Day 21 - Batch evaluate multiple candidates against recruiter rules.
    """
    try:
        def do_batch_eval():
            config = None
            if request.rules:
                config = EligibilityRuleConfig.from_dict(request.rules.model_dump())
            elif request.role_name:
                config = get_rule_config_for_role(request.role_name)

            return eligibility_engine.batch_evaluate(request.candidates, config)

        result = await run_in_threadpool(do_batch_eval)
        return result

    except Exception as error:
        logger.exception("Batch eligibility evaluation failed")
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =====================================================
# DAY 22: HR SCREENING QUESTION BANK ENDPOINTS
# =====================================================


@app.get("/screening/questions")
async def get_screening_questions(
    role: Optional[str] = None,
    category: Optional[str] = None,
    mandatory_only: bool = False,
    min_importance: Optional[str] = None,
):
    """
    Day 22 - Query HR screening questions with filtering by role,
    category, mandatory flag, and minimum importance level.
    """
    try:
        def query_questions():
            filtered = question_bank.filter_questions(
                role=role,
                category=category,
                mandatory_only=mandatory_only,
                min_importance=min_importance,
            )
            return {
                "total_found": len(filtered),
                "filters_applied": {
                    "role": role,
                    "category": category,
                    "mandatory_only": mandatory_only,
                    "min_importance": min_importance,
                },
                "questions": [q.model_dump() for q in filtered],
            }

        result = await run_in_threadpool(query_questions)
        return result

    except Exception as error:
        logger.exception("Failed to retrieve screening questions")
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@app.get("/screening/categories")
async def get_screening_categories():
    """
    Day 22 - Retrieve question category taxonomy and evaluation criteria.
    """
    try:
        return {
            "categories": question_bank.category_taxonomy,
            "total_categories": len(question_bank.category_taxonomy),
        }
    except Exception as error:
        logger.exception("Failed to retrieve category taxonomy")
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@app.post("/screening/questions/render")
async def render_screening_question(
    request: QuestionRenderRequest,
):
    """
    Day 22 - Render dynamic question template with candidate context and language localization.
    """
    try:
        def do_render():
            return question_bank.render_question(
                question_id=request.question_id,
                context=request.context,
                language=request.language,
            )

        result = await run_in_threadpool(do_render)
        return result

    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as error:
        logger.exception("Failed to render screening question")
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@app.post("/screening/script/generate")
async def generate_screening_call_script(
    request: CallScriptRequest,
):
    """
    Day 22 - Generate a complete, conversational screening call script
    customized for an automated AI voice agent session.
    """
    try:
        def do_generate():
            script = question_bank.generate_call_script(
                candidate_data=request.candidate_data,
                role_name=request.role_name,
                job_location=request.job_location,
                language=request.language,
                bot_name=request.bot_name,
            )
            return script.model_dump()

        result = await run_in_threadpool(do_generate)
        return result

    except Exception as error:
        logger.exception("Failed to generate screening call script")
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# Day 23 - Voice Transcript Data Architecture Endpoints
# =========================================================

@app.post("/screening/transcripts/normalize", response_model=TranscriptNormalizeResponse)
async def normalize_transcript_utterance(
    request: TranscriptNormalizeRequest,
):
    """
    Day 23 - Normalize raw speech-to-text utterance: strips filler words,
    converts numbers/durations/CTC, and checks confidence thresholds.
    """
    try:
        def do_normalize():
            norm_res = transcript_normalizer.normalize_utterance(
                raw_text=request.raw_text,
                confidence=request.confidence,
            )
            return TranscriptNormalizeResponse(
                raw_text=norm_res.raw_text,
                cleaned_text=norm_res.cleaned_text,
                removed_fillers=norm_res.removed_fillers,
                normalized_entities=norm_res.normalized_entities,
                confidence=norm_res.confidence,
                confidence_level=norm_res.confidence_level.value,
                is_low_confidence=norm_res.is_low_confidence,
            )

        return await run_in_threadpool(do_normalize)

    except Exception as error:
        logger.exception("Failed to normalize speech transcript")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/transcripts/ingest", response_model=TranscriptIngestResponse)
async def ingest_voice_transcript(
    payload: VoiceTranscriptPayload,
):
    """
    Day 23 - Ingest complete voice screening transcript:
    runs full normalization, persists to hierarchical JSON file storage,
    and indexes into SQLite relational database.
    """
    try:
        def do_ingest():
            # 1. Normalize full transcript
            norm_data = transcript_normalizer.normalize_full_transcript(payload)

            # 2. Save to hierarchical file storage
            file_path = transcript_storage.save_transcript(payload)

            # 3. Save to relational SQLite database
            call_id = transcript_db.save_call_session(payload)

            norm_dict = norm_data.model_dump() if hasattr(norm_data, "model_dump") else norm_data.dict()

            return TranscriptIngestResponse(
                session_id=payload.session_id,
                call_id=call_id,
                candidate_id=payload.metadata.candidate_id,
                job_id=payload.metadata.job_id,
                status="INGESTED",
                total_turns=len(payload.turns),
                total_question_interactions=len(payload.question_interactions),
                file_storage_path=file_path,
                db_persisted=True,
                normalized_data=norm_dict,
            )

        return await run_in_threadpool(do_ingest)

    except Exception as error:
        logger.exception("Failed to ingest voice transcript")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/transcripts/{call_id}")
async def get_transcript_session(call_id: str):
    """
    Day 23 - Retrieve structured transcript session from SQLite database by call_id or session_id.
    """
    try:
        def do_get():
            return transcript_db.get_call_session(call_id)

        result = await run_in_threadpool(do_get)
        if not result:
            raise HTTPException(status_code=404, detail=f"Transcript session not found for id: {call_id}")
        return result

    except HTTPException:
        raise
    except Exception as error:
        logger.exception(f"Failed to retrieve transcript session {call_id}")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/transcripts/candidate/{candidate_id}")
async def get_candidate_transcripts(candidate_id: str):
    """
    Day 23 - List all voice screening call sessions recorded for a candidate.
    """
    try:
        def do_get():
            return transcript_db.get_calls_by_candidate(candidate_id)

        result = await run_in_threadpool(do_get)
        return {
            "candidate_id": candidate_id,
            "total_calls": len(result),
            "calls": result,
        }

    except Exception as error:
        logger.exception(f"Failed to retrieve candidate transcripts {candidate_id}")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/transcripts/metadata/standards", response_model=MetadataStandardsResponse)
async def get_transcript_metadata_standards():
    """
    Day 23 - Return formal documentation on metadata standards,
    normalization rules, and database schema conventions.
    """
    return MetadataStandardsResponse(
        standard_name="Zecpath-AI Voice Transcript & Metadata Specification",
        version="1.0.0",
        metadata_fields={
            "candidate_id": "Unique candidate identifier linking to ATS profile",
            "job_id": "Target job requisition identifier",
            "call_id": "Unique voice call session UUID",
            "question_id": "Day 22 Question Bank ID (e.g., INTRO_01, EXP_01, SKILL_ML_01, SAL_02, NP_01)",
            "timestamp_utc": "ISO-8601 UTC timestamp of call initiation",
            "duration_seconds": "Total audio duration in seconds",
            "avg_confidence": "Average STT transcription confidence score (0.0 - 1.0)",
            "call_status": "Call state: SCHEDULED, IN_PROGRESS, COMPLETED, DROPPED, FAILED",
            "language": "Spoken language code: en, hi, ml, ta",
            "speaker": "Dialogue speaker label: BOT, CANDIDATE, SYSTEM",
        },
        normalization_rules=[
            "Whitespace collapse and punctuation normalization",
            "Removal of conversational verbal fillers (um, uh, you know, actually, basically)",
            "Conversion of spoken numbers and fractions into digits (two and a half -> 2.5)",
            "Notice period normalization into integer days and immediate joiner flag",
            "Salary/CTC normalization into LPA float and negotiation flag",
            "Technical skill entity matching across candidate utterances",
            "Confidence thresholding: utterances < 0.70 confidence flagged for review",
        ],
        confidence_thresholds={
            "HIGH": ">= 0.85 (Reliable for autonomous scoring)",
            "MEDIUM": "0.70 - 0.84 (Acceptable, standard evaluation)",
            "LOW": "0.50 - 0.69 (Flagged: Requires human review)",
            "CRITICAL_LOW": "< 0.50 (Trigger automated AI fallback prompt)",
        },
        database_tables=[
            "screening_calls (call session metadata & audit log)",
            "transcript_turns (chronological turn-by-turn dialogue & timestamps)",
            "question_interactions (Q&A pairs mapped to Day 22 questions & extracted entities)",
        ],
    )


@app.get("/screening/transcripts/db/summary")
async def get_transcript_database_summary():
    """
    Day 23 - Return summary telemetry for the transcript SQLite database.
    """
    try:
        def do_summary():
            return transcript_db.get_db_summary()

        return await run_in_threadpool(do_summary)
    except Exception as error:
        logger.exception("Failed to retrieve DB summary")
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# DAY 24 - SPEECH-TO-TEXT INTEGRATION & CLEANING ENDPOINTS
# =========================================================

@app.post("/screening/stt/clean", response_model=STTCleanResponse)
async def clean_speech_transcript(request: STTCleanRequest):
    """
    Day 24 - Clean raw spoken transcripts:
    - Strips filler words (um, uh, like, actually, basically, yaar, na, matlab).
    - Corrects punctuation and infers question marks.
    - Preserves canonical proper noun casing (Python, PyTorch, Docker, B.Tech, LPA).
    - Analyzes edge cases (interrupted speech, partial answers, silence).
    """
    try:
        def do_clean():
            category = request.question_category or "General"
            return stt_cleaner.process_transcript(
                raw_text=request.raw_text,
                category=category,
                silence_duration_sec=request.silence_duration_seconds,
            )

        res = await run_in_threadpool(do_clean)
        return STTCleanResponse(
            original_text=res.original_text,
            cleaned_text=res.cleaned_text,
            removed_fillers=res.removed_fillers,
            punctuation_corrected=res.punctuation_corrected,
            proper_case_applied=res.proper_case_applied,
            edge_case_analysis=res.edge_case_analysis.model_dump(),
        )
    except Exception as error:
        logger.exception("Failed to clean transcript")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/stt/transcribe", response_model=STTTranscribeResponse)
async def transcribe_speech_payload(request: STTTranscribeRequest):
    """
    Day 24 - Ingest speech stream or audio file and transcribe with acoustic profiling:
    - Calculates acoustic confidence adjusted for candidate accent and background noise.
    - Inspects audio waveform if a WAV file is provided.
    - Cleans transcription and infers conversational recovery prompts for edge cases.
    """
    input_source = request.audio_file_path or request.text_payload
    if not input_source:
        raise HTTPException(
            status_code=400,
            detail="Either 'audio_file_path' or 'text_payload' must be provided."
        )

    try:
        # Resolve accent and noise enums
        try:
            accent_enum = AccentType(request.accent)
        except ValueError:
            accent_enum = AccentType.INDIAN_ENGLISH

        try:
            noise_enum = NoiseCondition(request.noise_condition)
        except ValueError:
            noise_enum = NoiseCondition.CLEAN_STUDIO

        def do_transcribe():
            result = stt_service.transcribe(
                raw_text_or_audio_path=input_source,
                accent=accent_enum,
                noise_condition=noise_enum,
                category=request.question_category or "General",
            )
            edge_res = stt_cleaner.process_transcript(
                raw_text=result.raw_transcript,
                category=request.question_category or "General",
                silence_duration_sec=request.silence_duration_seconds or result.audio_metadata.silence_duration_seconds,
            )
            return result, edge_res

        stt_res, clean_res = await run_in_threadpool(do_transcribe)

        return STTTranscribeResponse(
            raw_transcript=stt_res.raw_transcript,
            cleaned_transcript=clean_res.cleaned_text,
            confidence=stt_res.confidence,
            word_confidences=stt_res.word_confidences,
            detected_accent=stt_res.detected_accent.value,
            audio_metadata=stt_res.audio_metadata.model_dump(),
            latency_ms=stt_res.latency_ms,
            edge_case=clean_res.edge_case_analysis.edge_case.value,
            recovery_prompt=clean_res.edge_case_analysis.recovery_prompt,
        )
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("STT transcription failed")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/stt/benchmark/run", response_model=STTBenchmarkReportResponse)
async def run_stt_accuracy_benchmark():
    """
    Day 24 - Run STT Accuracy Benchmark across 6 accents and 4 acoustic noise conditions:
    - Calculates Word Error Rate (WER) and Character Error Rate (CER) via dynamic programming.
    - Saves comprehensive report to data/screening_output/stt_accuracy_benchmark_report.json.
    """
    try:
        def do_benchmark():
            return stt_benchmark.run_benchmark()

        report = await run_in_threadpool(do_benchmark)
        return STTBenchmarkReportResponse(
            total_tests=report.total_tests,
            overall_wer=report.overall_wer,
            overall_cer=report.overall_cer,
            mean_confidence=report.mean_confidence,
            mean_latency_ms=report.mean_latency_ms,
            accent_breakdown=report.accent_breakdown,
            noise_breakdown=report.noise_breakdown,
            generated_at=report.generated_at,
            status=report.status,
        )
    except Exception as error:
        logger.exception("Failed to run STT accuracy benchmark")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/stt/benchmark/report", response_model=STTBenchmarkReportResponse)
async def get_stt_accuracy_benchmark_report():
    """
    Day 24 - Retrieve the latest saved STT Accuracy Benchmark report.
    """
    try:
        def do_get_report():
            report = stt_benchmark.load_saved_report()
            if not report:
                report = stt_benchmark.run_benchmark()
            return report

        report = await run_in_threadpool(do_get_report)
        return STTBenchmarkReportResponse(
            total_tests=report.total_tests,
            overall_wer=report.overall_wer,
            overall_cer=report.overall_cer,
            mean_confidence=report.mean_confidence,
            mean_latency_ms=report.mean_latency_ms,
            accent_breakdown=report.accent_breakdown,
            noise_breakdown=report.noise_breakdown,
            generated_at=report.generated_at,
            status=report.status,
        )
    except Exception as error:
        logger.exception("Failed to get STT accuracy benchmark report")
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# DAY 25 - ANSWER INTENT & UNDERSTANDING ENDPOINTS
# =========================================================

@app.post("/screening/intent/classify", response_model=IntentClassifyResponse)
async def classify_candidate_intent(request: IntentClassifyRequest):
    """
    Day 25 - Classify candidate utterance into communicative intent:
    - Experience, skill confirmation/decline, salary, availability, clarification, off-topic, or vague.
    """
    try:
        def do_classify():
            primary, conf, secondary = intent_classifier.classify_intent(
                text=request.text,
                question_category=request.question_category,
                question_prompt=request.question_prompt,
            )
            return primary, conf, secondary

        primary, conf, secondary = await run_in_threadpool(do_classify)
        return IntentClassifyResponse(
            text=request.text,
            primary_intent=primary.value,
            confidence=conf,
            secondary_intents=[s.value for s in secondary],
        )
    except Exception as error:
        logger.exception("Failed to classify intent")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/answer/understand", response_model=AnswerUnderstandResponse)
async def understand_candidate_answer(request: AnswerUnderstandRequest):
    """
    Day 25 - End-to-end Answer Understanding Engine:
    - Intent classification
    - Deep entity extraction (skills, proficiency, experience, availability, salary)
    - Off-topic deflection & vagueness scoring
    - Semantic StructuredAnswerObject compilation with conversational follow-up recommendations
    """
    try:
        def do_understand():
            return answer_engine.understand_answer(
                raw_text=request.raw_text,
                question_category=request.question_category,
                question_prompt=request.question_prompt,
                turn_id=request.turn_id,
                question_id=request.question_id,
            )

        res = await run_in_threadpool(do_understand)
        return AnswerUnderstandResponse(
            turn_id=res.turn_id,
            question_id=res.question_id,
            question_category=res.question_category,
            raw_text=res.raw_text,
            cleaned_text=res.cleaned_text,
            primary_intent=res.primary_intent.value,
            intent_confidence=res.intent_confidence,
            secondary_intents=[s.value for s in res.secondary_intents],
            extracted_skills=[s.model_dump() for s in res.extracted_skills],
            experience=res.experience.model_dump() if res.experience else None,
            availability=res.availability.model_dump() if res.availability else None,
            salary=res.salary.model_dump() if res.salary else None,
            quality=res.quality.model_dump(),
            follow_up_recommendation=res.follow_up_recommendation,
        )
    except Exception as error:
        logger.exception("Failed to process answer understanding")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/answer/batch-understand", response_model=DialogueBatchUnderstandResponse)
async def batch_understand_dialogue(request: DialogueBatchUnderstandRequest):
    """
    Day 25 - Process multi-turn screening conversation dialogue:
    - Aggregates dominant intents, confirmed skills, and overall dialogue clarity score.
    """
    try:
        def do_batch():
            structured_answers = []
            all_intents = []
            all_skills = set()
            clarity_scores = []

            for turn in request.turns:
                ans = answer_engine.understand_answer(
                    raw_text=turn.raw_text,
                    question_category=turn.question_category,
                    question_prompt=turn.question_prompt,
                    turn_id=turn.turn_id,
                    question_id=turn.question_id,
                )
                structured_answers.append(ans.model_dump())
                all_intents.append(ans.primary_intent.value)
                clarity_scores.append(ans.quality.clarity_score)
                for s in ans.extracted_skills:
                    if s.is_confirmed:
                        all_skills.add(s.skill)

            mean_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 1.0
            return {
                "total_turns_analyzed": len(request.turns),
                "dominant_intents": list(dict.fromkeys(all_intents)),
                "aggregated_skills": sorted(list(all_skills)),
                "overall_clarity_score": round(mean_clarity, 2),
                "structured_answers": structured_answers,
            }

        result = await run_in_threadpool(do_batch)
        return DialogueBatchUnderstandResponse(**result)
    except Exception as error:
        logger.exception("Failed to process dialogue batch understanding")
        raise HTTPException(status_code=500, detail=str(error))


# =========================================================
# Day 26 - Screening Scoring Engine Endpoints
# =========================================================

@app.post("/screening/scoring/evaluate-question", response_model=ScoreQuestionResponse)
async def evaluate_question_score(request: ScoreQuestionRequest):
    """
    Day 26 - Evaluate single candidate question answer:
    - Scores Clarity, Relevance, Completeness, and Consistency (0 - 100).
    - Computes weighted score, grade, strengths, weaknesses, and explainable breakdown.
    """
    try:
        def do_eval():
            breakdown = scoring_engine.score_question_answer(
                raw_text=request.raw_text,
                question_category=request.question_category,
                question_text=request.question_text,
                question_id=request.question_id,
            )
            return ScoreQuestionResponse(
                question_id=breakdown.question_id,
                question_category=breakdown.question_category,
                raw_answer=breakdown.raw_answer,
                cleaned_answer=breakdown.cleaned_answer,
                clarity_score=breakdown.clarity_score,
                relevance_score=breakdown.relevance_score,
                completeness_score=breakdown.completeness_score,
                consistency_score=breakdown.consistency_score,
                weighted_question_score=breakdown.weighted_question_score,
                grade=breakdown.grade.value,
                strengths=breakdown.strengths,
                weaknesses=breakdown.weaknesses,
                penalties=breakdown.penalties,
                explanation=breakdown.explanation,
                dimension_scores={
                    dim_name: dim_obj.model_dump()
                    for dim_name, dim_obj in breakdown.dimension_scores.items()
                },
            )

        return await run_in_threadpool(do_eval)
    except Exception as error:
        logger.exception("Failed to evaluate question score")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/scoring/evaluate-session", response_model=ScoreSessionResponse)
async def evaluate_session_scores(request: ScoreSessionRequest):
    """
    Day 26 - Evaluate complete multi-turn screening conversation session:
    - Evaluates all question turns.
    - Performs cross-turn consistency audit (skill, tenure, and availability contradiction checks).
    - Aggregates category scores and computes overall normalized score (0 - 100).
    - Produces explainable report with strengths, risk factors, and next-round probes.
    """
    try:
        def do_session():
            structured_answers = []
            breakdowns = []

            for turn in request.turns:
                ans = answer_engine.understand_answer(
                    raw_text=turn.raw_text,
                    question_category=turn.question_category,
                    question_prompt=turn.question_text,
                    question_id=turn.question_id,
                )
                structured_answers.append(ans)
                q_score = scoring_engine.score_question_answer(
                    raw_text=turn.raw_text,
                    question_category=turn.question_category,
                    question_text=turn.question_text,
                    question_id=turn.question_id,
                    structured_answer=ans,
                )
                breakdowns.append(q_score)

            final_obj = scoring_engine.aggregate_screening_session(
                questions_breakdowns=breakdowns,
                structured_answers=structured_answers,
                candidate_id=request.candidate_id,
                call_id=request.call_id,
                job_id=request.job_id,
            )

            serialized_questions = [
                ScoreQuestionResponse(
                    question_id=b.question_id,
                    question_category=b.question_category,
                    raw_answer=b.raw_answer,
                    cleaned_answer=b.cleaned_answer,
                    clarity_score=b.clarity_score,
                    relevance_score=b.relevance_score,
                    completeness_score=b.completeness_score,
                    consistency_score=b.consistency_score,
                    weighted_question_score=b.weighted_question_score,
                    grade=b.grade.value,
                    strengths=b.strengths,
                    weaknesses=b.weaknesses,
                    penalties=b.penalties,
                    explanation=b.explanation,
                    dimension_scores={
                        dim_name: dim_obj.model_dump()
                        for dim_name, dim_obj in b.dimension_scores.items()
                    },
                )
                for b in final_obj.per_question_breakdowns
            ]

            return ScoreSessionResponse(
                candidate_id=final_obj.candidate_id,
                call_id=final_obj.call_id,
                job_id=final_obj.job_id,
                overall_score=final_obj.overall_score,
                normalized_score=final_obj.normalized_score,
                recommendation_tier=final_obj.recommendation_tier.value,
                grade=final_obj.grade.value,
                dimension_averages=final_obj.dimension_averages,
                category_breakdowns={
                    cat: summary.model_dump()
                    for cat, summary in final_obj.category_breakdowns.items()
                },
                per_question_breakdowns=serialized_questions,
                explainability=final_obj.explainability.model_dump(),
                evaluated_at=final_obj.evaluated_at,
            )

        return await run_in_threadpool(do_session)
    except Exception as error:
        logger.exception("Failed to evaluate screening session score")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/scoring/weights", response_model=ScoringWeightsConfigResponse)
async def get_scoring_weights():
    """
    Day 26 - Retrieve active dimension weights, category weights, and decision thresholds.
    """
    return ScoringWeightsConfigResponse(
        dimension_weights={
            dim.value: weight for dim, weight in scoring_engine.dimension_weights.items()
        },
        category_weights=scoring_engine.category_weights,
        grade_thresholds={
            "EXCELLENT": ">= 85.0",
            "STRONG": "70.0 - 84.9",
            "MODERATE": "55.0 - 69.9",
            "POOR": "40.0 - 54.9",
            "UNSATISFACTORY": "< 40.0",
        },
        recommendation_thresholds={
            "STRONGLY_RECOMMENDED": "Overall >= 82.0 AND Consistency >= 80.0 without contradictions",
            "RECOMMENDED": "Overall >= 68.0 AND Consistency >= 65.0",
            "RECOMMENDED_WITH_RESERVATIONS": "Overall >= 50.0",
            "NOT_RECOMMENDED": "Overall < 50.0 OR Consistency < 50.0",
        },
    )


# =========================================================
# Day 27 - Confidence & Sentiment Signal Analysis Endpoints
# =========================================================

@app.post("/screening/behavioral/analyze-turn", response_model=BehavioralTurnResponse)
async def analyze_behavioral_turn(request: BehavioralTurnRequest):
    """
    Day 27 - Analyze vocal confidence, pacing (WPM), hesitation patterns,
    uncertainty/hedging, and sentiment polarity for a single candidate turn.
    """
    try:
        def do_turn_analysis():
            analysis = behavioral_engine.analyze_turn(
                turn_id=request.turn_id or "TURN_01",
                raw_text=request.raw_text,
                duration_seconds=request.duration_seconds,
                latency_ms=request.latency_ms,
                stt_acoustic_confidence=request.stt_acoustic_confidence,
                word_confidences=request.word_confidences,
            )
            c_metrics = analysis.confidence_metrics
            s_result = analysis.sentiment
            ci = analysis.communication_indicators

            return BehavioralTurnResponse(
                turn_id=analysis.turn_id,
                raw_text=analysis.raw_text,
                confidence_score=c_metrics.final_confidence_score,
                confidence_tier=c_metrics.confidence_tier,
                pace_wpm=c_metrics.pace_metrics.wpm,
                pace_rating=c_metrics.pace_metrics.pace_rating.value,
                hesitation_penalties=c_metrics.total_hesitation_penalty,
                hesitation_incidents=[i.model_dump() for i in c_metrics.hesitation_incidents],
                uncertainty_score=c_metrics.uncertainty.uncertainty_score,
                hedging_phrases=c_metrics.uncertainty.hedging_phrases,
                sentiment_polarity=s_result.polarity.value,
                compound_sentiment=s_result.compound_score,
                engagement_level=s_result.engagement_level.value,
                emotional_tone=s_result.emotional_tone,
                communication_indicators=ci.model_dump(),
                observations=analysis.key_observations,
            )

        return await run_in_threadpool(do_turn_analysis)
    except Exception as error:
        logger.exception("Failed to analyze behavioral turn")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/behavioral/analyze-session", response_model=BehavioralSessionResponse)
async def analyze_behavioral_session(request: BehavioralSessionRequest):
    """
    Day 27 - Synthesize multi-turn candidate interview call into an executive
    Behavioral Indicators Report with green flags, red flags, and interview probes.
    """
    try:
        def do_session_analysis():
            turns_data = [t.model_dump() for t in request.turns]
            report = behavioral_engine.analyze_session(
                candidate_id=request.candidate_id or "CANDIDATE_01",
                session_id=request.session_id or "CALL_SESSION_01",
                turns=turns_data,
            )

            serialized_turns = [
                BehavioralTurnResponse(
                    turn_id=t.turn_id,
                    raw_text=t.raw_text,
                    confidence_score=t.confidence_metrics.final_confidence_score,
                    confidence_tier=t.confidence_metrics.confidence_tier,
                    pace_wpm=t.confidence_metrics.pace_metrics.wpm,
                    pace_rating=t.confidence_metrics.pace_metrics.pace_rating.value,
                    hesitation_penalties=t.confidence_metrics.total_hesitation_penalty,
                    hesitation_incidents=[i.model_dump() for i in t.confidence_metrics.hesitation_incidents],
                    uncertainty_score=t.confidence_metrics.uncertainty.uncertainty_score,
                    hedging_phrases=t.confidence_metrics.uncertainty.hedging_phrases,
                    sentiment_polarity=t.sentiment.polarity.value,
                    compound_sentiment=t.sentiment.compound_score,
                    engagement_level=t.sentiment.engagement_level.value,
                    emotional_tone=t.sentiment.emotional_tone,
                    communication_indicators=t.communication_indicators.model_dump(),
                    observations=t.key_observations,
                )
                for t in report.turn_breakdowns
            ]

            return BehavioralSessionResponse(
                candidate_id=report.candidate_id,
                session_id=report.session_id,
                total_turns_analyzed=report.total_turns_analyzed,
                overall_confidence_score=report.overall_confidence_score,
                overall_sentiment=report.overall_sentiment.value,
                average_compound_sentiment=report.average_compound_sentiment,
                average_wpm=report.average_wpm,
                overall_pace_rating=report.overall_pace_rating.value,
                communication_indicators=report.communication_indicators.model_dump(),
                behavioral_green_flags=report.behavioral_green_flags,
                behavioral_red_flags=report.behavioral_red_flags,
                recruiter_executive_summary=report.recruiter_executive_summary,
                recommended_interviewer_probes=report.recommended_interviewer_probes,
                turn_breakdowns=serialized_turns,
            )

        return await run_in_threadpool(do_session_analysis)
    except Exception as error:
        logger.exception("Failed to analyze behavioral session")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/behavioral/benchmarks", response_model=BehavioralBenchmarksResponse)
async def get_behavioral_benchmarks():
    """
    Day 27 - Retrieve standard speech pacing benchmarks, confidence tiers,
    sentiment categories, and communication indicators.
    """
    return BehavioralBenchmarksResponse(
        pace_benchmarks={
            "VERY_SLOW": "< 100 WPM (May indicate recall difficulty or extreme hesitation)",
            "SLOW": "100 - 120 WPM (Deliberate, thoughtful pacing)",
            "OPTIMAL": "120 - 165 WPM (Professional natural conversational rhythm)",
            "FAST": "165 - 185 WPM (Energetic, high-fluency pacing)",
            "RUSHED": "> 185 WPM (Rapid delivery, possible nervousness)",
        },
        confidence_tiers={
            "HIGH": "Score >= 80.0 (Direct, minimal fillers, steady cadence)",
            "MODERATE": "Score 60.0 - 79.9 (Occasional hesitation or hedging)",
            "LOW": "Score < 60.0 (Excessive fillers, stutters, or heavy uncertainty)",
        },
        sentiment_categories={
            "VERY_POSITIVE": "Compound > 0.45 (High enthusiasm, passion, eager)",
            "POSITIVE": "Compound 0.15 to 0.45 (Constructive, collaborative, cooperative)",
            "NEUTRAL": "Compound -0.15 to 0.15 (Professional, matter-of-fact)",
            "NEGATIVE": "Compound < -0.15 (Dissatisfied, critical, reluctant)",
            "DEFENSIVE": "Hostile or guarded expressions ('none of your business', etc.)",
        },
        communication_indicators={
            "Fluency": "Smoothness of delivery without stutters, fillers, or awkward pauses (25%)",
            "Assertiveness": "Directness of answers without excessive hedging (25%)",
            "Engagement": "Constructive enthusiasm and cooperative demeanor (20%)",
            "Pacing": "Conversational rhythm centered around 120-165 WPM (15%)",
            "Articulation": "Depth of vocabulary and structured answers (15%)",
        },
    )


# =========================================================
# Day 28 - AI Screening Report Generator Endpoints
# =========================================================

@app.post("/screening/report/generate", response_model=GenerateReportResponse)
async def generate_screening_report(payload: GenerateReportRequest):
    """
    Day 28 - Synthesize multi-dimensional scoring and behavioral indicators
    into a structured, recruiter-ready AI screening report.
    """
    try:
        def do_generate():
            report = report_builder.build_report(
                candidate_id=payload.candidate_id,
                candidate_name=payload.candidate_name,
                job_id=payload.job_id,
                role_name=payload.role_name,
                candidate_data=payload.candidate_data,
                question_evaluations=payload.question_evaluations,
                role_mandatory_skills=payload.role_mandatory_skills,
                role_bonus_skills=payload.role_bonus_skills,
                budget_max_lpa=payload.budget_max_lpa,
                budget_min_lpa=payload.budget_min_lpa,
                max_acceptable_notice_days=payload.max_acceptable_notice_days,
                behavioral_summary=payload.behavioral_summary,
                recommended_interviewer_probes=payload.recommended_interviewer_probes,
            )
            return GenerateReportResponse(
                report_id=report.report_id,
                candidate_name=report.candidate_name,
                role_name=report.role_name,
                recommendation=report.recommendation.value,
                recommendation_badge=report.recommendation_badge,
                overall_score=report.scores.overall_score,
                overall_grade=report.scores.overall_grade,
                executive_summary=report.executive_summary,
                report=report_builder.export_json(report),
                markdown_export=report_builder.export_markdown(report),
                html_export=report_builder.export_html(report),
            )

        return await run_in_threadpool(do_generate)
    except Exception as error:
        logger.exception("Failed to generate screening report")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/report/export", response_model=ExportReportResponse)
async def export_screening_report(payload: ExportReportRequest):
    """
    Day 28 - Export an existing screening report into Markdown, HTML, or structured JSON.
    """
    try:
        def do_export():
            report = ScreeningReport.model_validate(payload.report)
            fmt = payload.export_format.upper()
            if fmt == "MARKDOWN":
                content = report_builder.export_markdown(report)
            elif fmt == "HTML":
                content = report_builder.export_html(report)
            elif fmt == "JSON":
                content = json.dumps(report_builder.export_json(report), indent=2)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported export format: {payload.export_format}")

            return ExportReportResponse(
                report_id=report.report_id,
                export_format=fmt,
                content=content,
            )

        return await run_in_threadpool(do_export)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Failed to export screening report")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/report/samples", response_model=SampleReportsResponse)
async def get_sample_screening_reports():
    """
    Day 28 - Retrieve pre-built realistic candidate screening reports demonstrating
    all recommendation tiers (STRONG_HIRE, HIRE, PROCEED_WITH_CAUTION, NO_HIRE).
    """
    try:
        def do_samples():
            samples = generate_sample_reports()
            return SampleReportsResponse(
                total_samples=len(samples),
                samples={k: report_builder.export_json(v) for k, v in samples.items()},
            )

        return await run_in_threadpool(do_samples)
    except Exception as error:
        logger.exception("Failed to retrieve sample reports")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/report/schema")
async def get_screening_report_schema():
    """
    Day 28 - Retrieve the JSON schema definition for exportable AI screening reports.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "schemas", "screening_report_schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Screening report schema file not found")


# =====================================================
# DAY 29: AI CONVERSATION FLOW ENDPOINTS
# =====================================================


@app.post("/screening/flow/start", response_model=FlowStartResponse)
async def start_screening_flow(payload: FlowStartRequest):
    """
    Day 29 - Start a new AI conversational screening session and emit the opening greeting.
    """
    try:
        def do_start():
            session, action = call_flow_engine.start_session(
                candidate_id=payload.candidate_id,
                candidate_name=payload.candidate_name,
                role_name=payload.role_name,
                question_ids=payload.question_ids,
            )
            return FlowStartResponse(
                session_id=session.session_id,
                candidate_name=session.candidate_name,
                current_state=session.current_state.value,
                current_phase=session.current_phase.value,
                action=action.model_dump(),
            )

        return await run_in_threadpool(do_start)
    except Exception as error:
        logger.exception("Failed to start screening flow")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/flow/step", response_model=FlowStepResponse)
async def step_screening_flow(payload: FlowStepRequest):
    """
    Day 29 - Advance the conversational state machine by one turn with candidate utterance or silence.
    """
    try:
        def do_step():
            session, action = call_flow_engine.process_turn(
                session_id=payload.session_id,
                candidate_utterance=payload.candidate_utterance,
                silence_ms=payload.silence_ms,
            )
            return FlowStepResponse(
                session_id=session.session_id,
                current_state=session.current_state.value,
                current_phase=session.current_phase.value,
                current_question_index=session.current_question_index,
                action=action.model_dump(),
                is_completed=session.is_completed,
            )

        return await run_in_threadpool(do_step)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        logger.exception("Failed to step screening flow")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/flow/handle-event", response_model=FlowEventResponse)
async def handle_flow_event(payload: FlowEventRequest):
    """
    Day 29 - Manually trigger and test a specific conversational event (silence timeout, confusion, repetition).
    """
    try:
        def do_event():
            try:
                disruption = DisruptionType(payload.disruption_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid disruption type: {payload.disruption_type}")

            session, action = call_flow_engine.handle_explicit_event(
                session_id=payload.session_id,
                disruption_type=disruption,
                payload=payload.payload,
            )
            return FlowEventResponse(
                session_id=session.session_id,
                disruption_type=disruption.value,
                action=action.model_dump(),
                current_state=session.current_state.value,
            )

        return await run_in_threadpool(do_event)
    except HTTPException:
        raise
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        logger.exception("Failed to handle flow event")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/flow/state/{session_id}", response_model=FlowStateResponse)
async def get_flow_state(session_id: str):
    """
    Day 29 - Retrieve the full live session state and summary for an active or completed call.
    """
    try:
        def do_state():
            session = call_flow_engine.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
            summary = call_flow_engine.get_summary(session_id)
            return FlowStateResponse(
                session_id=session_id,
                session=session.model_dump(),
                summary=summary.model_dump(),
            )

        return await run_in_threadpool(do_state)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Failed to get flow state")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/flow/schema")
async def get_flow_schema():
    """
    Day 29 - Retrieve the JSON schema definition for AI screening call flow and state machine.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "schemas", "call_flow_schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Call flow schema file not found")


# =========================================================
# Day 30 - System Testing & Optimization Endpoints
# =========================================================

@app.post("/screening/optimization/simulate-call", response_model=SimulateCallResponse)
async def simulate_screening_call(payload: SimulateCallRequest):
    """
    Day 30 - Execute a simulated multi-turn AI screening call for a benchmark profile.
    """
    try:
        def do_simulate():
            res = simulation_engine.simulate_call(
                candidate_id=payload.candidate_id,
                use_optimized_thresholds=payload.use_optimized_thresholds,
            )
            return SimulateCallResponse(
                session_id=res.session_id,
                candidate_id=res.candidate_id,
                candidate_name=res.candidate_name,
                target_role=res.target_role,
                archetype=res.archetype.value,
                total_turns=res.total_turns,
                ai_overall_score=res.ai_overall_score,
                ai_technical_score=res.ai_technical_score,
                ai_communication_score=res.ai_communication_score,
                ai_recommendation=res.ai_recommendation.value,
                human_recommendation=res.human_recommendation.value,
                recommendation_matches=res.recommendation_matches,
                is_false_rejection=res.is_false_rejection,
                is_false_acceptance=res.is_false_acceptance,
                summary_notes=res.summary_notes,
            )

        return await run_in_threadpool(do_simulate)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        logger.exception("Failed to simulate screening call")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/optimization/evaluate-benchmark", response_model=BenchmarkEvaluateResponse)
async def evaluate_benchmark_suite(payload: BenchmarkEvaluateRequest):
    """
    Day 30 - Evaluate complete 12-candidate human ground-truth benchmark suite.
    """
    try:
        def do_benchmark():
            report = system_evaluator.run_full_benchmark_evaluation()
            return BenchmarkEvaluateResponse(
                report_id=report.report_id,
                generated_at=report.generated_at,
                baseline_metrics=report.baseline_metrics.model_dump(),
                optimized_metrics=report.optimized_metrics.model_dump(),
                false_rejection_reduction_pct=report.false_rejection_reduction_pct,
                resolved_candidates=report.resolved_candidates,
                benchmark_profiles_evaluated=report.benchmark_profiles_evaluated,
                key_takeaways=report.key_takeaways,
            )

        return await run_in_threadpool(do_benchmark)
    except Exception as error:
        logger.exception("Failed to evaluate benchmark suite")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/optimization/tune-thresholds", response_model=TuneThresholdsResponse)
async def tune_screening_thresholds(payload: TuneThresholdsRequest):
    """
    Day 30 - Apply tuned threshold parameters and evaluate the impact on precision, F1, and FRR.
    """
    try:
        def do_tune():
            new_cfg = ThresholdConfig(
                name="custom_tuned",
                overall_hire_cutoff=payload.overall_hire_cutoff,
                strong_hire_cutoff=payload.strong_hire_cutoff,
                technical_hire_cutoff=payload.technical_hire_cutoff,
                communication_hire_cutoff=payload.communication_hire_cutoff,
                enable_tech_compensation=payload.enable_tech_compensation,
                brevity_protection=payload.brevity_protection,
                hesitation_penalty_dampener=payload.hesitation_penalty_dampener,
            )
            profiles = simulation_engine.get_profiles()
            comparison = threshold_optimizer.compare_benchmarks(
                benchmark_profiles=profiles,
                optimized_cfg=new_cfg,
            )
            return TuneThresholdsResponse(
                status="Thresholds successfully updated and validated against benchmark",
                applied_thresholds=new_cfg.model_dump(),
                resulting_f1_score=comparison.optimized_metrics.f1_score,
                resulting_frr=comparison.optimized_metrics.false_rejection_rate,
            )

        return await run_in_threadpool(do_tune)
    except Exception as error:
        logger.exception("Failed to tune screening thresholds")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/optimization/metrics", response_model=OptimizationMetricsResponse)
async def get_optimization_metrics():
    """
    Day 30 - Retrieve top-level optimized performance metrics across the ground-truth benchmark.
    """
    try:
        def do_metrics():
            report = system_evaluator.run_full_benchmark_evaluation()
            m = report.optimized_metrics
            return OptimizationMetricsResponse(
                total_profiles=report.benchmark_profiles_evaluated,
                accuracy=m.accuracy,
                precision=m.precision,
                recall=m.recall,
                f1_score=m.f1_score,
                false_rejection_rate=m.false_rejection_rate,
                false_acceptance_rate=m.false_acceptance_rate,
                cohens_kappa=m.cohens_kappa,
            )

        return await run_in_threadpool(do_metrics)
    except Exception as error:
        logger.exception("Failed to get optimization metrics")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/optimization/schema")
async def get_optimization_schema():
    """
    Day 30 - Retrieve Draft-07 JSON schema definition for system optimization and benchmark reports.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "schemas", "system_optimization_schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="System optimization schema file not found")


# =========================================================
# Day 31 - Edge Case & Failure Handling Endpoints
# =========================================================

@app.post("/screening/edge-cases/analyze-audio", response_model=AudioAnalysisResponse)
async def analyze_audio_conditions(payload: AudioAnalysisRequest):
    """
    Day 31 - Evaluate telephony acoustic telemetry:
    - Analyzes Signal-to-Noise Ratio (SNR), amplitude, clipping, and packet loss.
    - Classifies background noise (Stationary hum, Traffic, Babble, Keyboard).
    - Determines if acoustic degradation requires a retry or confidence discounting.
    """
    try:
        def do_analyze():
            telemetry = AudioConditionHandler.evaluate_telemetry(
                snr_db=payload.snr_db,
                peak_amplitude_dbfs=payload.peak_amplitude_dbfs,
                packet_loss_rate=payload.packet_loss_rate,
                clipping_events=payload.clipping_events,
                codec_bitrate_kbps=payload.codec_bitrate_kbps,
                noise_hints=payload.noise_hints,
            )
            needs_retry, action, prompt = AudioConditionHandler.should_request_acoustic_retry(telemetry)
            return AudioAnalysisResponse(
                snr_db=telemetry.snr_db,
                estimated_noise_type=telemetry.estimated_noise_type.value,
                estimated_audio_degradation=telemetry.estimated_audio_degradation.value,
                acoustic_confidence_discount=telemetry.acoustic_confidence_discount,
                needs_acoustic_retry=needs_retry,
                recommended_action=action.value if action else None,
                retry_prompt=prompt,
            )

        return await run_in_threadpool(do_analyze)
    except Exception as error:
        logger.exception("Failed to analyze audio conditions")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/edge-cases/normalize-language", response_model=LanguageNormalizeResponse)
async def normalize_bilingual_language(payload: LanguageNormalizeRequest):
    """
    Day 31 - Identify and translate Hinglish / code-switched candidate utterances:
    - Normalizes conversational Hindi connectives to canonical English.
    - Preserves all technical keywords and stack entities.
    - Converts transliterated numerical entities (salary in Lakhs, notice period in days).
    """
    try:
        def do_norm():
            res = LanguageMixingNormalizer.analyze_and_normalize(payload.text)
            return LanguageNormalizeResponse(
                original_text=res.original_utterance,
                detected_category=res.detected_category.value,
                detected_languages=res.detected_languages,
                normalized_text=res.normalized_english_text,
                extracted_entities=res.extracted_entities,
                confidence=res.confidence_score,
            )

        return await run_in_threadpool(do_norm)
    except Exception as error:
        logger.exception("Failed to normalize language mixing")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/edge-cases/evaluate-turn", response_model=EvaluateTurnEdgeCaseResponse)
async def evaluate_edge_case_turn(payload: EvaluateTurnEdgeCaseRequest):
    """
    Day 31 - End-to-end resilient turn evaluation:
    - Analyzes audio condition, code-switching, and missing answer flags.
    - Applies retry logic, progressive degradation, or emergency human handoff.
    """
    try:
        def do_eval():
            coordinator = ResilientCallFlowCoordinator(
                session_id=payload.session_id,
                candidate_id=payload.candidate_id,
            )
            res = coordinator.evaluate_turn(
                turn_id=payload.turn_id,
                utterance=payload.utterance,
                question_id=payload.question_id,
                topic=payload.topic,
                next_topic=payload.next_topic,
                snr_db=payload.snr_db,
                peak_amplitude_dbfs=payload.peak_amplitude_dbfs,
                packet_loss_rate=payload.packet_loss_rate,
                clipping_events=payload.clipping_events,
                noise_hints=payload.noise_hints,
            )
            return EvaluateTurnEdgeCaseResponse(
                session_id=payload.session_id,
                turn_id=res.turn_id,
                original_text=res.original_text,
                normalized_text=res.normalized_text,
                audio_telemetry=res.audio_telemetry.model_dump(),
                code_switch_category=res.code_switch_result.detected_category.value,
                extracted_entities=res.code_switch_result.extracted_entities,
                is_safe_to_advance=res.is_safe_to_advance,
                safety_tier=res.safety_tier.value,
                system_response=res.system_response,
                audit_flags=res.audit_flags,
            )

        return await run_in_threadpool(do_eval)
    except Exception as error:
        logger.exception("Failed to evaluate edge-case turn")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/edge-cases/run-benchmark", response_model=EdgeCaseBenchmarkRunResponse)
async def run_edge_case_benchmark():
    """
    Day 31 - Execute the 16-scenario Edge-Case Benchmark Suite:
    - Tests Poor Audio, Language Mixing, Missing Answers, and Background Noise.
    - Returns detailed scenario breakdown and overall system resilience rate.
    """
    try:
        benchmark_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "benchmarks", "edge_case_benchmark.json"
        )
        if not os.path.exists(benchmark_path):
            raise HTTPException(status_code=404, detail="Edge-case benchmark dataset not found")

        with open(benchmark_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def do_benchmark():
            scenarios = data.get("scenarios", [])
            results = []
            audio_count = 0
            code_switch_count = 0
            missing_count = 0
            noise_count = 0
            successful_handlings = 0

            for sc in scenarios:
                coordinator = ResilientCallFlowCoordinator(
                    session_id=f"sess_{sc['scenario_id']}",
                    candidate_id=sc["candidate_name"].lower().replace(" ", "_"),
                )
                tele = sc.get("telemetry", {})
                res = coordinator.evaluate_turn(
                    turn_id=1,
                    utterance=sc["utterance"],
                    question_id=sc["target_question_id"],
                    topic=sc["question_topic"],
                    next_topic=sc["next_topic"],
                    snr_db=tele.get("snr_db", 26.0),
                    peak_amplitude_dbfs=tele.get("peak_amplitude_dbfs", -12.0),
                    packet_loss_rate=tele.get("packet_loss_rate", 0.0),
                    clipping_events=tele.get("clipping_events", 0),
                    codec_bitrate_kbps=tele.get("codec_bitrate_kbps", 64.0),
                    noise_hints=tele.get("noise_hints", {}),
                )

                cat = sc["category"]
                if cat == "poor_audio":
                    audio_count += 1
                elif cat == "language_mixing":
                    code_switch_count += 1
                elif cat == "missing_answers":
                    missing_count += 1
                elif cat == "background_noise":
                    noise_count += 1

                # Verify expected handling
                matched = (res.is_safe_to_advance == sc["should_advance"])
                if matched:
                    successful_handlings += 1

                results.append({
                    "scenario_id": sc["scenario_id"],
                    "candidate_name": sc["candidate_name"],
                    "category": cat,
                    "original_utterance": sc["utterance"],
                    "normalized_text": res.normalized_text,
                    "is_safe_to_advance": res.is_safe_to_advance,
                    "safety_tier": res.safety_tier.value,
                    "system_response": res.system_response,
                    "audit_flags": res.audit_flags,
                    "handling_matched_expected": matched,
                })

            resilience_rate = round(successful_handlings / len(scenarios) if scenarios else 1.0, 3)

            return EdgeCaseBenchmarkRunResponse(
                total_scenarios=len(scenarios),
                scenarios_evaluated=len(results),
                audio_recoveries_handled=audio_count,
                code_switches_normalized=code_switch_count,
                missing_answers_recovered=missing_count,
                noise_adaptations_handled=noise_count,
                overall_resilience_rate=resilience_rate,
                scenario_results=results,
            )

        return await run_in_threadpool(do_benchmark)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Failed to run edge-case benchmark")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/edge-cases/schema")
async def get_edge_case_schema():
    """
    Day 31 - Retrieve Draft-07 JSON schema definition for edge case and failure handling telemetry.
    """
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "schemas", "failure_handling_schema.json"
    )
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Failure handling schema file not found")


# =========================================================
# Day 32 - Production Screening System Finalization Endpoints
# =========================================================

production_system = ProductionScreeningSystem()


@app.get("/screening/production/health", response_model=ProductionHealthResponse)
async def get_production_system_health():
    """
    Day 32 - Diagnostic health and readiness probe verifying all 11 screening subsystems.
    """
    try:
        health = await run_in_threadpool(production_system.get_system_health)
        return ProductionHealthResponse(
            status=health.status,
            timestamp=health.timestamp,
            version=health.version,
            uptime_status=health.uptime_status,
            subsystems=[s.model_dump() for s in health.subsystems],
            active_sessions_count=health.active_sessions_count,
        )
    except Exception as error:
        logger.exception("Failed to check production system health")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/screening/production/manifest", response_model=ProductionManifestResponse)
async def get_production_handover_manifest():
    """
    Day 32 - Engineering handover manifest cataloging all 12 days of AI screening deliverables.
    """
    try:
        manifest = await run_in_threadpool(production_system.get_handover_manifest)
        return ProductionManifestResponse(
            track_title=manifest.track_title,
            completion_date=manifest.completion_date,
            author=manifest.author,
            organization=manifest.organization,
            repository=manifest.repository,
            total_curriculum_days=manifest.total_curriculum_days,
            modules_inventory=manifest.modules_inventory,
            metrics_summary=manifest.metrics_summary,
            api_endpoints_count=manifest.api_endpoints_count,
            test_suites_count=manifest.test_suites_count,
        )
    except Exception as error:
        logger.exception("Failed to get handover manifest")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/production/session/start", response_model=ProductionStartSessionResponse)
async def start_production_screening_session(request: ProductionStartSessionRequest):
    """
    Day 32 - Initialize an end-to-end production screening call session for a candidate.
    """
    try:
        config = ProductionSessionConfig(
            candidate_id=request.candidate_id,
            candidate_name=request.candidate_name,
            job_role=request.job_role,
            target_experience_years=request.target_experience_years,
            max_budget_lpa=request.max_budget_lpa,
            max_notice_days=request.max_notice_days,
            required_skills=request.required_skills,
            apply_threshold_optimization=request.apply_threshold_optimization,
            enable_acoustic_fairness_buffer=request.enable_acoustic_fairness_buffer,
            enable_hinglish_normalization=request.enable_hinglish_normalization,
        )
        session = await run_in_threadpool(production_system.start_session, config)
        initial_prompt = session.turns[0]["text"] if session.turns else ""
        return ProductionStartSessionResponse(
            session_id=session.session_id,
            candidate_id=session.config.candidate_id,
            candidate_name=session.config.candidate_name,
            job_role=session.config.job_role,
            status=session.status,
            current_state=session.current_state,
            initial_ai_prompt=initial_prompt,
            created_at=session.created_at,
        )
    except Exception as error:
        logger.exception("Failed to start production screening session")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/production/session/turn", response_model=ProductionTurnResponse)
async def process_production_screening_turn(request: ProductionTurnRequest):
    """
    Day 32 - Execute an inbound conversational turn through the resilient production pipeline:
    Acoustics -> Hinglish Normalization -> Silence Recovery -> Intent -> Scoring.
    """
    try:
        turn_input = ScreeningTurnInput(
            turn_index=request.turn_index,
            candidate_speech=request.candidate_speech,
            snr_db=request.snr_db,
            amplitude_dbfs=request.amplitude_dbfs,
            packet_loss_rate=request.packet_loss_rate,
            clipping_events=request.clipping_events,
            response_time_seconds=request.response_time_seconds,
        )
        out = await run_in_threadpool(
            production_system.process_turn, request.session_id, turn_input
        )
        return ProductionTurnResponse(
            session_id=request.session_id,
            turn_index=out.turn_index,
            current_state=out.current_state,
            ai_spoken_prompt=out.ai_spoken_prompt,
            detected_intent=out.detected_intent,
            normalized_speech=out.normalized_speech,
            extracted_entities=out.extracted_entities,
            acoustic_discount=out.acoustic_discount,
            safety_tier=out.safety_tier,
            is_terminal=out.is_terminal,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        logger.exception("Failed to process production turn")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/screening/production/session/finalize", response_model=ProductionFinalizeResponse)
async def finalize_production_screening_session(request: ProductionFinalizeRequest):
    """
    Day 32 - Finalize session, evaluate eligibility, compute calibrated scores, and generate report.
    """
    try:
        report = await run_in_threadpool(
            production_system.finalize_session, request.session_id
        )
        return ProductionFinalizeResponse(
            session_id=report["session_id"],
            candidate_id=report["candidate_id"],
            candidate_name=report["candidate_name"],
            job_role=report["job_role"],
            completed_at=report["completed_at"],
            eligibility_verified=report["eligibility_verified"],
            final_score=report["final_score"],
            decision=report["decision"],
            score_breakdown=report["score_breakdown"],
            technologies_verified=report["technologies_verified"],
            brevity_protection_applied=report["brevity_protection_applied"],
            false_rejection_risk=report["false_rejection_risk"],
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        logger.exception("Failed to finalize production session")
        raise HTTPException(status_code=500, detail=str(error))









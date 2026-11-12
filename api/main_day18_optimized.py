import logging
import time
import uuid
import gc

from starlette.concurrency import run_in_threadpool

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
)

from api.services import ATSService

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
    title="Zecpath AI - ATS API",
    description=(
        "API for resume upload, parsing, scoring, "
        "ranking, shortlisting and asynchronous processing"
    ),
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

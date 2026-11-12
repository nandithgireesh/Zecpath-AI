from datetime import datetime
from typing import Dict


class JobManager:

    def __init__(self):

        self.jobs: Dict[str, dict] = {}

    # --------------------------------------------------
    # Create Job
    # --------------------------------------------------

    def create_job(self, job_id: str):

        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "PENDING",
            "message": "Job created",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "result": None,
            "error": None,
        }

    # --------------------------------------------------
    # Update Job
    # --------------------------------------------------

    def update_job(
        self,
        job_id: str,
        status: str,
        message: str = "",
        result=None,
        error=None,
    ):

        if job_id not in self.jobs:
            return

        self.jobs[job_id]["status"] = status
        self.jobs[job_id]["message"] = message

        if result is not None:
            self.jobs[job_id]["result"] = result

        if error is not None:
            self.jobs[job_id]["error"] = error

        if status in ["COMPLETED", "FAILED"]:

            self.jobs[job_id]["completed_at"] = datetime.now().isoformat()

    # --------------------------------------------------
    # Get Job
    # --------------------------------------------------

    def get_job(self, job_id: str):

        return self.jobs.get(job_id)

    # --------------------------------------------------
    # Delete Job
    # --------------------------------------------------

    def delete_job(self, job_id: str):

        if job_id in self.jobs:

            del self.jobs[job_id]


job_manager = JobManager()

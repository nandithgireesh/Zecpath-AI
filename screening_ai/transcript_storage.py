import os
import json
from typing import Optional, List, Dict, Any
from screening_ai.transcript_models import VoiceTranscriptPayload, NormalizedScreeningData


DEFAULT_TRANSCRIPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "screening_transcripts"
)


class TranscriptStorageManager:
    """
    Day 23 Hierarchical File Storage Manager.
    Stores and retrieves voice screening transcripts organized by job_id and candidate_id.
    """

    def __init__(self, base_dir: str = DEFAULT_TRANSCRIPTS_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_target_path(self, job_id: str, candidate_id: str, call_id: str) -> str:
        safe_job = str(job_id).replace(" ", "_")
        safe_cand = str(candidate_id).replace(" ", "_")
        safe_call = str(call_id).replace(" ", "_")
        job_dir = os.path.join(self.base_dir, safe_job)
        cand_dir = os.path.join(job_dir, safe_cand)
        os.makedirs(cand_dir, exist_ok=True)
        return os.path.join(cand_dir, f"{safe_call}.json")

    def save_transcript(self, payload: VoiceTranscriptPayload) -> str:
        """Serialize voice transcript payload to hierarchical JSON file."""
        meta = payload.metadata
        call_id = meta.call_id or payload.session_id
        target_path = self._get_target_path(meta.job_id, meta.candidate_id, call_id)

        data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return target_path

    def get_transcript(self, job_id: str, candidate_id: str, call_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve voice transcript by hierarchical keys."""
        target_path = self._get_target_path(job_id, candidate_id, call_id)
        if not os.path.exists(target_path):
            return None

        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_transcripts(self, job_id: Optional[str] = None, candidate_id: Optional[str] = None) -> List[str]:
        """List all saved transcript file paths, optionally filtered by job_id or candidate_id."""
        matching = []
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.base_dir)
                    parts = rel_path.split(os.sep)

                    # Structure: {job_id}/{candidate_id}/{call_id}.json
                    if len(parts) >= 3:
                        j_id, c_id, _ = parts[0], parts[1], parts[2]
                        if job_id and j_id != str(job_id).replace(" ", "_"):
                            continue
                        if candidate_id and c_id != str(candidate_id).replace(" ", "_"):
                            continue
                    matching.append(full_path)

        return matching

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from screening_ai.transcript_models import VoiceTranscriptPayload, CallStatus, SpeakerType


from contextlib import contextmanager

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "screening.db"
)


class TranscriptDatabaseManager:
    """
    Day 23 SQLite Database Manager for Screening Interaction Architecture.
    Provides schema management, relational persistence, and indexing for voice transcripts.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Create relational tables and indexes if they do not already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Screening calls session table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS screening_calls (
                call_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                candidate_name TEXT,
                role_name TEXT,
                start_time TEXT NOT NULL,
                duration_seconds REAL DEFAULT 0.0,
                avg_confidence REAL DEFAULT 0.0,
                call_status TEXT DEFAULT 'COMPLETED',
                language TEXT DEFAULT 'en',
                created_at TEXT NOT NULL
            );
            """)

            # 2. Transcript turns table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcript_turns (
                turn_id TEXT PRIMARY KEY,
                call_id TEXT NOT NULL,
                turn_index INTEGER NOT NULL,
                speaker TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                normalized_text TEXT,
                start_time_ms INTEGER DEFAULT 0,
                end_time_ms INTEGER DEFAULT 0,
                confidence REAL DEFAULT 1.0,
                is_low_confidence INTEGER DEFAULT 0,
                FOREIGN KEY(call_id) REFERENCES screening_calls(call_id) ON DELETE CASCADE
            );
            """)

            # 3. Question interactions table (Linked to Day 22 Question IDs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_interactions (
                interaction_id TEXT PRIMARY KEY,
                call_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                category TEXT NOT NULL,
                prompt_text TEXT NOT NULL,
                response_raw TEXT NOT NULL,
                response_normalized TEXT,
                extracted_entities TEXT,
                confidence REAL DEFAULT 1.0,
                validation_status TEXT DEFAULT 'VALID',
                FOREIGN KEY(call_id) REFERENCES screening_calls(call_id) ON DELETE CASCADE
            );
            """)

            # Indexes for high-frequency queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_candidate ON screening_calls(candidate_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_job ON screening_calls(job_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_turns_call ON transcript_turns(call_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_call ON question_interactions(call_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_qid ON question_interactions(question_id);")

            conn.commit()

    def save_call_session(self, payload: VoiceTranscriptPayload) -> str:
        """
        Atomically persist a complete voice screening call, dialogue turns,
        and question interaction records into the relational database.
        """
        meta = payload.metadata
        call_id = meta.call_id or payload.session_id
        session_id = payload.session_id

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Insert or replace call session record
            cursor.execute("""
            INSERT OR REPLACE INTO screening_calls (
                call_id, session_id, candidate_id, job_id, candidate_name, role_name,
                start_time, duration_seconds, avg_confidence, call_status, language, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id,
                session_id,
                meta.candidate_id,
                meta.job_id,
                meta.candidate_name,
                meta.role_name,
                meta.timestamp_utc,
                meta.duration_seconds,
                meta.avg_confidence,
                meta.call_status.value if isinstance(meta.call_status, CallStatus) else str(meta.call_status),
                meta.language,
                datetime.now(timezone.utc).isoformat()
            ))

            # Delete existing turns/interactions for idempotency
            cursor.execute("DELETE FROM transcript_turns WHERE call_id = ?", (call_id,))
            cursor.execute("DELETE FROM question_interactions WHERE call_id = ?", (call_id,))

            # Insert turns
            for idx, turn in enumerate(payload.turns):
                speaker_val = turn.speaker.value if isinstance(turn.speaker, SpeakerType) else str(turn.speaker)
                cursor.execute("""
                INSERT INTO transcript_turns (
                    turn_id, call_id, turn_index, speaker, raw_text, normalized_text,
                    start_time_ms, end_time_ms, confidence, is_low_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turn.turn_id,
                    call_id,
                    idx,
                    speaker_val,
                    turn.raw_text,
                    turn.normalized_text or turn.raw_text,
                    turn.start_time_ms,
                    turn.end_time_ms,
                    turn.confidence,
                    1 if turn.is_low_confidence else 0
                ))

            # Insert question interactions
            for qi in payload.question_interactions:
                ent_dict = qi.extracted_entities.model_dump() if hasattr(qi.extracted_entities, "model_dump") else qi.extracted_entities.dict()
                cursor.execute("""
                INSERT INTO question_interactions (
                    interaction_id, call_id, question_id, category, prompt_text,
                    response_raw, response_normalized, extracted_entities, confidence, validation_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    qi.interaction_id,
                    call_id,
                    qi.question_id,
                    qi.category,
                    qi.prompt_text,
                    qi.response_raw,
                    qi.response_normalized or qi.response_raw,
                    json.dumps(ent_dict),
                    qi.confidence,
                    qi.validation_status
                ))

            conn.commit()

        return call_id

    def get_call_session(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full call session with all dialogue turns and question interactions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM screening_calls WHERE call_id = ? OR session_id = ?", (call_id, call_id))
            call_row = cursor.fetchone()
            if not call_row:
                return None

            actual_call_id = call_row["call_id"]

            cursor.execute("SELECT * FROM transcript_turns WHERE call_id = ? ORDER BY turn_index ASC", (actual_call_id,))
            turn_rows = cursor.fetchall()

            cursor.execute("SELECT * FROM question_interactions WHERE call_id = ?", (actual_call_id,))
            interaction_rows = cursor.fetchall()

            turns = [dict(r) for r in turn_rows]
            interactions = []
            for r in interaction_rows:
                item = dict(r)
                if item.get("extracted_entities"):
                    try:
                        item["extracted_entities"] = json.loads(item["extracted_entities"])
                    except Exception:
                        pass
                interactions.append(item)

            result = dict(call_row)
            result["turns"] = turns
            result["question_interactions"] = interactions
            return result

    def get_calls_by_candidate(self, candidate_id: str) -> List[Dict[str, Any]]:
        """List all screening call summaries for a given candidate."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM screening_calls WHERE candidate_id = ? ORDER BY created_at DESC",
                (candidate_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_calls_by_job(self, job_id: str) -> List[Dict[str, Any]]:
        """List all screening call summaries for a given job requisition."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM screening_calls WHERE job_id = ? ORDER BY created_at DESC",
                (job_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_db_summary(self) -> Dict[str, Any]:
        """Aggregate database metrics for telemetry and reporting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total_calls, AVG(avg_confidence) as mean_conf FROM screening_calls")
            call_stats = dict(cursor.fetchone())

            cursor.execute("SELECT COUNT(*) as total_turns FROM transcript_turns")
            turn_stats = dict(cursor.fetchone())

            cursor.execute("SELECT COUNT(*) as total_interactions FROM question_interactions")
            qi_stats = dict(cursor.fetchone())

            return {
                "total_calls": call_stats["total_calls"] or 0,
                "average_confidence": round(call_stats["mean_conf"] or 0.0, 3),
                "total_turns": turn_stats["total_turns"] or 0,
                "total_question_interactions": qi_stats["total_interactions"] or 0,
                "db_path": self.db_path
            }

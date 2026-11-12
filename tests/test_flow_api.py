"""
Integration Tests: Day 29 AI Conversation Flow REST Endpoints
=============================================================
Validates all /screening/flow/* API routes using FastAPI TestClient.
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import unittest
from fastapi.testclient import TestClient
from api.main_day20 import app


class TestScreeningFlowAPI(unittest.TestCase):
    """Integration test suite for Day 29 AI conversation flow endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_start_flow_endpoint(self):
        """Test POST /screening/flow/start initializes session and emits greeting."""
        payload = {
            "candidate_id": "cand_day29_01",
            "candidate_name": "Arjun Menon",
            "role_name": "Senior Cloud Solutions Architect"
        }
        response = self.client.post("/screening/flow/start", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()

        self.assertTrue(data["session_id"].startswith("session_"))
        self.assertEqual(data["candidate_name"], "Arjun Menon")
        self.assertEqual(data["current_state"], "AWAITING_INPUT")
        self.assertEqual(data["current_phase"], "GREETING_CONSENT")
        self.assertIn("Arjun Menon", data["action"]["text_to_speak"])
        self.assertTrue(data["action"]["should_listen"])

    def test_02_step_flow_affirmative_greeting(self):
        """Test candidate affirming readiness advances from GREETING to first technical question."""
        # 1. Start session
        start_res = self.client.post("/screening/flow/start", json={
            "candidate_id": "cand_day29_02",
            "candidate_name": "Divya Rao",
            "role_name": "Senior Python Backend Engineer"
        })
        self.assertEqual(start_res.status_code, 200)
        session_id = start_res.json()["session_id"]

        # 2. Candidate says ready
        step_payload = {
            "session_id": session_id,
            "candidate_utterance": "Yes, I can hear you clearly and I am ready to begin.",
            "silence_ms": 0
        }
        step_res = self.client.post("/screening/flow/step", json=step_payload)
        self.assertEqual(step_res.status_code, 200, step_res.text)
        step_data = step_res.json()

        self.assertEqual(step_data["current_phase"], "CORE_TECHNICAL")
        self.assertEqual(step_data["current_state"], "AWAITING_INPUT")
        self.assertEqual(step_data["current_question_index"], 0)
        self.assertTrue(len(step_data["action"]["text_to_speak"]) > 20)

    def test_03_step_flow_silence_nudge(self):
        """Test silence duration generates a gentle nudge action."""
        # 1. Start session
        start_res = self.client.post("/screening/flow/start", json={
            "candidate_id": "cand_day29_03",
            "candidate_name": "Vikram Seth",
            "role_name": "DevOps Engineer"
        })
        session_id = start_res.json()["session_id"]

        # 2. Send 7000ms silence
        silence_payload = {
            "session_id": session_id,
            "candidate_utterance": "",
            "silence_ms": 7000
        }
        step_res = self.client.post("/screening/flow/step", json=silence_payload)
        self.assertEqual(step_res.status_code, 200)
        data = step_res.json()

        self.assertEqual(data["action"]["action_type"], "NUDGE_SILENCE")
        self.assertIn("Are you still with me", data["action"]["text_to_speak"])

    def test_04_handle_event_confusion(self):
        """Test explicit confusion event returns simplified clarification."""
        # 1. Start session
        start_res = self.client.post("/screening/flow/start", json={
            "candidate_id": "cand_day29_04",
            "candidate_name": "Kavita Pillai",
            "role_name": "Backend Engineer"
        })
        session_id = start_res.json()["session_id"]

        # 2. Move past greeting
        self.client.post("/screening/flow/step", json={
            "session_id": session_id,
            "candidate_utterance": "Yes, I am ready"
        })

        # 3. Trigger confusion event
        event_res = self.client.post("/screening/flow/handle-event", json={
            "session_id": session_id,
            "disruption_type": "CANDIDATE_CONFUSION",
            "payload": {"utterance": "I'm sorry, I don't understand what you mean by distributed architecture."}
        })
        self.assertEqual(event_res.status_code, 200, event_res.text)
        data = event_res.json()
        self.assertEqual(data["disruption_type"], "CANDIDATE_CONFUSION")
        self.assertEqual(data["action"]["action_type"], "CLARIFY_CONFUSION")
        self.assertTrue(any(k in data["action"]["text_to_speak"].lower() for k in ["break that down", "clarify", "rephrase", "simpler", "clearer"]))

    def test_05_get_flow_state(self):
        """Test GET /screening/flow/state/{session_id} returns session and summary."""
        # 1. Start session
        start_res = self.client.post("/screening/flow/start", json={
            "candidate_id": "cand_day29_05",
            "candidate_name": "Rohit Nair",
            "role_name": "Fullstack Engineer"
        })
        session_id = start_res.json()["session_id"]

        # 2. Retrieve state
        state_res = self.client.get(f"/screening/flow/state/{session_id}")
        self.assertEqual(state_res.status_code, 200, state_res.text)
        data = state_res.json()

        self.assertEqual(data["session_id"], session_id)
        self.assertIn("session", data)
        self.assertIn("summary", data)
        self.assertEqual(data["session"]["candidate_name"], "Rohit Nair")
        self.assertEqual(data["summary"]["completion_status"], "IN_PROGRESS")

    def test_06_get_flow_schema(self):
        """Test GET /screening/flow/schema returns valid Draft-07 JSON schema."""
        schema_res = self.client.get("/screening/flow/schema")
        self.assertEqual(schema_res.status_code, 200, schema_res.text)
        data = schema_res.json()
        self.assertEqual(data["title"], "AICallFlowSchema")
        self.assertEqual(data["$schema"], "http://json-schema.org/draft-07/schema#")
        self.assertIn("properties", data)
        self.assertIn("current_phase", data["properties"])

    def test_07_not_found_errors(self):
        """Verify proper 404 responses for non-existent session IDs."""
        res = self.client.get("/screening/flow/state/session_non_existent")
        self.assertEqual(res.status_code, 404)

        step_res = self.client.post("/screening/flow/step", json={"session_id": "session_non_existent"})
        self.assertEqual(step_res.status_code, 404)


if __name__ == "__main__":
    unittest.main()

"""
Day 59: API & Integration Planning - Formal JSON Schemas
========================================================
Platform: Zecpath Enterprise Automated Hiring Platform
Generates and validates OpenAPI 3.1 & JSON Schema Draft-07 compliant
definitions for all 5 core AI endpoints.
"""

from typing import Dict, Any
import json
from .models import (
    ResumeParseRequest, AsyncJobResponse,
    ATSScoreRequest, ATSScoreResponse,
    ScreeningSessionRequest, ScreeningUtteranceRequest, ScreeningUtteranceResponse,
    InterviewTurnRequest, InterviewTurnResponse,
    DecisionArbitrationRequest, DecisionArbitrationResponse,
    APIErrorEnvelope
)


class APISchemaRegistry:
    """
    Central repository exporting machine-readable JSON schemas
    for automated API gateways, client SDKs, and contract testing.
    """

    @staticmethod
    def get_all_schemas() -> Dict[str, Dict[str, Any]]:
        return {
            "ResumeParseRequest": ResumeParseRequest.model_json_schema(),
            "AsyncJobResponse": AsyncJobResponse.model_json_schema(),
            "ATSScoreRequest": ATSScoreRequest.model_json_schema(),
            "ATSScoreResponse": ATSScoreResponse.model_json_schema(),
            "ScreeningSessionRequest": ScreeningSessionRequest.model_json_schema(),
            "ScreeningUtteranceRequest": ScreeningUtteranceRequest.model_json_schema(),
            "ScreeningUtteranceResponse": ScreeningUtteranceResponse.model_json_schema(),
            "InterviewTurnRequest": InterviewTurnRequest.model_json_schema(),
            "InterviewTurnResponse": InterviewTurnResponse.model_json_schema(),
            "DecisionArbitrationRequest": DecisionArbitrationRequest.model_json_schema(),
            "DecisionArbitrationResponse": DecisionArbitrationResponse.model_json_schema(),
            "APIErrorEnvelope": APIErrorEnvelope.model_json_schema(),
        }

    @staticmethod
    def get_openapi_paths_specification() -> Dict[str, Any]:
        """
        Returns OpenAPI 3.1.0 compatible paths and operations mapping.
        """
        return {
            "/api/v1/ai/resume/parse": {
                "post": {
                    "summary": "Submit resume for asynchronous entity parsing & extraction",
                    "operationId": "parseResumeAsync",
                    "tags": ["Resume AI"],
                    "x-processing-mode": "ASYNC",
                    "x-sla-target-seconds": 3.0,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ResumeParseRequest"}}}
                    },
                    "responses": {
                        "202": {
                            "description": "Job accepted and queued for worker processing",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AsyncJobResponse"}}}
                        },
                        "400": {"description": "Invalid payload", "content": {"application/problem+json": {"schema": {"$ref": "#/components/schemas/APIErrorEnvelope"}}}}
                    }
                }
            },
            "/api/v1/ai/ats/score": {
                "post": {
                    "summary": "Calculate semantic ATS compatibility between candidate and JD",
                    "operationId": "calculateATSScore",
                    "tags": ["ATS AI"],
                    "x-processing-mode": "ASYNC",
                    "x-sla-target-seconds": 1.5,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ATSScoreRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "description": "ATS score and skill gap breakdown computed",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ATSScoreResponse"}}}
                        }
                    }
                }
            },
            "/api/v1/ai/screening/utterance": {
                "post": {
                    "summary": "Process candidate voice/text utterance in conversational screening",
                    "operationId": "processScreeningTurn",
                    "tags": ["Screening AI"],
                    "x-processing-mode": "SYNC",
                    "x-sla-target-ms": 80.0,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ScreeningUtteranceRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "description": "Next question and real-time eligibility intent",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ScreeningUtteranceResponse"}}}
                        }
                    }
                }
            },
            "/api/v1/ai/interview/turn": {
                "post": {
                    "summary": "Real-time evaluation of interview answer and code execution",
                    "operationId": "evaluateInterviewTurn",
                    "tags": ["Interview AI"],
                    "x-processing-mode": "SYNC",
                    "x-sla-target-ms": 50.0,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/InterviewTurnRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "description": "Scored turn, Socratic follow-up, and pacing feedback",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/InterviewTurnResponse"}}}
                        }
                    }
                }
            },
            "/api/v1/ai/decision/arbitrate": {
                "post": {
                    "summary": "Arbitrate multi-stage assessment scores into final hiring recommendation",
                    "operationId": "arbitrateFinalDecision",
                    "tags": ["Decision AI"],
                    "x-processing-mode": "SYNC",
                    "x-sla-target-ms": 40.0,
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DecisionArbitrationRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "description": "Final recommendation verdict and audit certification",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DecisionArbitrationResponse"}}}
                        }
                    }
                }
            }
        }

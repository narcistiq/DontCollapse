"""
main.py — FastAPI server exposing the resilience pipeline via a single endpoint.

Usage:
    uvicorn main:app --reload

Endpoint:
    POST /analyze
    Body: { "scenario": "heavy_rain" | "storm_surge" | "sea_level_rise" | "repeated_flooding" }
    Returns: full narrative JSON for all scored zones
"""

import json
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from pipeline import resilience_pipeline


# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="Tampa Bay Resilience API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_SCENARIOS = ["heavy_rain", "storm_surge", "sea_level_rise", "repeated_flooding"]


# ── Request model ─────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    scenario: str


# ── Runner + session service (created once at startup) ────────────────────────

session_service = InMemorySessionService()
APP_NAME = "tampa_resilience"

runner = Runner(
    agent=resilience_pipeline,
    app_name=APP_NAME,
    session_service=session_service,
)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    if request.scenario not in VALID_SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario. Choose from: {VALID_SCENARIOS}",
        )

    # Each request gets its own session so state doesn't bleed between calls
    session_id = str(uuid.uuid4())
    user_id = "engineer"

    session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    # The user message tells the pipeline which scenario to run
    user_message = Content(
        role="user",
        parts=[Part(text=f"Run the resilience analysis for scenario: {request.scenario}")]
    )

    # Stream through all agent events and collect the final state
    final_state = {}
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        # Capture session state after each agent completes
        if event.is_final_response():
            session = session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
            final_state = session.state

    # The NarrativeAgent stores its output under 'narratives'
    raw_narratives = final_state.get("narratives", "")

    # Strip markdown fences if Gemini wrapped the JSON
    clean = raw_narratives.strip().removeprefix("```json").removesuffix("```").strip()

    try:
        result = json.loads(clean)
    except (json.JSONDecodeError, TypeError):
        # Return the raw string if parsing fails so the frontend can debug
        result = {"raw": raw_narratives}

    return result


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "valid_scenarios": VALID_SCENARIOS}
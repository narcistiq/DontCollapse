"""
main.py — FastAPI server exposing the resilience pipeline via a single endpoint.

Usage:
    uvicorn main:app --reload

Endpoint:
    POST /analyze
    Body: { "scenario": "heavy rainfall" | "storm surge" | "sea-level-rise increase" | "repeated flooding days" }
    Returns: full narrative JSON for all scored zones
"""
from dotenv import load_dotenv
load_dotenv()
import json
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from backend.pipeline import resilience_pipeline


# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="Don't Collpase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_SCENARIOS = ["heavy rainfall", "storm surge", "sea-level-rise increase", "repeated flooding days"]


# ── Request model ─────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    scenario: str


# ── Runner + session service (created once at startup) ────────────────────────

session_service = InMemorySessionService()
APP_NAME = "dont_collapse"

runner = Runner(
    agent=resilience_pipeline,
    app_name=APP_NAME,
    session_service=session_service,
)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        if request.scenario not in VALID_SCENARIOS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scenario. Choose from: {VALID_SCENARIOS}",
            )

        session_id = str(uuid.uuid4())
        user_id = "engineer"

        # Use the runner's own session service, not a separate one
        await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

        user_message = Content(
            role="user",
            parts=[Part(text=f"Run the resilience analysis for scenario: {request.scenario}")]
        )

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            pass

        session = await runner.session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

        raw_narratives = session.state.get("final_output", "")
        clean = raw_narratives.strip().removeprefix("```json").removesuffix("```").strip()

        try:
            result = json.loads(clean)
        except (json.JSONDecodeError, TypeError):
            result = {"raw": raw_narratives}

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "valid_scenarios": VALID_SCENARIOS}
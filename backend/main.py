"""
main.py — FastAPI server exposing the resilience pipeline via single endpoint.
"""
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from backend.pipeline import run_resilience_pipeline

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="Don't Collpase API (Groq Edition)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_SCENARIOS = ["live conditions", "category 5 hurricane", "heavy rainfall", "storm surge", "sea-level-rise increase", "repeated flooding days", "severe heatwave", "baseline"]

class AnalyzeRequest(BaseModel):
    scenario: str

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        scenario = request.scenario.lower().replace("-", " ")
        if scenario not in VALID_SCENARIOS:
             # Just fallback to baseline if unknown
             scenario = "baseline"

        result = run_resilience_pipeline(scenario)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class LogisticsRequest(BaseModel):
    zone_id: str
    severity: int

@app.post("/logistics/handshake")
async def logistics_handshake(request: LogisticsRequest):
    """
    Mock endpoint to represent another 'Specialist Agent' (Logistics Agent).
    Demonstrates A2A architecture in ADK.
    """
    if request.severity > 80:
        return {"status": "success", "allocation_status": f"URGENT: Deploying 50 buses and 10 high-water rescue vehicles to Zone {request.zone_id}."}
    else:
        return {"status": "success", "allocation_status": f"Monitoring Zone {request.zone_id}. Standing by with standard emergency ops."}

@app.get("/health")
def health():
    return {"status": "ok", "backend": "groq"}

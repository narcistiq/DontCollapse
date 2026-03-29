"""
scorer_agent.py — Deterministic fragility scorer.

Uses a custom BaseAgent instead of LlmAgent so NO Gemini call is made.
The score_zones function does all the work in pure Python; the result
is written directly to session state['scores'].
"""

import json
from pathlib import Path
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part


# ── Load static data once at import time ──────────────────────────────────────

DATA_PATH = Path(__file__).parent.parent / "data" / "tampa_data.json"

with open(DATA_PATH) as f:
    TAMPA_DATA = json.load(f)


# ── Scoring logic (deterministic, no LLM needed) ─────────────────────────────

def score_zones(scenario_key: str) -> dict:
    """
    Score every Tampa Bay zone for a given flood scenario.

    Args:
        scenario_key: one of 'heavy_rain' | 'storm_surge' |
                      'sea_level_rise' | 'repeated_flooding'

    Returns:
        A dict with 'scenario_label' and a ranked list of 'scored_zones'.
    """
    if scenario_key not in TAMPA_DATA["scenarios"]:
        return {
            "error": f"Unknown scenario '{scenario_key}'. "
                     f"Valid options: {list(TAMPA_DATA['scenarios'].keys())}"
        }

    scenario = TAMPA_DATA["scenarios"][scenario_key]
    threshold = scenario["elevation_threshold_ft"]
    scored = []

    for zone in TAMPA_DATA["zones"]:
        # Each factor normalised to 0–1; higher = more fragile.

        elev_gap = max(0, threshold - zone["elevation_ft"])
        elev_score = min(elev_gap / threshold, 1.0)

        drain_score = 1.0 - ((zone["drainage_quality"] - 1) / 4)

        route_score = 1.0 - min((zone["alternate_routes"] - 1) / 4, 1.0)

        shelter_score = min(zone["distance_to_shelter_mi"] / 6.0, 1.0)

        history_score = min(zone["flood_history_events"] / 8.0, 1.0)

        raw = (
            scenario["elevation_weight"] * elev_score
            + scenario["drainage_weight"] * drain_score
            + scenario["access_weight"] * route_score
            + scenario["shelter_weight"] * shelter_score
            + scenario["history_weight"] * history_score
        )

        fragility_score = round(raw * 100, 1)

        scored.append({
            "id": zone["id"],
            "name": zone["name"],
            "fragility_score": fragility_score,
            "factors": {
                "elevation_ft": zone["elevation_ft"],
                "drainage_quality": zone["drainage_quality"],
                "alternate_routes": zone["alternate_routes"],
                "distance_to_shelter_mi": zone["distance_to_shelter_mi"],
                "flood_history_events": zone["flood_history_events"],
            },
            "infrastructure": zone["infrastructure"],
        })

    scored.sort(key=lambda z: z["fragility_score"], reverse=True)

    return {
        "scenario_key": scenario_key,
        "scenario_label": scenario["label"],
        "scored_zones": scored[:3],
    }


# ── Custom agent — no LLM call, writes directly to session state ──────────────

class ScorerAgent(BaseAgent):
    """
    Runs score_zones() in pure Python and stores the result in
    session state['scores']. Costs zero Gemini API calls.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:

        scenario_key = ctx.session.state.get("scenario_key", "heavy_rain")
        result = score_zones(scenario_key)
        scores_json = json.dumps(result)

        # Persist for NarrativeAgent to read
        ctx.session.state["scores"] = scores_json

        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=scores_json)]),
        )


scorer_agent = ScorerAgent(
    name="ScorerAgent",
    description=(
        "Deterministically scores Tampa Bay zones for fragility under a flood "
        "scenario. Writes ranked zones to session state['scores']. No LLM used."
    ),
)
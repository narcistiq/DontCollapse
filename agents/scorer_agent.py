"""
ScorerAgent — computes fragility scores for each Tampa Bay zone
based on the selected flood scenario and static infrastructure data.
"""

import json
from pathlib import Path
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


# ── Load static data once at import time ──────────────────────────────────────

DATA_PATH = Path(__file__).parent.parent / "tampa_data.json"

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
        A dict with 'scenario_label' and a ranked list of 'scored_zones',
        each containing id, name, fragility_score (0–100), and
        the individual factor values used in the calculation.
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

        # Each factor is normalised to 0–1, then inverted so that
        # a higher value = more fragile (worse).

        # Elevation: how far below the flood threshold is this zone?
        elev_gap = max(0, threshold - zone["elevation_ft"])
        elev_score = min(elev_gap / threshold, 1.0)          # 0 = safe, 1 = very low

        # Drainage quality: rated 1 (poor) – 5 (excellent)
        drain_score = 1.0 - ((zone["drainage_quality"] - 1) / 4)  # invert

        # Alternate routes: 1 (trapped) – 5+ (many options)
        route_score = 1.0 - min((zone["alternate_routes"] - 1) / 4, 1.0)

        # Distance to nearest shelter (further = more vulnerable)
        shelter_score = min(zone["distance_to_shelter_mi"] / 6.0, 1.0)

        # Flood history (more events = more fragile)
        history_score = min(zone["flood_history_events"] / 8.0, 1.0)

        # Weighted composite
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
                "elevation_score": round(elev_score, 2),
                "drainage_quality": zone["drainage_quality"],
                "drainage_score": round(drain_score, 2),
                "alternate_routes": zone["alternate_routes"],
                "route_score": round(route_score, 2),
                "distance_to_shelter_mi": zone["distance_to_shelter_mi"],
                "shelter_score": round(shelter_score, 2),
                "flood_history_events": zone["flood_history_events"],
                "history_score": round(history_score, 2),
            },
            "infrastructure": zone["infrastructure"],
        })

    # Rank highest fragility first
    scored.sort(key=lambda z: z["fragility_score"], reverse=True)

    return {
        "scenario_key": scenario_key,
        "scenario_label": scenario["label"],
        "scored_zones": scored,
    }


# ── Wrap as an ADK FunctionTool ───────────────────────────────────────────────

score_zones_tool = FunctionTool(func=score_zones)


# ── Agent definition ──────────────────────────────────────────────────────────

scorer_agent = LlmAgent(
    name="ScorerAgent",
    model="gemini-2.0-flash",
    description=(
        "Scores Tampa Bay infrastructure zones for fragility under a given "
        "flood scenario. Returns a ranked list of zones with detailed factor "
        "breakdowns. Always call the score_zones tool and return its full output."
    ),
    instruction=(
        "You are a infrastructure fragility scoring engine. "
        "When given a scenario key, call the score_zones tool immediately "
        "and return the complete JSON result without modification. "
        "Do not add commentary — the NarrativeAgent will handle that."
    ),
    tools=[score_zones_tool],
    output_key="scores",   # stores result in session state under 'scores'
)